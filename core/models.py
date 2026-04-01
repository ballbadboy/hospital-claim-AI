from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enum import Enum
from datetime import datetime, timezone


class Department(str, Enum):
    CATH_LAB = "cath_lab"
    OR_SURGERY = "or_surgery"
    CHEMO = "chemo"
    DIALYSIS = "dialysis"
    ICU_NICU = "icu_nicu"
    ER_UCEP = "er_ucep"
    ODS_MIS = "ods_mis"
    OPD_NCD = "opd_ncd"
    REHAB = "rehab_palliative"


class Fund(str, Enum):
    UC = "uc"
    SSS = "sss"
    CSMBS = "csmbs"


class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    PASSED = "passed"
    OPTIMIZATION = "optimization"


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


class ClaimInput(BaseModel):
    hn: str = Field(..., description="Hospital Number")
    an: Optional[str] = Field(None, description="Admission Number")
    patient_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[Sex] = None
    fund: Fund = Fund.UC

    principal_dx: str = Field(..., min_length=1, description="ICD-10-TM Principal Diagnosis")
    secondary_dx: list[str] = Field(default_factory=list, max_length=50)
    procedures: list[str] = Field(default_factory=list, max_length=50, description="ICD-9-CM codes")

    admit_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    submit_date: Optional[datetime] = None

    ward: Optional[str] = None
    authen_code: Optional[str] = None

    devices: list[dict] = Field(default_factory=list, max_length=20, description="Stent/implant details")
    clinical_docs: dict = Field(default_factory=dict, description="Available documentation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hn": "12345",
                "an": "AN2026001",
                "principal_dx": "I21.1",
                "secondary_dx": ["E11.9", "I10"],
                "procedures": ["37.22", "88.56", "36.07"],
                "fund": "uc",
                "admit_date": "2026-02-14T07:50:00",
                "discharge_date": "2026-02-17T10:00:00",
                "devices": [{"type": "DES", "brand": "Xience", "size": "3.0x28mm", "lot": "ABC123", "qty": 1}],
                "clinical_docs": {"troponin": True, "ekg": True, "cath_report": True, "d2b_time": "65min"}
            }
        }
    )


class CheckResult(BaseModel):
    severity: Severity
    checkpoint: str
    message: str
    fix_action: Optional[str] = None


class ClaimCheckResponse(BaseModel):
    hn: str
    an: Optional[str]
    department: Department
    fund: Fund
    principal_dx: str
    procedures: list[str]
    expected_drg: Optional[str] = None
    estimated_rw: Optional[float] = None
    estimated_claim: Optional[float] = None

    results: list[CheckResult] = []
    score: int = 0
    ready_to_submit: bool = False

    critical_count: int = 0
    warning_count: int = 0
    passed_count: int = 0
    optimization_count: int = 0

    ai_analysis: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AppealRequest(BaseModel):
    hn: str
    an: str
    deny_reason: str
    department: Department
    fund: Fund = Fund.UC
    principal_dx: Optional[str] = None
    procedures: list[str] = Field(default_factory=list)
    additional_info: Optional[str] = None


class AppealResponse(BaseModel):
    letter_text: str
    supporting_docs: list[str]
    estimated_recovery: Optional[float] = None


class BatchCheckRequest(BaseModel):
    claims: list[ClaimInput]


class DashboardStats(BaseModel):
    total_claims: int = 0
    denied_claims: int = 0
    deny_rate: float = 0.0
    revenue_at_risk: float = 0.0
    revenue_recovered: float = 0.0
    avg_score: float = 0.0
    by_department: dict = Field(default_factory=dict)
    by_deny_reason: dict = Field(default_factory=dict)
