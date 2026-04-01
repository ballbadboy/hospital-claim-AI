# Hospital Claim AI — Full Platform + Agent Design

## Context

Hospital Claim AI is a prototype that will go to production in real Thai hospitals. The current system has a working core (rule engine, Claude AI analysis, CSV batch upload, appeal generation) but lacks persistence, integrations, UI, and agent capabilities.

Hospitals primarily use HOSxP and SSB as HIS systems, but the platform must support any HIS via a plugin architecture. The workflow is mixed: manual CSV upload by staff + automatic integration from HIS.

## Goals

1. **Production-ready data layer** with full audit trail
2. **Pluggable HIS connector** supporting HOSxP, SSB, CSV, and any future HIS
3. **Dashboard + Reports** for KPI visibility and Excel export
4. **LINE notifications + FDH submission** for real-time alerts and actual claim filing
5. **Claude Cowork Agent** — both specialist (invoked by others) and autonomous (self-monitoring)

## Approach

**Foundation First** — build infrastructure bottom-up so each phase unlocks the next.

---

## Cross-Cutting: Security, Compliance & Resilience

These concerns apply across all phases and must be addressed from Phase 1 onward.

### Authentication & Authorization

Since this system handles PHI (Protected Health Information) in real hospitals, auth is mandatory from Phase 1.

**Mechanism:** JWT-based auth with hospital LDAP/AD integration option.

**Roles:**
| Role | Permissions |
|------|------------|
| admin | Full access: config, users, all endpoints |
| coder | Check claims, upload CSV, draft appeals, view dashboard |
| department_head | View department KPIs, approve submissions |
| finance | View submissions, trigger FDH submit, view revenue reports |
| readonly | View dashboard and reports only |

**Implementation:**
- `api/auth/` module with JWT token issuance, validation middleware
- Per-endpoint role decorator: `@require_role("coder", "admin")`
- PHI access logged in audit trail (who viewed which patient record)
- **Access token expiry: 15 minutes** (short-lived for security)
- **Refresh token expiry: 8 hours** (hospital shift length), stored in Redis for revocation
- Phase 1 delivers local user/password auth; LDAP/AD integration added in Phase 3
- Application MUST refuse to start if `jwt_secret_key` is empty or shorter than 32 characters

**Rate limiting & brute-force protection:**
- Login endpoint: max 5 failed attempts per IP per 5 minutes → return 429
- Account lockout: 10 consecutive failed attempts → lock account for 30 minutes, LINE notify admin
- Rate limiting via `slowapi` (FastAPI-compatible, Redis-backed from Phase 2, in-memory for Phase 1)

**Token revocation:**
- Redis-based token blacklist (available from Phase 2; Phase 1 uses in-memory set as temporary measure)
- Admin API: `POST /api/v1/auth/revoke/{user_id}` — immediately invalidates all tokens for a user
- On password change or role change: auto-revoke all existing tokens
- Compromised credential response: admin can revoke instantly, no waiting for expiry

**New files:**
```
api/
  auth/
    __init__.py
    jwt_handler.py      # token creation, validation
    middleware.py        # FastAPI dependency for auth
    models.py           # User, Role models
    routes.py           # login, refresh, user management
```

### Data Protection & PDPA Compliance

Thai hospitals are subject to the PDPA (Personal Data Protection Act). Requirements:

