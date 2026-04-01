# Phase 1: Data Layer & Authentication — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add database persistence, audit logging, claim lifecycle tracking, and JWT authentication to the Hospital Claim AI system.

**Architecture:** Repository pattern for DB operations, FastAPI dependency injection for sessions, JWT auth with role-based access control, Alembic for migrations. All existing endpoints updated to persist results and require authentication.

**Tech Stack:** PostgreSQL, Alembic, PyJWT, passlib[bcrypt], slowapi, python-json-logger

**Spec:** `docs/superpowers/specs/2026-03-25-full-platform-agent-design.md`

**Note:** This is Phase 1 of 5. Phases 2-5 will have separate plan documents.

---

### Task 1: Update requirements and structured logging

**Files:**
- Modify: `requirements.txt`
- Modify: `core/config.py`

- [ ] **Step 1: Add Phase 1 dependencies to requirements.txt**

```
# Add to requirements.txt (alembic is already present):
pyjwt==2.10.1
passlib[bcrypt]==1.7.4
slowapi==0.1.9
python-json-logger==3.2.1
```

- [ ] **Step 2: Update setup_logging() to use JSON format**

In `core/config.py`, replace the existing `setup_logging()` function:

```python
def setup_logging() -> None:
    settings = get_settings()
    from pythonjsonlogger import jsonlogger

    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

- [ ] **Step 3: Add auth settings to Settings class**

In `core/config.py`, add these fields to `Settings`:

```python
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 15
    jwt_refresh_token_hours: int = 8
```

- [ ] **Step 4: Create pytest config for asyncio mode**

Create `pyproject.toml` (or add to existing):

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 5: Install new dependencies and verify**

Run: `cd hospital-claim-ai-app && pip install -r requirements.txt`
Expected: All packages install successfully.

- [ ] **Step 6: Run existing tests to confirm nothing broke**

Run: `python3 -m pytest tests/ -v`
Expected: All 13 tests pass.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt core/config.py
git commit -m "feat(phase1): add dependencies and structured JSON logging"
```

---

### Task 2: State machine enums and ORM model updates

**Files:**
- Modify: `core/models.py` — add FDHStatus, AppealStatus enums
- Modify: `core/database.py` — update ClaimRecord columns, add connection pooling, add User model

- [ ] **Step 1: Write tests for state machine enums**

Create `tests/test_models.py`:

```python
import pytest
from core.models import FDHStatus, AppealStatus


class TestFDHStatus:
    def test_all_statuses_exist(self):
        expected = {"pending", "checked", "ready", "re_checking",
                    "submitted", "approved", "denied", "cancelled"}
        assert {s.value for s in FDHStatus} == expected

    def test_string_enum(self):
        assert FDHStatus.PENDING == "pending"
        assert isinstance(FDHStatus.PENDING, str)


class TestAppealStatus:
    def test_all_statuses_exist(self):
        expected = {"none", "drafted", "submitted",
                    "approved", "rejected", "re_drafted"}
        assert {s.value for s in AppealStatus} == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_models.py -v`
Expected: FAIL — `FDHStatus` not found.

- [ ] **Step 3: Add FDHStatus and AppealStatus enums to models.py**

Add after `class Severity` in `core/models.py`:

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

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Update ClaimRecord ORM to use new enums and add connection pooling**

In `core/database.py`:

Update `get_engine()`:
```python
def get_engine():
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.app_env == "development",
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
    )
```

Update `ClaimRecord` columns — change `fdh_status` and `appeal_status` defaults:
```python
    fdh_status = Column(String, default=FDHStatus.PENDING)
    appeal_status = Column(String, default=AppealStatus.NONE)
```

Add `User` model:
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="readonly")
    is_active = Column(Boolean, default=True)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
```

Import enums at top of `database.py`:
```python
from core.models import FDHStatus, AppealStatus
```

- [ ] **Step 6: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass (existing + new).

- [ ] **Step 7: Commit**

```bash
git add core/models.py core/database.py tests/test_models.py
git commit -m "feat(phase1): add state machine enums, User model, connection pooling"
```

---

### Task 3: Alembic setup and initial migration

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/script.py.mako`
- Create: `alembic/versions/` (auto-generated)
- Modify: `core/database.py` — remove `init_db()`

- [ ] **Step 1: Initialize Alembic**

Run: `cd hospital-claim-ai-app && alembic init alembic`
Expected: Creates `alembic/` directory and `alembic.ini`.

- [ ] **Step 2: Configure alembic/env.py for async**

