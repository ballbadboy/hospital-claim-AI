# Cath Lab Core Engine + API — Design Spec

> Date: 2026-03-26
> Author: Dr.Kasemson Kasemwong + Claude
> Status: Approved
> Hospital: 11855 รพ.พญาไทศรีราชา เขต 6 ชลบุรี

## Goal

Implement FastAPI endpoints for Cath Lab claim validation (pre-submission) and deny analysis (post-denial). Both share a core engine that uses knowledge base files for deterministic checks + Claude API for clinical reasoning.

## Architecture

```
REST API (FastAPI)
├── POST /api/v1/cathlab/check         → Pre-submission validation
├── POST /api/v1/cathlab/analyze-deny  → Post-denial analysis
├── POST /api/v1/cathlab/parse-eclaim  → Parse e-Claim CSV
└── GET  /api/v1/cathlab/drg-lookup/{code} → DRG + RW lookup

Core Engine
├── eclaim_parser.py      → Parse e-Claim CSV format
├── cathlab_validator.py  → 8 checkpoints
├── ccmcc_optimizer.py    → CC/MCC suggestions + RW impact
├── deny_analyzer.py      → Root cause + fix + appeal
├── drg_calculator.py     → DRG lookup + payment calc
└── ai_engine.py          → Claude API (existing, add cathlab prompts)

Knowledge Base (read-only files)
├── drg-rw-table-cardiac.md    → 60+ cardiac DRGs with RW
├── cardiac-codes.md           → ICD-10 + ICD-9-CM codes
├── deny-codes.md              → 500+ C-codes + deny codes
├── validation-rules.md        → 8 checkpoints spec
├── clinical-criteria.md       → STEMI/NSTEMI/UA criteria
└── core-rules.md              → CC/MCC tables, 16-file rules
```

## Data Models

### Input: CathLabClaim

```python
class CathLabClaim(BaseModel):
    rep_no: str | None = None
    tran_id: str | None = None
    hn: str
    an: str
    pid: str                          # CID 13 digits
    patient_name: str | None = None
    patient_type: str = "IP"
    age: int | None = None
    sex: str | None = None
    admit_date: datetime
    discharge_date: datetime
    discharge_type: str = "1"
    principal_dx: str                 # ICD-10
    secondary_dx: list[str] = []
    procedures: list[str] = []        # ICD-9-CM
    drg: str | None = None
    rw: float | None = None
    charge_amount: float = 0
    expected_payment: float | None = None
    fund: str = "UCS"
    authen_code: str | None = None
    devices: list[DeviceItem] = []
    drugs: list[DrugItem] = []
    deny_codes: list[str] = []        # For analyze-deny
    denied_items: list[str] = []
    inst_amount: float = 0
    clinical_notes: str | None = None

class DeviceItem(BaseModel):
    type: int                         # 3/4/5
    code: str
    name: str | None = None
    qty: int = 1
    rate: float = 0
    serial_no: str | None = None

class DrugItem(BaseModel):
    did: str                          # GPUID / TMT
    name: str | None = None
    amount: float = 0
```

### Output: CheckResult

```python
class CheckpointResult(BaseModel):
    checkpoint: int                   # 1-8
    name: str
    status: str                       # pass/warning/critical
    message: str
    auto_fixable: bool = False
    fix_applied: str | None = None

class Optimization(BaseModel):
    current_code: str | None = None
    suggested_code: str
    reason: str
    clinical_evidence: str | None = None
    rw_impact: float                  # delta RW
    money_impact: float              # delta baht

class CheckResult(BaseModel):
    an: str
    score: int                        # 0-100
    status: str                       # pass/warning/critical
    checkpoints: list[CheckpointResult]
    optimizations: list[Optimization]
    auto_fixes_applied: list[str]
    expected_drg: str | None = None
    expected_rw: float | None = None
    expected_payment: float | None = None
    warnings: list[str]
    errors: list[str]
```

### Output: DenyAnalysis

```python
class DenyCodeExplained(BaseModel):
    code: str
    meaning: str
    fix: str

class DenyAnalysis(BaseModel):
    an: str
    category: str                     # coding_error/device/timing/eligibility/clinical
    severity: str                     # high/medium/low
    root_cause: str
    deny_codes_explained: list[DenyCodeExplained]
    recommended_action: str           # auto_fix/appeal/escalate/write_off
    fix_steps: list[str]
    appeal_draft: str | None = None
    recovery_chance: float            # 0.0-1.0
    estimated_recovery: float
    confidence: float
```

## Endpoints

### POST /api/v1/cathlab/check

Pre-submission validation: runs 8 checkpoints + CC/MCC optimization.

Input: CathLabClaim (JSON)
Output: CheckResult

### POST /api/v1/cathlab/analyze-deny

Post-denial analysis: identifies root cause, suggests fix, drafts appeal.

Input: CathLabClaim with deny_codes populated
Output: DenyAnalysis

### POST /api/v1/cathlab/parse-eclaim

Parses e-Claim CSV export into structured CathLabClaim objects.

Input: UploadFile (CSV)
Output: list[CathLabClaim]

### GET /api/v1/cathlab/drg-lookup/{drg_code}

Looks up DRG info from knowledge base.

Input: DRG code (e.g. "05290")
Output: {drg, rw, wtlos, ot, rw0d, description, payment_estimate}

## 8 Checkpoints (cathlab_validator.py)

1. **Basic Data** — AN, HN, CID checksum, PDx exists, sex/age match, dates valid
2. **Dx-Proc Match** — PDx I20-I25 matches procedures 36.0x/37.2x/88.5x
3. **Device Docs** — Stent type/serial/lot/qty/rate vs GPO VMI
4. **16-File Completeness** — IPD/DIA/OPR/ADP/DRU/CHA/INS fields
5. **Timing** — ≤30 days, authen code valid
6. **CC/MCC Optimization** — DM specific, HF specific, CKD staged
7. **DRG Verification** — Expected DRG matches, RW reasonable
8. **Drug/Lab Catalog** — TMT code match, Clopidogrel/Heparin/Ticagrelor

## Real Test Case

```
AN: 69-03556
DRG: 05290 (Acute MI w single vessel PTCA wo sig CCC)
RW: 8.6544
Charge: 31,517 | Expected: 71,322 | Actual: 0 (DENY)
Deny: HC09, IP01, HC13
Denied: CLOPIDOGREL_DRUG, INST (31,490), IPINRGR

Expected deny_analyzer output:
  category: device_documentation
  root_cause: HC09 = stent/device documentation incomplete
  fix: check stent serial, Clopidogrel TMT, ADP file
  recovery_chance: 0.85
  estimated_recovery: 71,322
```

## Implementation Order

1. Data models (Pydantic)
2. e-Claim CSV parser
3. DRG calculator (RW lookup)
4. 8-checkpoint validator
5. CC/MCC optimizer
6. Deny analyzer
7. AI engine integration
8. API routes
9. Tests with real case
