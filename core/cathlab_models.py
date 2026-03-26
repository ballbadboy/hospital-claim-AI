"""Cath Lab Claim Data Models — Pydantic schemas for e-Claim data."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DeviceItem(BaseModel):
    type: int = Field(description="3=วัสดุสิ้นเปลือง, 4=ข้อต่อ, 5=อวัยวะเทียม")
    code: str = Field(description="รหัสอุปกรณ์ สปสช.")
    name: str | None = None
    qty: int = 1
    rate: float = 0
    serial_no: str | None = Field(None, description="Lot/Serial number (ต้องตรง GPO VMI)")


class DrugItem(BaseModel):
    did: str = Field(description="Drug ID (GPUID / TMT code)")
    name: str | None = None
    amount: float = 0


class CathLabClaim(BaseModel):
    """Input model: Cath Lab claim data parsed from e-Claim CSV or JSON."""

    rep_no: str | None = None
    tran_id: str | None = None
    hn: str
    an: str
    pid: str = Field(description="CID 13 หลัก")
    patient_name: str | None = None
    patient_type: str = "IP"
    age: int | None = None
    sex: str | None = None
    admit_date: datetime
    discharge_date: datetime
    discharge_type: str = "1"
    principal_dx: str = Field(description="ICD-10 primary diagnosis")
    secondary_dx: list[str] = []
    procedures: list[str] = Field(default=[], description="ICD-9-CM procedure codes")
    drg: str | None = None
    rw: float | None = None
    charge_amount: float = 0
    expected_payment: float | None = None
    fund: str = "UCS"
    authen_code: str | None = None
    devices: list[DeviceItem] = []
    drugs: list[DrugItem] = []
    deny_codes: list[str] = []
    denied_items: list[str] = []
    inst_amount: float = 0
    clinical_notes: str | None = None

    @field_validator("pid")
    @classmethod
    def validate_cid(cls, v: str) -> str:
        digits = v.replace("-", "").replace(" ", "")
        if len(digits) != 13:
            raise ValueError(f"CID ต้อง 13 หลัก (ได้ {len(digits)} หลัก)")
        return digits

    @property
    def los(self) -> int:
        delta = self.discharge_date - self.admit_date
        days = delta.days
        return max(days, 1)

    @property
    def days_since_discharge(self) -> int:
        return (datetime.now() - self.discharge_date).days


class CheckpointResult(BaseModel):
    checkpoint: int
    name: str
    status: str = Field(description="pass/warning/critical")
    message: str
    auto_fixable: bool = False
    fix_applied: str | None = None
    details: dict | None = None


class Optimization(BaseModel):
    current_code: str | None = None
    suggested_code: str
    reason: str
    clinical_evidence: str | None = None
    rw_impact: float = Field(description="Delta RW")
    money_impact: float = Field(description="Delta baht (base rate 8,350)")


class CheckResult(BaseModel):
    """Output model: Pre-submission validation result."""

    an: str
    score: int = Field(ge=0, le=100)
    status: str = Field(description="pass/warning/critical")
    checkpoints: list[CheckpointResult]
    optimizations: list[Optimization] = []
    auto_fixes_applied: list[str] = []
    expected_drg: str | None = None
    expected_rw: float | None = None
    expected_payment: float | None = None
    warnings: list[str] = []
    errors: list[str] = []


class DenyCodeExplained(BaseModel):
    code: str
    meaning: str
    fix: str


class DenyAnalysis(BaseModel):
    """Output model: Post-denial analysis result."""

    an: str
    category: str = Field(description="coding_error/device/timing/eligibility/clinical")
    severity: str = Field(description="high/medium/low")
    root_cause: str
    deny_codes_explained: list[DenyCodeExplained]
    recommended_action: str = Field(description="auto_fix/appeal/escalate/write_off")
    fix_steps: list[str]
    appeal_draft: str | None = None
    recovery_chance: float = Field(ge=0, le=1)
    estimated_recovery: float
    confidence: float = Field(ge=0, le=1)


class DRGInfo(BaseModel):
    """DRG lookup result from RW table."""

    drg: str
    rw: float
    wtlos: float
    ot: int
    rw0d: float
    of_factor: float
    description: str
    payment_estimate_in_zone: float = Field(description="RW × 8,350")
    payment_estimate_out_zone: float = Field(description="RW × 9,600")