- **Encryption in transit:** TLS required for all API endpoints; no plaintext HTTP
- **Data retention:** Claim records retained for 10 years (medical record law); configurable per hospital
- **Access logging:** Every read/write of patient data recorded in audit log with user identity
- **Consent:** Out of scope for this system (handled by hospital's HIS admission process)

**PII storage policy:**
- `HN` (Hospital Number) is a hospital-internal identifier, stored in cleartext for indexing and queryability. It is not considered externally-identifiable PII on its own.
- `patient_name` is NOT stored in the database. It is transient — passed through `ClaimInput` for display/AI analysis during the request, but never persisted to `ClaimRecord`. When patient name is needed later, it is fetched from the HIS on-demand via the HIS connector. This eliminates PII-at-rest risk.
- `AN` (Admission Number) is stored for tracking and FDH submission, treated same as HN.
- API responses never include patient_name unless the HIS connector is called to enrich the response.

**Database encryption:** PostgreSQL-level encryption is not required given the PII storage policy above (no PII at rest). If a hospital requires additional protection, PostgreSQL's `pgcrypto` extension can encrypt specific columns. This is a per-hospital deployment decision, not a code architecture decision.

### Error Handling & Resilience

**Circuit breaker pattern** for external services:

| Service | Failure threshold | Fallback |
|---------|------------------|----------|
| Claude API | 3 failures in 60s | Rule-engine-only mode (existing graceful degradation) |
| FDH API | 3 failures in 60s | Queue for retry, LINE notify admin |
| HIS (HOSxP/SSB) | 5 failures in 120s | Skip scan cycle, retry next schedule |
| LINE API | 3 failures in 60s | Log notification, deliver on recovery |

**Dead letter queue:** Failed Celery tasks moved to DLQ after 3 retries. Admin dashboard shows DLQ items for manual resolution.

**Health check aggregation:** `/api/v1/health` returns status of all dependencies (DB, Redis, HIS, FDH, Claude API, LINE).

**Database connection pooling:**
```python
# database.py engine configuration
create_async_engine(
    settings.database_url,
    pool_size=10,        # base connections
    max_overflow=20,     # burst capacity
    pool_timeout=30,     # wait for connection before error
    pool_recycle=1800,   # recycle connections every 30 min (avoid stale)
)
```
Celery workers use a separate engine instance with `pool_size=5` to avoid contention with the API server.

### Testing Strategy

| Phase | Test Type | Coverage Target |
|-------|-----------|----------------|
| 1 | Unit tests for repositories + integration tests for DB | Repositories: 90% |
| 2 | Unit tests per connector + integration tests with mock HIS | Connectors: 85% |
| 3 | API integration tests for dashboard/report endpoints | Endpoints: 80% |
| 4 | Integration tests for FDH client (mock API) + LINE (mock) | Submission flow: 85% |
| 5 | Agent behavior tests: decision rules, tool invocations | Decision rules: 95% |

**Test data:** Synthetic patient data generator (no real PHI in tests). Factory functions following the existing `make_claim()` pattern in `tests/test_rule_engine.py`.

**E2E testing (Phase 3):** Playwright for critical frontend flows — login, claim review, submission approval, report export. Run against a test backend with synthetic data.

**CI pipeline:** pytest → coverage check → lint → docker build on every push.

### Deployment

**Target:** On-premise Docker deployment within hospital network (PHI must not leave hospital network). Cloud option available for hospitals with cloud-approved infrastructure.

**Development:** `docker-compose.yml` with PostgreSQL, Redis, and the app.

**Production topology:**
```
Hospital Network
├── Docker Host
│   ├── hospital-claim-ai (FastAPI app)
│   ├── celery-worker (background tasks)
│   ├── celery-beat (scheduler)
│   ├── postgresql (data)
│   └── redis (cache + queue + pub/sub)
├── HIS Server (HOSxP/SSB) ← internal network
└── Outbound (via hospital firewall)
    ├── FDH API (NHSO)
    ├── Claude API (Anthropic)
    └── LINE API
```

**Database backup:** Daily automated pg_dump, retained 30 days, encrypted at rest.

**Monitoring:** Structured JSON logging (replace current plaintext format in `setup_logging()` with `python-json-logger`) + Prometheus metrics endpoint + Grafana dashboard (optional). LINE alerts for system-level failures.

**Rollback strategy:** Every Alembic migration must include a working `downgrade()` path. Deployment procedure: (1) backup DB, (2) deploy new version, (3) run health check, (4) if failed → `alembic downgrade -1` + redeploy previous Docker image. Docker images tagged with git SHA for traceability.

**Container resilience:** All containers run with `restart: unless-stopped` policy. Disk space monitoring with alert at 80% capacity (PostgreSQL can fill disks). Resource limits defined in docker-compose.

---

## Phase 1: Data Layer & Persistence

### What

Add database persistence, audit logging, and claim lifecycle tracking to all existing endpoints.

### New Files

```
core/
  repositories.py       # CRUD operations (ClaimRepo, AuditRepo)
api/
  dependencies.py       # get_db_session dependency injection
alembic/                # database migrations
  env.py
  versions/
    001_initial.py
```

### Modified Files

```
core/database.py        # add session factory dependency
api/routes.py           # all endpoints save to DB
api/main.py             # call init with alembic
```

### Design

**Repository pattern** separates DB logic from routes:

```python
class ClaimRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_check_result(self, claim: ClaimInput, result: ClaimCheckResponse) -> ClaimRecord: ...
    async def get_by_an(self, an: str) -> ClaimRecord | None: ...
    async def list_claims(self, filters: dict, page: int, size: int) -> list[ClaimRecord]: ...
    async def update_status(self, an: str, status: str) -> ClaimRecord: ...

class AuditRepository:
    async def log_action(self, an: str, action: str, details: dict, user: str = "system") -> AuditLog: ...
    async def get_audit_trail(self, an: str) -> list[AuditLog]: ...
```

**Claim lifecycle — two independent state machines:**

`fdh_status` tracks claim submission lifecycle (authoritative for submission state):
```
pending → checked → ready → submitted → approved
            │                  │
            ▼                  ▼
        re_checking          denied
            │
            ▼
         checked (loop back)

Any state → cancelled (manual withdrawal)
```

When `fdh_status` = `denied`, the `appeal_status` machine activates:

`appeal_status` tracks appeal lifecycle (authoritative for appeal state):
```
none → drafted → submitted → approved
                            → rejected → re_drafted → submitted (retry)
```

**Authority boundary:** `fdh_status` stays at `denied` throughout the appeal process. It does NOT have appeal sub-states. Only `appeal_status` tracks appeal progress. When `appeal_status` reaches `approved`, `fdh_status` transitions to `approved`. When `appeal_status` reaches `rejected` (final, after exhausting retries), `fdh_status` remains `denied`.

Both state machines are defined as Python Enums:

```python
class FDHStatus(str, Enum):
    PENDING = "pending"
    CHECKED = "checked"
    READY = "ready"
    RE_CHECKING = "re_checking"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"

class AppealStatus(str, Enum):
    NONE = "none"
    DRAFTED = "drafted"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    RE_DRAFTED = "re_drafted"
```

Transitions enforced in `ClaimRepository.update_status()` with a state machine validator. Invalid transitions raise `InvalidStateTransition` error.

**Migration strategy:**
- Remove existing `init_db()` / `create_all()` from `database.py`
- Initialize Alembic with `alembic init alembic`
- Generate initial migration from existing ORM models: `alembic revision --autogenerate -m "initial"`
- For environments with existing prototype schema: provide a `scripts/migrate_from_prototype.py` that stamps the current DB as the initial revision
- All future schema changes via `alembic revision --autogenerate`

**Key decisions:**
- Alembic for migrations (replaces `create_all()`)
- Every check/submit/appeal writes an audit log entry
- FastAPI dependency injection for DB sessions with automatic rollback on error
- ORM models remain in `core/database.py` for now; extract to `core/orm_models.py` if model count exceeds 6

---

## Phase 2: HIS Connector Plugin System

### What

A plugin architecture that normalizes data from any HIS into `ClaimInput`, so the core engine never knows where data came from.

### New Files

```
modules/
  his_connector/
    __init__.py
    base.py             # BaseHISConnector (abstract class)
    registry.py         # ConnectorRegistry: register + select connector
    hosxp.py            # HOSxPConnector (MySQL/API)
    ssb.py              # SSBConnector (API/DB)
    csv_connector.py    # CSVConnector (wraps existing CSV logic)
```

### Design

**Abstract base:**

```python
class BaseHISConnector(ABC):
    @abstractmethod
    async def fetch_discharges(self, since: datetime) -> list[ClaimInput]:
        """Fetch new discharges since given time."""

    @abstractmethod
    async def fetch_claim(self, hn: str, an: str) -> ClaimInput:
        """Fetch single claim by HN/AN."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check HIS connectivity."""

    def normalize(self, raw_data: dict) -> ClaimInput:
        """Transform HIS-specific format to standard ClaimInput."""
```

**Registry pattern:**

```python
class ConnectorRegistry:
    _connectors: dict[str, type[BaseHISConnector]] = {}

    @classmethod
    def register(cls, name: str, connector_class: type[BaseHISConnector]): ...

    @classmethod
    def get(cls, name: str) -> BaseHISConnector: ...

# Usage
ConnectorRegistry.register("hosxp", HOSxPConnector)
ConnectorRegistry.register("ssb", SSBConnector)
ConnectorRegistry.register("csv", CSVConnector)

connector = ConnectorRegistry.get(settings.his_type)
```

**Connector instantiation and configuration:**

Each connector receives its config from `Settings`. Multiple connectors can be active simultaneously (e.g., HOSxP for real-time + CSV for manual override):

```python
# config.py additions
his_connectors: list[str] = ["hosxp"]  # active connectors, e.g. ["hosxp", "csv"]
hosxp_db_host: str = ""
hosxp_db_port: int = 3306
hosxp_db_name: str = "hosxp_pcu"
hosxp_db_user: str = ""
hosxp_db_password: str = ""
ssb_api_url: str = ""
ssb_api_key: str = ""
```

```python
# Registry instantiates connectors with settings
class ConnectorRegistry:
    @classmethod
    def get(cls, name: str) -> BaseHISConnector:
        connector_class = cls._connectors[name]
        settings = get_settings()
        return connector_class(settings)  # connector reads its own fields from settings

    @classmethod
    def get_all_active(cls) -> list[BaseHISConnector]:
        """Return all configured active connectors."""
        settings = get_settings()
        return [cls.get(name) for name in settings.his_connectors]
```

Connectors are created per-use (not singletons) to avoid stale DB connections.

**Key decisions:**
- Adding a new HIS = one new file implementing `BaseHISConnector` + one `register()` call
- Multiple connectors can be active simultaneously (`his_connectors` is a list)
- Each connector reads its own settings from the shared `Settings` object
- `normalize()` maps HIS-specific field names to `ClaimInput` fields
- Health check exposed on dashboard for connection monitoring
- CSV connector is always available as a fallback regardless of `his_connectors` config
- **HOSxP connector MUST use a read-only database account** with SELECT-only privileges on specific tables. Writing to HOSxP could corrupt hospital operations. The connector configuration should document which HOSxP tables are accessed.

---

## Phase 3: Dashboard + Reports

### What

React frontend for KPI visibility, claim management, and Excel report generation.

### New Files

```
dashboard/
  src/
    components/
      KPICards.tsx
      DenyReasonChart.tsx
      DepartmentTable.tsx
      ClaimTimeline.tsx
      BatchUploader.tsx
      ClaimDetail.tsx
    pages/
      Dashboard.tsx         # KPI overview
      Claims.tsx            # claim list + filter/search
      ClaimView.tsx         # single claim detail + actions
      Reports.tsx           # monthly reports + export

api/
  routes_dashboard.py       # stats endpoints querying DB
  routes_reports.py         # report generation + Excel export

core/
  report_engine.py          # monthly summaries, deny stats, revenue
```

### Dashboard Layout

Main page shows:
- **KPI cards**: total claims, deny rate (with trend), revenue at risk, recovery rate
- **Deny reason chart**: pie/bar chart of top denial causes
- **Department table**: KPI per department with comparison to previous month
- **Recent claims**: sortable table with status indicators and scores
- **CSV upload**: drag-and-drop batch upload

### Reports

| Report | Content | Audience |
|--------|---------|----------|
| Monthly Summary | deny rate trend, revenue, top deny reasons | Management |
| Department Detail | KPI per department, month-over-month | Department heads |
| Claim Audit Trail | all actions per claim | Compliance |
| Denial Analysis | deny causes + fixes + appeal success rate | Coding team |

### Key Decisions

- **Vite + React + TailwindCSS + Recharts** — lightweight, deploy as static files behind FastAPI or Nginx
- **React Query (TanStack Query)** for server state management — handles caching, refetching, pagination
- **API-first** — dashboard calls same `/api/v1/` endpoints; all new routes also under `/api/v1/`
- **Excel export via openpyxl** — already in requirements
- **Pagination + filters** on claim list for performance with large datasets
- **Thai language UI** with English medical terms (consistent with API response language)
- **Responsive design** — hospital staff use both desktop and tablets on ward rounds

---

## Phase 4: LINE Notification + FDH Submission

### What

Real-time LINE alerts for claim issues and direct FDH submission from the system.

### New Files

```
modules/
  notifications/
    __init__.py
    base.py              # BaseNotifier (abstract)
    line_notifier.py     # LINE OA integration
    templates.py         # Thai message templates

  fdh_client/
    __init__.py
    client.py            # FDH API client (submit, status, retry)
    models.py            # FDH request/response models
    file_builder.py      # Build 16-file format from ClaimInput

core/
  submission_engine.py   # orchestrate: validate -> submit -> track -> notify
```

### LINE Notification Events

| Event | Recipients | Priority |
|-------|-----------|----------|
| Critical issue found | Coding staff | Immediate |
| Submission success | Finance | Normal |
| Approaching 30-day deadline | Department head | Urgent |
| Denial received | Coding staff | Immediate |
| Appeal result summary | Management | Daily digest |

LINE messages include action buttons linking to Dashboard for quick response.

### FDH Submission Flow

```
ClaimInput → Validate (score >= 80, 0 critical)
           → Build 16-File format
           → Submit to FDH API
           → Success: update status + notify
           → Failure: retry queue (3 attempts with backoff) + notify
```

### Key Decisions

- **Notifier is pluggable** like HIS — `BaseNotifier` supports LINE, Email, SMS
- **FDH retry with exponential backoff** — 3 attempts before alerting human
- **Submission threshold**: score >= 80 AND 0 critical issues
- **16-File builder** auto-generates FDH format from ClaimInput
- **LINE Rich Menu** links to Dashboard pages

---

## Phase 5: Claude Cowork Agent

### What

Hospital Claim AI as a Claude agent — both invokable by other agents (specialist) and self-running (autonomous).

### New Files

```
agent/
  __init__.py
  claim_agent.py         # agent definition (tools + instructions)
  tools/
    __init__.py
    check_claim.py       # tool: validate single claim
    check_batch.py       # tool: validate multiple claims
    appeal.py            # tool: draft appeal letter
    lookup.py            # tool: search claims/status
    submit.py            # tool: submit to FDH
    dashboard.py         # tool: get KPI stats
    his_fetch.py         # tool: fetch data from HIS

  autonomous/
    __init__.py
    scheduler.py         # cron-based periodic scan
    event_listener.py    # webhook receiver from HIS
    monitor.py           # orchestrate: scan -> check -> notify -> submit
    rules.py             # decision rules for autonomous actions
```

### Mode A: Specialist Agent

Other Claude agents or users invoke tools directly:

```python
claim_agent = Agent(
    name="Hospital Claim AI",
    model=settings.anthropic_model,  # configurable, not hardcoded
    instructions="...",  # Thai hospital claim expert
    tools=[
        check_claim_tool,
        check_batch_tool,
        generate_appeal_tool,
        lookup_claim_tool,
        submit_to_fdh_tool,
        get_dashboard_stats_tool,
        fetch_from_his_tool,
    ],
)
```

Available operations:
- "check this claim" → validates and returns score + issues + recommendations
- "draft an appeal for AN2026001" → generates appeal letter with clinical reasoning
- "what's the deny rate this month?" → returns KPI summary
- "fetch new discharges from HIS" → pulls and validates new cases

### Mode B: Autonomous Agent

Self-monitoring with scheduled scans and event-driven triggers:

**Triggers:**
- **Scheduled**: scan HIS every 2 hours for new discharges
- **Event-driven**: HIS sends webhook on new discharge → agent processes immediately

**Decision rules:**

| Condition | Action | Human confirmation? |
|-----------|--------|-------------------|
| Score >= 80, 0 critical | Auto-submit to FDH | No — submit + notify success |
| Score 60-79, 0 critical | LINE notify + suggest fixes | Yes — wait for human |
| Has critical issues | LINE notify + block submission | Yes — must fix first |
| 3 days before 30-day deadline | Urgent LINE alert | No — alert immediately |
| Denial received | Auto-draft appeal + LINE notify | Yes — human reviews draft |

### Key Decisions

- **Claude Agent SDK** (`claude-agent-sdk` — verify exact package name before implementation) for Cowork compatibility
- **Tools wrap existing core** — no logic duplication
- **Safety rails**: agent never submits claims with critical issues
- **Actions affecting money (submit, appeal) have clear thresholds**
- **Redis pub/sub** for realtime HIS events
- **APScheduler or Celery Beat** for periodic scans
- **Kill switch**: `autonomous_enabled` setting toggleable via admin API (`PUT /api/v1/admin/autonomous`) without redeployment. When disabled, all scheduled scans and auto-submissions halt immediately. LINE notifies admin when toggled. Default: `False` (must be explicitly enabled per hospital)

---

### Key Decisions (continued)

- Autonomous batch limit: same 500-claim cap as API; if HIS returns more, split into multiple batches via Celery tasks
- Agent model uses `settings.anthropic_model` (configurable, not hardcoded)

---

## Tech Stack Summary

| Component | Technology | Introduced in Phase |
|-----------|-----------|-------------------|
| Backend | Python 3.12, FastAPI | Existing |
| Auth | JWT + role-based middleware | Phase 1 |
| Database | PostgreSQL | Phase 1 |
| Migrations | Alembic | Phase 1 |
| Cache + Queue | Redis | Phase 2 (HIS scheduling) |
| Task Queue | Celery + Redis | Phase 2 |
| Frontend | React, TailwindCSS, Recharts | Phase 3 |
| AI | Claude API (Anthropic SDK) | Existing |
| Notifications | LINE Messaging API, line-bot-sdk | Phase 4 |
| Agent | Claude Agent SDK | Phase 5 |
| Export | openpyxl (Excel), pandas | Phase 3 |
| Container | Docker (non-root), docker-compose | Phase 1 |
| HIS Integration | Plugin system (HOSxP MySQL, SSB API, CSV) | Phase 2 |

**New requirements.txt additions by phase:**
- Phase 1: `alembic`, `pyjwt`, `passlib[bcrypt]`
- Phase 2: `redis`, `celery[redis]`, `aiomysql` (HOSxP), `apscheduler`
- Phase 3: (frontend — separate package.json)
- Phase 4: (LINE SDK already present)
- Phase 5: `claude-agent-sdk`

**Settings additions:**
```python
# Phase 1
jwt_secret_key: str = ""
jwt_algorithm: str = "HS256"
jwt_expiry_hours: int = 8

# Phase 2
redis_url: str = "redis://localhost:6379/0"
his_connectors: list[str] = ["csv"]
hosxp_db_host: str = ""
hosxp_db_port: int = 3306
hosxp_db_name: str = ""
hosxp_db_user: str = ""
hosxp_db_password: str = ""
ssb_api_url: str = ""
ssb_api_key: str = ""

# Phase 5
autonomous_scan_interval_hours: int = 2
auto_submit_score_threshold: int = 80
```

## Dependency Graph

```
Phase 1 (Data Layer)
    ├── Phase 2 (HIS Connectors) — needs DB to store fetched claims
    │       └── Phase 5 (Agent) — needs HIS connectors for autonomous fetch
    ├── Phase 3 (Dashboard) — needs DB to query stats
    │       └── Phase 3b (Reports) — needs dashboard stats
    └── Phase 4 (LINE + FDH) — needs DB for status tracking
            └── Phase 5 (Agent) — needs LINE + FDH for autonomous actions
```

Phase 1 is the critical path. Phases 2, 3, 4 can partially parallelize after Phase 1 is complete. Phase 5 depends on all prior phases.