Replace `alembic/env.py` content with:

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from core.config import get_settings
from core.database import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: Remove init_db() from database.py**

Remove the `init_db()` function from `core/database.py` entirely.

- [ ] **Step 4: Generate initial migration**

Run: `alembic revision --autogenerate -m "initial schema"`
Expected: Creates a migration file in `alembic/versions/`.

- [ ] **Step 5: Commit**

```bash
git add alembic/ alembic.ini core/database.py
git commit -m "feat(phase1): setup Alembic migrations, remove create_all"
```

---

### Task 4: State machine transition validator

**Files:**
- Create: `core/state_machine.py`
- Create: `tests/test_state_machine.py`

- [ ] **Step 1: Write failing tests for state transitions**

Create `tests/test_state_machine.py`:

```python
import pytest
from core.models import FDHStatus, AppealStatus


class TestFDHTransitions:
    def test_pending_to_checked(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.PENDING, FDHStatus.CHECKED)  # should not raise

    def test_checked_to_ready(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.CHECKED, FDHStatus.READY)

    def test_checked_to_re_checking(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.CHECKED, FDHStatus.RE_CHECKING)

    def test_submitted_to_denied(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.SUBMITTED, FDHStatus.DENIED)

    def test_invalid_pending_to_approved(self):
        from core.state_machine import validate_fdh_transition, InvalidStateTransition
        with pytest.raises(InvalidStateTransition):
            validate_fdh_transition(FDHStatus.PENDING, FDHStatus.APPROVED)

    def test_invalid_denied_to_ready(self):
        from core.state_machine import validate_fdh_transition, InvalidStateTransition
        with pytest.raises(InvalidStateTransition):
            validate_fdh_transition(FDHStatus.DENIED, FDHStatus.READY)

    def test_any_to_cancelled(self):
        from core.state_machine import validate_fdh_transition
        for status in FDHStatus:
            if status != FDHStatus.CANCELLED:
                validate_fdh_transition(status, FDHStatus.CANCELLED)

    def test_appeal_approved_transitions_fdh_to_approved(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.DENIED, FDHStatus.APPROVED)  # via appeal


class TestAppealTransitions:
    def test_none_to_drafted(self):
        from core.state_machine import validate_appeal_transition
        validate_appeal_transition(AppealStatus.NONE, AppealStatus.DRAFTED)

    def test_drafted_to_submitted(self):
        from core.state_machine import validate_appeal_transition
        validate_appeal_transition(AppealStatus.DRAFTED, AppealStatus.SUBMITTED)

    def test_rejected_to_re_drafted(self):
        from core.state_machine import validate_appeal_transition
        validate_appeal_transition(AppealStatus.REJECTED, AppealStatus.RE_DRAFTED)

    def test_invalid_none_to_approved(self):
        from core.state_machine import validate_appeal_transition, InvalidStateTransition
        with pytest.raises(InvalidStateTransition):
            validate_appeal_transition(AppealStatus.NONE, AppealStatus.APPROVED)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_state_machine.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement state machine validator**

Create `core/state_machine.py`:

```python
"""State machine transition validators for claim lifecycle."""

from core.models import FDHStatus, AppealStatus


class InvalidStateTransition(Exception):
    def __init__(self, current: str, target: str):
        super().__init__(f"Invalid transition: {current} → {target}")
        self.current = current
        self.target = target


# Valid transitions for fdh_status
_FDH_TRANSITIONS: dict[FDHStatus, set[FDHStatus]] = {
    FDHStatus.PENDING: {FDHStatus.CHECKED, FDHStatus.CANCELLED},
    FDHStatus.CHECKED: {FDHStatus.READY, FDHStatus.RE_CHECKING, FDHStatus.CANCELLED},
    FDHStatus.READY: {FDHStatus.SUBMITTED, FDHStatus.RE_CHECKING, FDHStatus.CANCELLED},
    FDHStatus.RE_CHECKING: {FDHStatus.CHECKED, FDHStatus.CANCELLED},
    FDHStatus.SUBMITTED: {FDHStatus.APPROVED, FDHStatus.DENIED, FDHStatus.CANCELLED},
    FDHStatus.APPROVED: set(),
    FDHStatus.DENIED: {FDHStatus.APPROVED, FDHStatus.CANCELLED},  # approved via appeal
    FDHStatus.CANCELLED: set(),
}

# Valid transitions for appeal_status
_APPEAL_TRANSITIONS: dict[AppealStatus, set[AppealStatus]] = {
    AppealStatus.NONE: {AppealStatus.DRAFTED},
    AppealStatus.DRAFTED: {AppealStatus.SUBMITTED},
    AppealStatus.SUBMITTED: {AppealStatus.APPROVED, AppealStatus.REJECTED},
    AppealStatus.APPROVED: set(),
    AppealStatus.REJECTED: {AppealStatus.RE_DRAFTED},
    AppealStatus.RE_DRAFTED: {AppealStatus.SUBMITTED},
}


def validate_fdh_transition(current: FDHStatus, target: FDHStatus) -> None:
    """Raise InvalidStateTransition if the transition is not allowed."""
    allowed = _FDH_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransition(current.value, target.value)


def validate_appeal_transition(current: AppealStatus, target: AppealStatus) -> None:
    """Raise InvalidStateTransition if the transition is not allowed."""
    allowed = _APPEAL_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransition(current.value, target.value)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_state_machine.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add core/state_machine.py tests/test_state_machine.py
git commit -m "feat(phase1): add state machine transition validators"
```

---

### Task 5: Repository pattern

**Files:**
- Create: `core/repositories.py`
- Create: `tests/test_repositories.py`

- [ ] **Step 1: Write failing tests for ClaimRepository**

Create `tests/test_repositories.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from core.models import (
    ClaimInput, ClaimCheckResponse, CheckResult, Severity,
    Department, Fund, FDHStatus, AppealStatus
)
from core.repositories import ClaimRepository, AuditRepository


def make_test_claim():
    return ClaimInput(
        hn="TEST001",
        an="AN001",
        principal_dx="I21.1",
        procedures=["37.22"],
        fund=Fund.UC,
    )


def make_test_response():
    return ClaimCheckResponse(
        hn="TEST001",
        an="AN001",
        department=Department.CATH_LAB,
        fund=Fund.UC,
        principal_dx="I21.1",
        procedures=["37.22"],
        results=[],
        score=85,
        ready_to_submit=True,
        critical_count=0,
        warning_count=0,
        passed_count=3,
        optimization_count=1,
    )


class TestClaimRepository:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.execute = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, mock_session):
        return ClaimRepository(mock_session)

    @pytest.mark.asyncio
    async def test_save_check_result_creates_record(self, repo, mock_session):
        claim = make_test_claim()
        response = make_test_response()
        record = await repo.save_check_result(claim, response)
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_check_result_sets_fdh_status_checked(self, repo, mock_session):
        claim = make_test_claim()
        response = make_test_response()
        record = await repo.save_check_result(claim, response)
        assert record.fdh_status == FDHStatus.CHECKED


class TestAuditRepository:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, mock_session):
        return AuditRepository(mock_session)

    @pytest.mark.asyncio
    async def test_log_action_creates_entry(self, repo, mock_session):
        await repo.log_action(an="AN001", action="check", details={"score": 85})
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_repositories.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement repositories**

Create `core/repositories.py`:

```python
"""Repository pattern — separates DB operations from route logic."""

import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import ClaimRecord, AuditLog, User
from core.models import (
    ClaimInput, ClaimCheckResponse, FDHStatus, AppealStatus
)
from core.state_machine import validate_fdh_transition, validate_appeal_transition

logger = logging.getLogger(__name__)


class ClaimRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_check_result(
        self, claim: ClaimInput, result: ClaimCheckResponse
    ) -> ClaimRecord:
        record = ClaimRecord(
            hn=claim.hn,
            an=claim.an,
            department=result.department.value,
            fund=claim.fund.value,
            principal_dx=claim.principal_dx,
            secondary_dx=claim.secondary_dx,
            procedures=claim.procedures,
            admit_date=claim.admit_date,
            discharge_date=claim.discharge_date,
            submit_date=claim.submit_date,
            check_score=result.score,
            check_results=[r.model_dump() for r in result.results],
            ready_to_submit=result.ready_to_submit,
            expected_drg=result.expected_drg,
            estimated_rw=result.estimated_rw,
            claim_amount=result.estimated_claim,
            ai_analysis=result.ai_analysis,
            # PENDING is for claims fetched from HIS but not yet checked (Phase 2).
            # save_check_result creates already-checked claims, so we skip PENDING.
            fdh_status=FDHStatus.CHECKED,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_an(self, an: str) -> ClaimRecord | None:
        result = await self.session.execute(
            select(ClaimRecord).where(ClaimRecord.an == an)
        )
        return result.scalar_one_or_none()

    async def list_claims(
        self,
        page: int = 1,
        size: int = 50,
        department: str | None = None,
        fdh_status: str | None = None,
    ) -> list[ClaimRecord]:
        query = select(ClaimRecord).order_by(ClaimRecord.created_at.desc())
        if department:
            query = query.where(ClaimRecord.department == department)
        if fdh_status:
            query = query.where(ClaimRecord.fdh_status == fdh_status)
        query = query.offset((page - 1) * size).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_fdh_status(self, an: str, new_status: FDHStatus) -> ClaimRecord:
        record = await self.get_by_an(an)
        if record is None:
            raise ValueError(f"Claim {an} not found")
        validate_fdh_transition(FDHStatus(record.fdh_status), new_status)
        record.fdh_status = new_status.value
        record.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return record

    async def update_appeal_status(self, an: str, new_status: AppealStatus) -> ClaimRecord:
        record = await self.get_by_an(an)
        if record is None:
            raise ValueError(f"Claim {an} not found")
        current = AppealStatus(record.appeal_status or AppealStatus.NONE)
        validate_appeal_transition(current, new_status)
        record.appeal_status = new_status.value
        record.updated_at = datetime.now(timezone.utc)
        if new_status == AppealStatus.APPROVED:
            validate_fdh_transition(FDHStatus(record.fdh_status), FDHStatus.APPROVED)
            record.fdh_status = FDHStatus.APPROVED.value
        await self.session.flush()
        return record


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(
        self,
        an: str,
        action: str,
        details: dict,
        user: str = "system",
    ) -> AuditLog:
        entry = AuditLog(an=an, action=action, details=details, user=user)
        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

    async def get_audit_trail(self, an: str) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.an == an)
            .order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self, username: str, hashed_password: str, role: str = "readonly"
    ) -> User:
        user = User(
            username=username,
            hashed_password=hashed_password,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def increment_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 10:
            from datetime import timedelta
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        await self.session.flush()

    async def reset_failed_login(self, user: User) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.flush()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_repositories.py -v`
Expected: All PASS.

- [ ] **Step 5: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add core/repositories.py tests/test_repositories.py
git commit -m "feat(phase1): add ClaimRepository, AuditRepository, UserRepository"
```

---

### Task 6: FastAPI DB session dependency

**Files:**
- Create: `api/dependencies.py`

- [ ] **Step 1: Create DB session dependency**

Create `api/dependencies.py`:

```python
"""FastAPI dependencies for DB sessions and auth."""

import logging
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session_factory
from core.repositories import ClaimRepository, AuditRepository, UserRepository

logger = logging.getLogger(__name__)

_session_factory = None


def _get_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = get_session_factory()
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = _get_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_claim_repo(
    session: AsyncSession = Depends(get_db_session),
) -> ClaimRepository:
    """Use as: claim_repo: ClaimRepository = Depends(get_claim_repo)"""
    return ClaimRepository(session)


async def get_audit_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AuditRepository:
    """Use as: audit_repo: AuditRepository = Depends(get_audit_repo)"""
    return AuditRepository(session)
```

- [ ] **Step 2: Run all tests to confirm no regressions**

Run: `python3 -m pytest tests/ -v`
Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add api/dependencies.py
git commit -m "feat(phase1): add FastAPI DB session dependencies"
```

---

### Task 7: JWT authentication module

**Files:**
- Create: `api/auth/__init__.py`
- Create: `api/auth/jwt_handler.py`
- Create: `api/auth/middleware.py`
- Create: `api/auth/models.py`
- Create: `api/auth/routes.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Write failing tests for JWT handler**

Create `tests/test_auth.py`:

```python
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


class TestJWTHandler:
    def test_create_access_token(self):
        from api.auth.jwt_handler import create_access_token
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32,
                jwt_algorithm="HS256",
                jwt_access_token_minutes=15,
            )
            token = create_access_token({"sub": "testuser", "role": "coder"})
            assert isinstance(token, str)
            assert len(token) > 0

    def test_decode_access_token(self):
        from api.auth.jwt_handler import create_access_token, decode_token
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32,
                jwt_algorithm="HS256",
                jwt_access_token_minutes=15,
            )
            token = create_access_token({"sub": "testuser", "role": "coder"})
            payload = decode_token(token)
            assert payload["sub"] == "testuser"
            assert payload["role"] == "coder"

    def test_decode_invalid_token_raises(self):
        from api.auth.jwt_handler import decode_token, InvalidToken
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32,
                jwt_algorithm="HS256",
            )
            with pytest.raises(InvalidToken):
                decode_token("invalid.token.here")

    def test_password_hashing(self):
        from api.auth.jwt_handler import hash_password, verify_password
        hashed = hash_password("testpass123")
        assert verify_password("testpass123", hashed) is True
        assert verify_password("wrongpass", hashed) is False

    def test_refuse_empty_secret(self):
        from api.auth.jwt_handler import create_access_token, InvalidToken
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="",
                jwt_algorithm="HS256",
                jwt_access_token_minutes=15,
            )
            with pytest.raises(InvalidToken, match="secret_key"):
                create_access_token({"sub": "test"})

    def test_refuse_short_secret(self):
        from api.auth.jwt_handler import create_access_token, InvalidToken
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="short",
                jwt_algorithm="HS256",
                jwt_access_token_minutes=15,
            )
            with pytest.raises(InvalidToken, match="secret_key"):
                create_access_token({"sub": "test"})


class TestAuthMiddleware:
    def _make_token(self, data: dict, token_type: str = "access"):
        from api.auth.jwt_handler import create_access_token, create_refresh_token
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32,
                jwt_algorithm="HS256",
                jwt_access_token_minutes=15,
                jwt_refresh_token_hours=8,
            )
            if token_type == "access":
                return create_access_token(data)
            return create_refresh_token(data)

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        from api.auth.middleware import get_current_user
        from unittest.mock import AsyncMock
        token = self._make_token({"sub": "testuser", "role": "coder"})
        creds = MagicMock()
        creds.credentials = token
        with patch("api.auth.middleware.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "testuser", "role": "coder", "type": "access"}
            user = await get_current_user(creds)
            assert user["sub"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_revoked_token(self):
        from api.auth.middleware import get_current_user, revoke_token
        from fastapi import HTTPException
        token = self._make_token({"sub": "testuser", "role": "coder"})
        revoke_token(token)
        creds = MagicMock()
        creds.credentials = token
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(creds)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_refresh_token_rejected(self):
        from api.auth.middleware import get_current_user
        from fastapi import HTTPException
        creds = MagicMock()
        creds.credentials = "some_token"
        with patch("api.auth.middleware.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "test", "role": "coder", "type": "refresh"}
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(creds)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_role_insufficient(self):
        from api.auth.middleware import require_role
        from fastapi import HTTPException
        checker = require_role("admin")
        with pytest.raises(HTTPException) as exc_info:
            await checker({"sub": "test", "role": "coder"})
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_role_sufficient(self):
        from api.auth.middleware import require_role
        checker = require_role("coder", "admin")
        user = await checker({"sub": "test", "role": "coder"})
        assert user["role"] == "coder"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_auth.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement JWT handler**

Create `api/auth/__init__.py` (empty file).

Create `api/auth/jwt_handler.py`:

```python
"""JWT token creation, validation, and password hashing."""

import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidToken(Exception):
    pass


def _get_secret() -> str:
    settings = get_settings()
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
        raise InvalidToken("jwt_secret_key must be at least 32 characters")
    return settings.jwt_secret_key


def create_access_token(data: dict) -> str:
    settings = get_settings()
    secret = _get_secret()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_minutes)
    payload = {**data, "exp": expire, "type": "access"}
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    settings = get_settings()
    secret = _get_secret()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_refresh_token_hours)
    payload = {**data, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    settings = get_settings()
    secret = _get_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidToken("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidToken("Invalid token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_auth.py -v`
Expected: All PASS.

- [ ] **Step 5: Implement auth middleware**

Create `api/auth/middleware.py`:

```python
"""FastAPI auth dependencies — require_role, get_current_user."""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.auth.jwt_handler import decode_token, InvalidToken

logger = logging.getLogger(__name__)
security = HTTPBearer()

# In-memory revocation (replaced by Redis in Phase 2)
_revoked_tokens: set[str] = set()
_revoked_user_ids: set[int] = set()


def revoke_token(token: str) -> None:
    _revoked_tokens.add(token)


def revoke_all_for_user(user_id: int) -> None:
    _revoked_user_ids.add(user_id)


def is_token_revoked(token: str) -> bool:
    return token in _revoked_tokens


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    if is_token_revoked(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")
    try:
        payload = decode_token(token)
    except InvalidToken as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    if payload.get("user_id") in _revoked_user_ids:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User tokens have been revoked")
    return payload


def require_role(*roles: str):
    """Dependency factory: require user to have one of the specified roles."""
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return _check
```

- [ ] **Step 6: Implement auth Pydantic models**

Create `api/auth/models.py`:

```python
"""Auth request/response models."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: str = Field(default="readonly")


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
```

- [ ] **Step 7: Implement auth routes**

Create `api/auth/routes.py`:

```python
"""Auth endpoints — login, refresh, user management."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.auth.models import (
    LoginRequest, TokenResponse, RefreshRequest,
    UserCreateRequest, UserResponse,
)
from api.auth.jwt_handler import (
    create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password, InvalidToken,
)
from api.auth.middleware import get_current_user, require_role, revoke_token, revoke_all_for_user
from api.dependencies import get_db_session
from core.repositories import UserRepository

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/login", response_model=TokenResponse)
@limiter.limit("5/5minutes")
async def login(request: Request, body: LoginRequest, session=Depends(get_db_session)):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(body.username)

    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_423_LOCKED, "Account locked. Try again later.")

    if not verify_password(body.password, user.hashed_password):
        await user_repo.increment_failed_login(user)
        await session.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    await user_repo.reset_failed_login(user)
    await session.commit()

    token_data = {"sub": user.username, "role": user.role, "user_id": user.id}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    try:
        payload = decode_token(body.refresh_token)
    except InvalidToken as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    token_data = {"sub": payload["sub"], "role": payload["role"], "user_id": payload["user_id"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@auth_router.post("/revoke/{user_id}")
async def revoke_user_tokens(
    user_id: int,
    admin: dict = Depends(require_role("admin")),
):
    # Phase 1: in-memory user-level revocation.
    # Phase 2 replaces with Redis-backed blacklist.
    revoke_all_for_user(user_id)
    logger.info("Token revocation requested for user_id=%d by %s", user_id, admin["sub"])
    return {"message": f"All tokens for user {user_id} revoked (in-memory, Phase 2 adds Redis persistence)"}


@auth_router.post("/users", response_model=UserResponse)
async def create_user(
    body: UserCreateRequest,
    admin: dict = Depends(require_role("admin")),
    session=Depends(get_db_session),
):
    user_repo = UserRepository(session)
    existing = await user_repo.get_by_username(body.username)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")

    valid_roles = {"admin", "coder", "department_head", "finance", "readonly"}
    if body.role not in valid_roles:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid role. Must be one of: {valid_roles}")

    user = await user_repo.create_user(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    await session.commit()
    return UserResponse(
        id=user.id, username=user.username, role=user.role, is_active=user.is_active
    )
```

- [ ] **Step 8: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 9: Commit**

```bash
git add api/auth/ tests/test_auth.py
git commit -m "feat(phase1): add JWT auth with rate limiting and token revocation"
```

---

### Task 8: Wire auth + persistence into existing routes and main app

**Files:**
- Modify: `api/main.py` — register auth router, add slowapi
- Modify: `api/routes.py` — add auth dependencies, persist to DB

- [ ] **Step 1: Update api/main.py**

Add imports and wire auth router + rate limiter:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.routes import router
from api.auth.routes import auth_router, limiter
from core.config import get_settings, setup_logging

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Refuse to start if JWT secret is missing or too short
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
        raise RuntimeError("jwt_secret_key must be at least 32 characters")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered claim validation for Thai hospitals. "
                "ลด Deny rate ทุกแผนก ทุกกองทุน",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 2: Update routes.py to add auth and DB persistence**

Add `Depends(get_current_user)` to all claim endpoints and save results to DB via repositories. Key changes:

At top of `api/routes.py`, add:
```python
from api.auth.middleware import get_current_user, require_role
from api.dependencies import get_db_session
from core.repositories import ClaimRepository, AuditRepository
```

Full updated route implementations (all share the same DB session for transactional consistency):

```python
@router.post("/check", response_model=ClaimCheckResponse)
async def check_single_claim(
    claim: ClaimInput,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """ตรวจสอบเคสเดี่ยว ก่อนส่งเบิก"""
    result = await check_claim(claim)
    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    await claim_repo.save_check_result(claim, result)
    await audit_repo.log_action(
        an=claim.an or "", action="check",
        details={"score": result.score, "critical": result.critical_count},
        user=user["sub"],
    )
    return result


@router.post("/check/batch", response_model=list[ClaimCheckResponse])
async def check_batch_claims(
    request: BatchCheckRequest,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """ตรวจสอบหลายเคสพร้อมกัน"""
    if len(request.claims) > 500:
        raise HTTPException(400, "Maximum 500 claims per batch")
    results = await check_batch(request.claims)
    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    for claim, result in zip(request.claims, results):
        await claim_repo.save_check_result(claim, result)
        await audit_repo.log_action(
            an=claim.an or "", action="check",
            details={"score": result.score, "critical": result.critical_count},
            user=user["sub"],
        )
    return results


@router.post("/check/csv")
async def check_csv_upload(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """Upload CSV จาก FDH Dashboard แล้วตรวจทุกเคส"""
    import io

    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "application/octet-stream"):
        raise HTTPException(400, "Only CSV files are accepted")

    content = await file.read()
    if len(content) > MAX_CSV_SIZE:
        raise HTTPException(413, f"File too large. Maximum {MAX_CSV_SIZE // 1024 // 1024} MB")

    df = pd.read_csv(io.BytesIO(content))

    if len(df) > 500:
        raise HTTPException(400, "Maximum 500 rows per CSV upload")

    claims = []
    for _, row in df.iterrows():
        sdx_raw = row.get("SDx")
        sdx = str(sdx_raw).split(",") if pd.notna(sdx_raw) and sdx_raw else []
        proc_raw = row.get("Procedures")
        procs = str(proc_raw).split(",") if pd.notna(proc_raw) and proc_raw else []

        claim = ClaimInput(
            hn=str(row.get("HN", "")),
            an=str(row.get("AN", "")),
            principal_dx=str(row.get("PDx", row.get("Primary Diagnosis", ""))),
            secondary_dx=sdx,
            procedures=procs,
        )
        claims.append(claim)

    results = await check_batch(claims)

    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    for claim, result in zip(claims, results):
        await claim_repo.save_check_result(claim, result)
        await audit_repo.log_action(
            an=claim.an or "", action="check_csv",
            details={"score": result.score, "critical": result.critical_count},
            user=user["sub"],
        )

    summary = {
        "total": len(results),
        "ready": sum(1 for r in results if r.ready_to_submit),
        "issues": sum(1 for r in results if not r.ready_to_submit),
        "critical_total": sum(r.critical_count for r in results),
        "results": results,
    }
    return summary


@router.post("/appeal", response_model=AppealResponse)
async def generate_appeal_letter(
    request: AppealRequest,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """สร้างหนังสืออุทธรณ์สำหรับเคสที่ถูก deny"""
    claim_data = {
        "hn": request.hn,
        "an": request.an,
        "principal_dx": request.principal_dx or "",
        "procedures": request.procedures,
    }

    letter = await generate_appeal(
        claim_data, request.deny_reason, request.department
    )

    # Update appeal status if claim exists in DB
    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    record = await claim_repo.get_by_an(request.an)
    if record and record.appeal_status in (AppealStatus.NONE, AppealStatus.NONE.value, None):
        from core.models import AppealStatus
        await claim_repo.update_appeal_status(request.an, AppealStatus.DRAFTED)
        record.appeal_text = letter

    await audit_repo.log_action(
        an=request.an, action="appeal_draft",
        details={"deny_reason": request.deny_reason},
        user=user["sub"],
    )

    return AppealResponse(
        letter_text=letter,
        supporting_docs=[
            "สำเนาเวชระเบียน",
            "รายงานผลหัตถการ",
            "ผล Lab ที่เกี่ยวข้อง",
        ],
    )


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """KPI Dashboard data — queries actual DB"""
    from sqlalchemy import func, select
    from core.database import ClaimRecord

    total = (await session.execute(select(func.count(ClaimRecord.id)))).scalar() or 0
    denied = (await session.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.fdh_status == "denied")
    )).scalar() or 0
    deny_rate = (denied / total * 100) if total > 0 else 0.0
    avg_score = (await session.execute(
        select(func.avg(ClaimRecord.check_score))
    )).scalar() or 0.0
    revenue_at_risk = (await session.execute(
        select(func.coalesce(func.sum(ClaimRecord.claim_amount), 0.0))
        .where(ClaimRecord.fdh_status == "denied")
    )).scalar() or 0.0
    revenue_recovered = (await session.execute(
        select(func.coalesce(func.sum(ClaimRecord.revenue_recovered), 0.0))
    )).scalar() or 0.0

    return DashboardStats(
        total_claims=total,
        denied_claims=denied,
        deny_rate=round(deny_rate, 2),
        revenue_at_risk=revenue_at_risk,
        revenue_recovered=revenue_recovered,
        avg_score=round(float(avg_score), 1),
    )
```

Keep `/health` endpoint public (no auth). Keep `/status/{an}` behind auth (added in Task 10).

- [ ] **Step 3: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add api/main.py api/routes.py
git commit -m "feat(phase1): wire auth + DB persistence into all endpoints"
```

---

### Task 9: docker-compose for development

**Files:**
- Create: `docker-compose.yml`
- Modify: `.env.example` — add new variables

- [ ] **Step 1: Create docker-compose.yml**

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - .:/app

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: hospital_claim_ai
      POSTGRES_USER: hcai
      POSTGRES_PASSWORD: hcai_dev_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hcai"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  pgdata:
```

- [ ] **Step 2: Update .env.example with new variables**

Add to `.env.example`:
```
JWT_SECRET_KEY=change-this-to-at-least-32-chars-long-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_HOURS=8
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "feat(phase1): add docker-compose for dev, update env example"
```

---

### Task 10: Claim status endpoint and enhanced health check

**Files:**
- Modify: `api/routes.py` — add `/status/{an}` and update `/health`
- Create: `tests/test_routes.py`

- [ ] **Step 1: Write test for status endpoint**

Create `tests/test_routes.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.models import FDHStatus, AppealStatus


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self):
        from fastapi.testclient import TestClient
        from api.main import app
        client = TestClient(app)
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
```

- [ ] **Step 2: Add /status/{an} endpoint to routes.py**

```python
@router.get("/status/{an}")
async def get_claim_status(
    an: str,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """ดูสถานะเคสตาม AN"""
    claim_repo = ClaimRepository(session)
    record = await claim_repo.get_by_an(an)
    if record is None:
        raise HTTPException(404, f"Claim {an} not found")
    audit_repo = AuditRepository(session)
    trail = await audit_repo.get_audit_trail(an)
    return {
        "an": record.an,
        "hn": record.hn,
        "department": record.department,
        "fdh_status": record.fdh_status,
        "appeal_status": record.appeal_status,
        "score": record.check_score,
        "ready_to_submit": record.ready_to_submit,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "audit_trail": [
            {"action": a.action, "details": a.details, "user": a.user, "at": a.created_at}
            for a in trail
        ],
    }
```

- [ ] **Step 3: Update health check with dependency status**

```python
@router.get("/health")
async def health_check():
    from core.config import get_settings
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.app_version,
        "services": {
            "database": "configured" if settings.database_url else "not_configured",
            "ai_engine": "configured" if settings.anthropic_api_key else "not_configured",
            "line": "configured" if settings.line_channel_token else "not_configured",
            "fdh": "configured" if settings.fdh_api_key else "not_configured",
        },
    }
```

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add api/routes.py tests/test_routes.py
git commit -m "feat(phase1): add claim status endpoint and enhanced health check"
```

---

### Task 11: Create initial admin user script

**Files:**
- Create: `scripts/create_admin.py`

- [ ] **Step 1: Create admin bootstrap script**

Create `scripts/create_admin.py`:

```python
"""Bootstrap script — create the initial admin user."""

import asyncio
import sys
from core.database import get_session_factory
from core.repositories import UserRepository
from api.auth.jwt_handler import hash_password


async def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_admin.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        sys.exit(1)

    factory = get_session_factory()
    async with factory() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_username(username)
        if existing:
            print(f"User '{username}' already exists")
            sys.exit(1)

        user = await repo.create_user(
            username=username,
            hashed_password=hash_password(password),
            role="admin",
        )
        await session.commit()
        print(f"Admin user '{username}' created (id={user.id})")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Commit**

```bash
git add scripts/create_admin.py
git commit -m "feat(phase1): add admin user bootstrap script"
```

---

### Task 12: Final integration test and cleanup

- [ ] **Step 1: Run full test suite**

Run: `python3 -m pytest tests/ -v --tb=short`
Expected: All tests pass (existing rule engine tests + new auth, models, state machine, repository tests).

- [ ] **Step 2: Verify docker-compose starts cleanly**

Run: `docker-compose up -d db && sleep 3 && docker-compose ps`
Expected: PostgreSQL container is healthy.

- [ ] **Step 3: Run Alembic migration against the dev DB**

Run: `DATABASE_URL=postgresql+asyncpg://hcai:hcai_dev_password@localhost:5432/hospital_claim_ai alembic upgrade head`
Expected: Migration applies successfully.

- [ ] **Step 4: Create admin user**

Run: `DATABASE_URL=... python3 scripts/create_admin.py admin admin12345678`
Expected: Admin user created.

- [ ] **Step 5: Final commit with all Phase 1 complete**

```bash
git add -A
git commit -m "feat(phase1): complete data layer + auth — Phase 1 done"
```
