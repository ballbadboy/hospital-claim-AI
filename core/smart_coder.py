"""Smart Coder — Auto-generate ICD-10/ICD-9-CM codes from Thai clinical notes.

Parses Thai/English clinical text using keyword matching + regex extraction,
maps to optimal ICD codes with CC/MCC optimization, and estimates DRG payment.
"""

import re
from pydantic import BaseModel, Field

from core.drg_calculator import lookup_drg, BASE_RATE_IN_ZONE


# ═══════════════════════════════════════════════
# Output Models
# ═══════════════════════════════════════════════

class CodeSuggestion(BaseModel):
    code: str
    description: str
    type: str = Field(description="pdx/sdx/proc")
    cc_mcc: str | None = None  # CC/MCC/None
    confidence: float = Field(ge=0, le=1)
    reason: str
    clinical_evidence: str


class CodingResult(BaseModel):
    pdx: CodeSuggestion
    sdx: list[CodeSuggestion]
    procedures: list[CodeSuggestion]
    expected_drg: str | None = None
    expected_rw: float | None = None
    expected_payment: float | None = None
    optimization_notes: list[str] = []
    warnings: list[str] = []


# ═══════════════════════════════════════════════
# Keyword Patterns (Thai + English)
# ═══════════════════════════════════════════════

# Diagnosis keywords
DX_STEMI = re.compile(
    r"(?<!N)STEMI|ST[\s\-]?elevation\s*MI|"
    r"กล้ามเนื้อหัวใจตายเฉียบพลัน.*ST\s*elevation|"
    r"acute\s+transmural\s+MI",
    re.IGNORECASE,
)
DX_NSTEMI = re.compile(
    r"NSTEMI|non[\s\-]?ST[\s\-]?elevation\s*MI|"
    r"subendocardial\s+MI",
    re.IGNORECASE,
)
DX_UA = re.compile(
    r"\bUA\b|unstable\s+angina|"
    r"กล้ามเนื้อหัวใจขาดเลือดเฉียบพลันชนิดไม่คงที่|"
    r"angina\s+ไม่คงที่",
    re.IGNORECASE,
)
DX_ANGINA = re.compile(
    r"angina|เจ็บหน้าอก|chest\s+pain|แน่นหน้าอก",
    re.IGNORECASE,
)
DX_MI = re.compile(
    r"\bMI\b|myocardial\s+infarction|หัวใจขาดเลือด|กล้ามเนื้อหัวใจตาย",
    re.IGNORECASE,
)
DX_IHD = re.compile(
    r"\bCAD\b|coronary\s+artery\s+disease|"
    r"ischemic\s+heart|chronic\s+IHD|"
    r"โรคหลอดเลือดหัวใจ",
    re.IGNORECASE,
)

# Wall/territory keywords for STEMI sub-classification
WALL_ANTERIOR = re.compile(
    r"anterior|LAD|หน้า|ant\s*wall|V1.*V4|V[1-4]",
    re.IGNORECASE,
)
WALL_INFERIOR = re.compile(
    r"inferior|RCA|ล่าง|inf\s*wall|II.*III.*aVF",
    re.IGNORECASE,
)
WALL_OTHER = re.compile(
    r"lateral|posterior|LCx|circumflex|ด้านข้าง|ด้านหลัง",
    re.IGNORECASE,
)

# EKG keywords
EKG_ST_ELEV = re.compile(
    r"ST\s*elevation|ST\s*elev|STE\b|ST\s*ยก|ST\s*สูง",
    re.IGNORECASE,
)
EKG_ST_DEP = re.compile(
    r"ST\s*depression|ST\s*dep|STD\b|ST\s*ต่ำ|ST\s*กด",
    re.IGNORECASE,
)
EKG_LBBB = re.compile(r"LBBB|left\s+bundle\s+branch\s+block", re.IGNORECASE)
EKG_NORMAL = re.compile(r"EKG\s*normal|normal\s*EKG|คลื่นหัวใจปกติ", re.IGNORECASE)

# Procedure keywords
PROC_PCI = re.compile(
    r"\bPCI\b|percutaneous\s+coronary|PTCA|"
    r"balloon\s+angioplasty|ขยายหลอดเลือดหัวใจ",
    re.IGNORECASE,
)
PROC_DES = re.compile(
    r"\bDES\b|drug[\s\-]?eluting\s+stent|ขดลวดเคลือบยา",
    re.IGNORECASE,
)
PROC_BMS = re.compile(
    r"\bBMS\b|bare[\s\-]?metal\s+stent|ขดลวดไม่เคลือบยา",
    re.IGNORECASE,
)
PROC_STENT = re.compile(
    r"\bstent\b|ใส่ขดลวด|ขดลวด",
    re.IGNORECASE,
)
PROC_CATH = re.compile(
    r"\bcath\b|catheterization|สวนหัวใจ|cardiac\s+cath",
    re.IGNORECASE,
)
PROC_ANGIO = re.compile(
    r"angiography|angiogram|coronary\s+angio|ฉีดสี",
    re.IGNORECASE,
)
PROC_MULTI_VESSEL = re.compile(
    r"multi[\s\-]?vessel|หลายเส้น|2\s*vessel|3\s*vessel|"
    r"multiple\s+vessel|two\s+vessel|three\s+vessel",
    re.IGNORECASE,
)
PROC_BALLOON = re.compile(
    r"balloon|บอลลูน|POBA|plain\s+old\s+balloon",
    re.IGNORECASE,
)

# Comorbidity keywords
COMOR_DM = re.compile(
    r"\bDM\b|diabetes|เบาหวาน|type\s*2\s*DM|T2DM",
    re.IGNORECASE,
)
COMOR_HT = re.compile(
    r"\bHT\b|hypertension|ความดัน|ความดันโลหิตสูง|ความดันสูง",
    re.IGNORECASE,
)
COMOR_CKD = re.compile(
    r"\bCKD\b|chronic\s+kidney|ไตเรื้อรัง|โรคไต",
    re.IGNORECASE,
)
COMOR_HF = re.compile(
    r"\bHF\b|heart\s+failure|หัวใจล้มเหลว|หัวใจวาย|CHF\b",
    re.IGNORECASE,
)
COMOR_AF = re.compile(
    r"\bAF\b|atrial\s+fibrillation|หัวใจเต้นผิดจังหวะ|a[\.\s]*fib",
    re.IGNORECASE,
)
COMOR_COPD = re.compile(
    r"\bCOPD\b|chronic\s+obstructive|ปอดอุดกั้นเรื้อรัง|ถุงลมโป่งพอง",
    re.IGNORECASE,
)
COMOR_DYSLIPID = re.compile(
    r"dyslipidemia|hyperlipidemia|ไขมันสูง|ไขมันในเลือดสูง|DLP",
    re.IGNORECASE,
)

# Lab value patterns — extract numbers
LAB_TROPONIN = re.compile(
    r"(?:troponin|trop|hs[\s\-]?trop(?:onin)?(?:\s*[TI])?)[\s:=]*"
    r"([0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)
LAB_TROPONIN_HIGH = re.compile(
    r"troponin\s*(?:สูง|elevated|positive|high|เพิ่ม|abnormal|rise)",
    re.IGNORECASE,
)
LAB_TROPONIN_NORMAL = re.compile(
    r"troponin\s*(?:ปกติ|normal|negative|ไม่สูง|low|neg)",
    re.IGNORECASE,
)
LAB_EF = re.compile(
    r"(?:EF|ejection\s+fraction|LVEF)[\s:=]*([0-9]+(?:\.[0-9]+)?)\s*%?",
    re.IGNORECASE,
)
LAB_EGFR = re.compile(
    r"(?:eGFR|GFR)[\s:=]*([0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)
LAB_CR = re.compile(
    r"(?:Cr|creatinine)[\s:=]*([0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)
LAB_HBA1C = re.compile(
    r"(?:HbA1c|A1c|HbA1C)[\s:=]*([0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)
LAB_BS = re.compile(
    r"(?:blood\s+sugar|FBS|FPG|glucose|น้ำตาล)[\s:=]*([0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)


# ═══════════════════════════════════════════════
# Internal Data Structures
# ═══════════════════════════════════════════════

class _ExtractedData:
    """Internal: holds all extracted clinical info from text."""

    def __init__(self):
        # Diagnosis flags
        self.is_stemi = False
        self.is_nstemi = False
        self.is_ua = False
        self.is_angina = False
        self.is_mi = False
        self.is_ihd = False

        # Wall territory
        self.wall_anterior = False
        self.wall_inferior = False
        self.wall_other = False

        # EKG
        self.st_elevation = False
        self.st_depression = False
        self.lbbb = False
        self.ekg_normal = False

        # Procedures
        self.has_pci = False
        self.has_des = False
        self.has_bms = False
        self.has_stent = False
        self.has_cath = False
        self.has_angio = False
        self.multi_vessel = False
        self.has_balloon = False

        # Comorbidities
        self.has_dm = False
        self.has_ht = False
        self.has_ckd = False
        self.has_hf = False
        self.has_af = False
        self.has_copd = False
        self.has_dyslipid = False

        # Lab values (None = not mentioned)
        self.troponin_value: float | None = None
        self.troponin_high: bool | None = None  # True/False/None
        self.ef_value: float | None = None
        self.egfr_value: float | None = None
        self.cr_value: float | None = None
        self.hba1c_value: float | None = None
        self.bs_value: float | None = None

        # Raw lowercased text for keyword matching
        self.raw_text: str = ""


# ═══════════════════════════════════════════════
# Step 1: Parse clinical text
# ═══════════════════════════════════════════════

def _extract(text: str) -> _ExtractedData:
    """Extract clinical info from Thai/English clinical notes."""
    d = _ExtractedData()
    d.raw_text = text.lower()

    # Diagnosis
    d.is_stemi = bool(DX_STEMI.search(text))
    d.is_nstemi = bool(DX_NSTEMI.search(text))
    d.is_ua = bool(DX_UA.search(text))
    d.is_angina = bool(DX_ANGINA.search(text))
    d.is_mi = bool(DX_MI.search(text))
    d.is_ihd = bool(DX_IHD.search(text))

    # Wall
    d.wall_anterior = bool(WALL_ANTERIOR.search(text))
    d.wall_inferior = bool(WALL_INFERIOR.search(text))
    d.wall_other = bool(WALL_OTHER.search(text))

    # EKG
    d.st_elevation = bool(EKG_ST_ELEV.search(text))
    d.st_depression = bool(EKG_ST_DEP.search(text))
    d.lbbb = bool(EKG_LBBB.search(text))
    d.ekg_normal = bool(EKG_NORMAL.search(text))

    # Procedures
    d.has_pci = bool(PROC_PCI.search(text))
    d.has_des = bool(PROC_DES.search(text))
    d.has_bms = bool(PROC_BMS.search(text))
    d.has_stent = bool(PROC_STENT.search(text))
    d.has_cath = bool(PROC_CATH.search(text))
    d.has_angio = bool(PROC_ANGIO.search(text))
    d.multi_vessel = bool(PROC_MULTI_VESSEL.search(text))
    d.has_balloon = bool(PROC_BALLOON.search(text))

    # Comorbidities
    d.has_dm = bool(COMOR_DM.search(text))
    d.has_ht = bool(COMOR_HT.search(text))
    d.has_ckd = bool(COMOR_CKD.search(text))
    d.has_hf = bool(COMOR_HF.search(text))
    d.has_af = bool(COMOR_AF.search(text))
    d.has_copd = bool(COMOR_COPD.search(text))
    d.has_dyslipid = bool(COMOR_DYSLIPID.search(text))

    # Lab values — Troponin
    trop_match = LAB_TROPONIN.search(text)
    if trop_match:
        d.troponin_value = float(trop_match.group(1))
        # Troponin > 0.04 ng/mL (conventional) or >14 ng/L (hs-TnT) → elevated
        # Use 0.04 as threshold for conventional, context-dependent
        d.troponin_high = d.troponin_value > 0.04
    if LAB_TROPONIN_HIGH.search(text):
        d.troponin_high = True
    if LAB_TROPONIN_NORMAL.search(text):
        d.troponin_high = False

    # EF
    ef_match = LAB_EF.search(text)
    if ef_match:
        d.ef_value = float(ef_match.group(1))

    # eGFR
    egfr_match = LAB_EGFR.search(text)
    if egfr_match:
        d.egfr_value = float(egfr_match.group(1))

    # Cr
    cr_match = LAB_CR.search(text)
    if cr_match:
        d.cr_value = float(cr_match.group(1))

    # HbA1c
    hba1c_match = LAB_HBA1C.search(text)
    if hba1c_match:
        d.hba1c_value = float(hba1c_match.group(1))

    # Blood sugar
    bs_match = LAB_BS.search(text)
    if bs_match:
        d.bs_value = float(bs_match.group(1))

    return d


# ═══════════════════════════════════════════════
# Step 2: Map to ICD codes
# ═══════════════════════════════════════════════

def _determine_pdx(d: _ExtractedData) -> CodeSuggestion:
    """Determine principal diagnosis based on extracted data."""

    # Priority 1: Explicit STEMI or (ST elevation + Troponin high)
    if d.is_stemi or (d.st_elevation and d.troponin_high is True) or (d.lbbb and d.troponin_high is True):
        # Determine wall
        if d.wall_anterior:
            return CodeSuggestion(
                code="I21.0",
                description="Acute transmural MI of anterior wall (STEMI)",
                type="pdx",
                confidence=0.95 if d.is_stemi else 0.85,
                reason="STEMI anterior wall: ST elevation + Troponin + anterior territory",
                clinical_evidence=_pdx_evidence(d),
            )
        elif d.wall_inferior:
            return CodeSuggestion(
                code="I21.1",
                description="Acute transmural MI of inferior wall (STEMI)",
                type="pdx",
                confidence=0.95 if d.is_stemi else 0.85,
                reason="STEMI inferior wall: ST elevation + Troponin + inferior territory",
                clinical_evidence=_pdx_evidence(d),
            )
        elif d.wall_other:
            return CodeSuggestion(
                code="I21.2",
                description="Acute transmural MI of other sites (STEMI)",
                type="pdx",
                confidence=0.90,
                reason="STEMI other territory: ST elevation + Troponin + lateral/posterior",
                clinical_evidence=_pdx_evidence(d),
            )
        else:
            return CodeSuggestion(
                code="I21.3",
                description="Acute transmural MI of unspecified site (STEMI)",
                type="pdx",
                confidence=0.80,
                reason="STEMI unspecified wall: no territory identified in notes",
                clinical_evidence=_pdx_evidence(d),
            )

    # Priority 2: NSTEMI or (Troponin high + no ST elevation)
    if d.is_nstemi or (d.troponin_high and not d.st_elevation):
        return CodeSuggestion(
            code="I21.4",
            description="Acute subendocardial MI (NSTEMI)",
            type="pdx",
            confidence=0.95 if d.is_nstemi else 0.85,
            reason="NSTEMI: Troponin elevated without ST elevation",
            clinical_evidence=_pdx_evidence(d),
        )

    # Priority 3: UA or (symptoms + Troponin normal)
    if d.is_ua or (d.troponin_high is False and (d.is_angina or d.is_mi)):
        return CodeSuggestion(
            code="I20.0",
            description="Unstable angina",
            type="pdx",
            confidence=0.90 if d.is_ua else 0.80,
            reason="UA: ischemic symptoms with normal Troponin",
            clinical_evidence=_pdx_evidence(d),
        )

    # Priority 4: Angina/chest pain without specific markers
    if d.is_angina and d.troponin_high is None:
        return CodeSuggestion(
            code="I20.0",
            description="Unstable angina",
            type="pdx",
            confidence=0.65,
            reason="Chest pain symptoms without Troponin result; defaulting to UA",
            clinical_evidence=_pdx_evidence(d),
        )

    # Priority 5: Chronic IHD/CAD
    if d.is_ihd:
        return CodeSuggestion(
            code="I25.1",
            description="Atherosclerotic heart disease (Chronic IHD)",
            type="pdx",
            confidence=0.80,
            reason="Chronic IHD: no acute markers found",
            clinical_evidence=_pdx_evidence(d),
        )

    # Priority 6: MI keyword without specifics
    if d.is_mi:
        return CodeSuggestion(
            code="I21.9",
            description="Acute MI, unspecified",
            type="pdx",
            confidence=0.50,
            reason="MI mentioned but insufficient detail to classify STEMI/NSTEMI",
            clinical_evidence=_pdx_evidence(d),
        )

    # Fallback: if procedures suggest cardiac but no diagnosis keywords
    if d.has_pci or d.has_cath:
        return CodeSuggestion(
            code="I25.1",
            description="Atherosclerotic heart disease (Chronic IHD)",
            type="pdx",
            confidence=0.50,
            reason="Cardiac procedure found without clear diagnosis; defaulting to Chronic IHD",
            clinical_evidence=_pdx_evidence(d),
        )

    # Ultimate fallback
    return CodeSuggestion(
        code="I25.9",
        description="Chronic ischemic heart disease, unspecified",
        type="pdx",
        confidence=0.30,
        reason="Insufficient clinical data for specific diagnosis",
        clinical_evidence=_pdx_evidence(d),
    )


def _pdx_evidence(d: _ExtractedData) -> str:
    """Build clinical evidence string for PDx."""
    parts = []
    if d.is_stemi:
        parts.append("STEMI mentioned")
    if d.is_nstemi:
        parts.append("NSTEMI mentioned")
    if d.is_ua:
        parts.append("UA mentioned")
    if d.st_elevation:
        parts.append("ST elevation on EKG")
    if d.st_depression:
        parts.append("ST depression on EKG")
    if d.lbbb:
        parts.append("LBBB on EKG")
    if d.troponin_value is not None:
        parts.append(f"Troponin={d.troponin_value}")
    if d.troponin_high is True:
        parts.append("Troponin elevated")
    if d.troponin_high is False:
        parts.append("Troponin normal")
    if d.wall_anterior:
        parts.append("anterior wall")
    if d.wall_inferior:
        parts.append("inferior wall")
    if d.wall_other:
        parts.append("lateral/posterior wall")
    if d.is_angina:
        parts.append("chest pain/angina")
    return "; ".join(parts) if parts else "minimal clinical data"


def _determine_sdx(d: _ExtractedData) -> list[CodeSuggestion]:
    """Determine secondary diagnoses with CC/MCC optimization."""
    sdx: list[CodeSuggestion] = []

    # Heart Failure — CC/MCC optimization: EF <40% → I50.21 (MCC) not I50.9
    if d.has_hf or (d.ef_value is not None and d.ef_value < 40):
        if d.ef_value is not None and d.ef_value < 40:
            sdx.append(CodeSuggestion(
                code="I50.21",
                description="Acute systolic (congestive) heart failure",
                type="sdx",
                cc_mcc="MCC",
                confidence=0.90,
                reason=f"EF {d.ef_value}% (<40%) = systolic HF → I50.21 (MCC) not I50.9",
                clinical_evidence=f"EF={d.ef_value}%",
            ))
        else:
            sdx.append(CodeSuggestion(
                code="I50.9",
                description="Heart failure, unspecified",
                type="sdx",
                cc_mcc=None,
                confidence=0.70,
                reason="HF mentioned without EF value; request echo for CC/MCC upgrade",
                clinical_evidence="HF keyword found, no EF documented",
            ))

    # DM — CC optimization: HbA1c >7 or complication → E11.65 (CC) not E11.9
    if d.has_dm:
        if (d.hba1c_value is not None and d.hba1c_value > 7) or d.has_ckd:
            sdx.append(CodeSuggestion(
                code="E11.65",
                description="Type 2 DM with hyperglycemia",
                type="sdx",
                cc_mcc="CC",
                confidence=0.90,
                reason="DM with HbA1c >7 or complication → E11.65 (CC) not E11.9",
                clinical_evidence=_dm_evidence(d),
            ))
        else:
            # No HbA1c or complication evidence — use E11.9 (no CC).
            # Upgrading to E11.65 requires chart-documented HbA1c >7 or complication.
            sdx.append(CodeSuggestion(
                code="E11.9",
                description="Type 2 DM without complications",
                type="sdx",
                cc_mcc=None,
                confidence=0.85,
                reason="DM found but no HbA1c/complication evidence — use E11.9; upgrade to E11.65 only with chart proof",
                clinical_evidence=_dm_evidence(d),
            ))

    # CKD — CC/MCC based on eGFR
    if d.has_ckd or (d.egfr_value is not None and d.egfr_value < 60):
        if d.egfr_value is not None:
            if d.egfr_value < 15:
                sdx.append(CodeSuggestion(
                    code="N18.5",
                    description="Chronic kidney disease, stage 5",
                    type="sdx",
                    cc_mcc="MCC",
                    confidence=0.95,
                    reason=f"eGFR {d.egfr_value} (<15) = CKD stage 5 (MCC)",
                    clinical_evidence=f"eGFR={d.egfr_value}",
                ))
            elif d.egfr_value < 30:
                sdx.append(CodeSuggestion(
                    code="N18.4",
                    description="Chronic kidney disease, stage 4",
                    type="sdx",
                    cc_mcc="MCC",
                    confidence=0.95,
                    reason=f"eGFR {d.egfr_value} (15-29) = CKD stage 4 (MCC)",
                    clinical_evidence=f"eGFR={d.egfr_value}",
                ))
            elif d.egfr_value < 60:
                sdx.append(CodeSuggestion(
                    code="N18.3",
                    description="Chronic kidney disease, stage 3",
                    type="sdx",
                    cc_mcc="CC",
                    confidence=0.90,
                    reason=f"eGFR {d.egfr_value} (30-59) = CKD stage 3 (CC)",
                    clinical_evidence=f"eGFR={d.egfr_value}",
                ))
        else:
            # CKD mentioned without eGFR
            sdx.append(CodeSuggestion(
                code="N18.9",
                description="Chronic kidney disease, unspecified",
                type="sdx",
                cc_mcc=None,
                confidence=0.60,
                reason="CKD mentioned without eGFR; request labs for staging → CC/MCC",
                clinical_evidence="CKD keyword found, no eGFR documented",
            ))

    # AF — CC
    if d.has_af:
        sdx.append(CodeSuggestion(
            code="I48.91",
            description="Unspecified atrial fibrillation",
            type="sdx",
            cc_mcc="CC",
            confidence=0.85,
            reason="Atrial fibrillation = CC",
            clinical_evidence="AF keyword found",
        ))

    # HT — no CC/MCC impact but still code it
    if d.has_ht:
        sdx.append(CodeSuggestion(
            code="I10",
            description="Essential (primary) hypertension",
            type="sdx",
            cc_mcc=None,
            confidence=0.90,
            reason="HT should be coded; no CC/MCC impact but required for completeness",
            clinical_evidence="HT keyword found",
        ))

    # COPD — MCC only if acute exacerbation explicitly documented
    if d.has_copd:
        _copd_exacerbation_keywords = ("exacerbation", "acute", "exac", "กำเริบ", "อาการกำเริบ")
        has_exacerbation = any(
            kw in (d.raw_text or "").lower() for kw in _copd_exacerbation_keywords
        )
        if has_exacerbation:
            sdx.append(CodeSuggestion(
                code="J44.1",
                description="COPD with acute exacerbation",
                type="sdx",
                cc_mcc="MCC",
                confidence=0.85,
                reason="COPD with documented acute exacerbation → J44.1 (MCC)",
                clinical_evidence="COPD + exacerbation keywords found",
            ))
        else:
            sdx.append(CodeSuggestion(
                code="J44.0",
                description="COPD with acute lower respiratory infection",
                type="sdx",
                cc_mcc="CC",
                confidence=0.80,
                reason="COPD without exacerbation evidence — use J44.0 (CC); upgrade to J44.1 only with chart-documented acute exacerbation",
                clinical_evidence="COPD keyword found, no exacerbation documented",
            ))

    # Dyslipidemia — no CC/MCC impact
    if d.has_dyslipid:
        sdx.append(CodeSuggestion(
            code="E78.5",
            description="Dyslipidemia, unspecified",
            type="sdx",
            cc_mcc=None,
            confidence=0.85,
            reason="Dyslipidemia coded for completeness; no CC/MCC impact",
            clinical_evidence="Dyslipidemia keyword found",
        ))

    return sdx


def _dm_evidence(d: _ExtractedData) -> str:
    """Build evidence string for DM coding."""
    parts = ["DM keyword found"]
    if d.hba1c_value is not None:
        parts.append(f"HbA1c={d.hba1c_value}")
    if d.bs_value is not None:
        parts.append(f"blood sugar={d.bs_value}")
    if d.has_ckd:
        parts.append("CKD comorbidity (diabetic complication)")
    return "; ".join(parts)


def _determine_procedures(d: _ExtractedData) -> list[CodeSuggestion]:
    """Determine procedure codes from extracted data."""
    procs: list[CodeSuggestion] = []

    # PCI with stent
    if d.has_pci or d.has_stent or d.has_des or d.has_bms or d.has_balloon:
        if d.multi_vessel:
            procs.append(CodeSuggestion(
                code="36.05",
                description="PTCA multiple vessels",
                type="proc",
                confidence=0.90,
                reason="Multi-vessel PCI documented",
                clinical_evidence="Multi-vessel PCI keywords found",
            ))
        if d.has_des:
            procs.append(CodeSuggestion(
                code="36.07",
                description="Insertion of drug-eluting coronary stent (DES)",
                type="proc",
                confidence=0.95,
                reason="Drug-eluting stent insertion",
                clinical_evidence="DES keyword found",
            ))
        elif d.has_bms:
            procs.append(CodeSuggestion(
                code="36.06",
                description="Insertion of non-drug-eluting coronary stent (BMS)",
                type="proc",
                confidence=0.95,
                reason="Bare-metal stent insertion",
                clinical_evidence="BMS keyword found",
            ))
        elif d.has_stent:
            # Stent mentioned without DES/BMS specification — default to DES (most common)
            procs.append(CodeSuggestion(
                code="36.07",
                description="Insertion of drug-eluting coronary stent (DES)",
                type="proc",
                confidence=0.75,
                reason="Stent mentioned without DES/BMS specification; defaulting to DES (most common)",
                clinical_evidence="Stent keyword found",
            ))
        elif d.has_balloon and not d.has_stent and not d.has_des and not d.has_bms:
            procs.append(CodeSuggestion(
                code="36.01",
                description="PTCA single vessel without stent",
                type="proc",
                confidence=0.80,
                reason="Balloon angioplasty without stent",
                clinical_evidence="Balloon keyword found without stent",
            ))
        elif d.has_pci and not d.has_stent and not d.has_des and not d.has_bms:
            # PCI without stent detail
            procs.append(CodeSuggestion(
                code="36.01",
                description="PTCA single vessel without stent",
                type="proc",
                confidence=0.60,
                reason="PCI mentioned without stent detail; verify stent usage in chart",
                clinical_evidence="PCI keyword found",
            ))

    # Diagnostic cardiac catheterization
    if d.has_cath:
        procs.append(CodeSuggestion(
            code="37.22",
            description="Left heart catheterization",
            type="proc",
            confidence=0.90,
            reason="Cardiac catheterization (diagnostic)",
            clinical_evidence="Cath keyword found",
        ))

    # Coronary angiography — code alongside cath
    if d.has_angio or d.has_cath:
        procs.append(CodeSuggestion(
            code="88.56",
            description="Coronary arteriography using 2 catheters (Judkins)",
            type="proc",
            confidence=0.85 if d.has_angio else 0.75,
            reason="Coronary angiography (always code alongside diagnostic cath)",
            clinical_evidence="Angiography/cath keyword found",
        ))

    return procs


# ═══════════════════════════════════════════════
# Step 3: DRG Estimation
# ═══════════════════════════════════════════════

def _estimate_drg(
    pdx: CodeSuggestion,
    sdx: list[CodeSuggestion],
    procs: list[CodeSuggestion],
) -> tuple[str | None, float | None, float | None]:
    """Estimate DRG code based on PDx, SDx (CC/MCC), and procedures."""

    has_pci = any(p.code.startswith("36.0") for p in procs)
    has_stent = any(p.code in ("36.06", "36.07") for p in procs)
    has_cath_only = any(p.code in ("37.22", "88.56") for p in procs) and not has_pci
    is_multi_vessel = any(p.code == "36.05" for p in procs)
    is_acute_mi = pdx.code.startswith("I21.")

    # Determine CC/MCC level from SDx
    has_mcc = any(s.cc_mcc == "MCC" for s in sdx)
    has_cc = any(s.cc_mcc == "CC" for s in sdx)

    # CCC suffix: 0=no sig CCC, 1=min CCC, 2=mod CCC
    if has_mcc:
        ccc_suffix = "2"  # mod CCC (MCC present)
    elif has_cc:
        ccc_suffix = "1"  # min CCC
    else:
        ccc_suffix = "0"  # no sig CCC

    drg_code = None

    # Acute MI + PCI
    if is_acute_mi and has_pci:
        if is_multi_vessel:
            drg_code = f"0527{ccc_suffix}"
        else:
            drg_code = f"0529{ccc_suffix}"

    # Acute MI + no PCI (medical treatment)
    elif is_acute_mi and not has_pci:
        if has_cath_only:
            # Acute MI transferred (cath only, no PCI at this admission)
            drg_code = f"0569{ccc_suffix}"
        else:
            drg_code = f"0553{ccc_suffix}"

    # Non-acute + PCI with stent
    elif has_stent and not is_acute_mi:
        drg_code = f"0523{ccc_suffix}"

    # Non-acute + PCI without stent
    elif has_pci and not has_stent and not is_acute_mi:
        drg_code = f"0524{ccc_suffix}"

    # Diagnostic cath only
    elif has_cath_only:
        if pdx.code in ("I21.0", "I21.1", "I21.2", "I21.3", "I21.4", "I21.9"):
            drg_code = f"0521{ccc_suffix}"
        else:
            drg_code = f"0522{ccc_suffix}"

    # UA/angina medical
    elif pdx.code.startswith("I20."):
        drg_code = f"0559{ccc_suffix}"

    # Chronic IHD
    elif pdx.code.startswith("I25."):
        drg_code = f"0559{ccc_suffix}"

    # HF as PDx
    elif pdx.code.startswith("I50."):
        drg_code = f"0555{ccc_suffix}"

    # Lookup RW and payment — with fallback to nearby DRG
    if drg_code:
        drg_info = lookup_drg(drg_code)
        if drg_info:
            return drg_code, drg_info.rw, drg_info.payment_estimate_in_zone
        # Fallback: try lower complexity suffix (2→1→0)
        base = drg_code[:4]
        for suffix in ("1", "0", "2", "3", "4"):
            fallback = base + suffix
            if fallback != drg_code:
                drg_info = lookup_drg(fallback)
                if drg_info:
                    return drg_code, drg_info.rw, drg_info.payment_estimate_in_zone
        return drg_code, None, None

    return None, None, None


# ═══════════════════════════════════════════════
# Step 4: Generate optimization notes and warnings
# ═══════════════════════════════════════════════

def _generate_notes(
    d: _ExtractedData,
    pdx: CodeSuggestion,
    sdx: list[CodeSuggestion],
    procs: list[CodeSuggestion],
) -> tuple[list[str], list[str]]:
    """Generate optimization notes and warnings."""
    notes: list[str] = []
    warnings: list[str] = []

    # CC/MCC optimization notes
    mcc_codes = [s for s in sdx if s.cc_mcc == "MCC"]
    cc_codes = [s for s in sdx if s.cc_mcc == "CC"]
    if mcc_codes:
        notes.append(
            f"MCC found: {', '.join(s.code for s in mcc_codes)} — "
            f"DRG weight maximized"
        )
    if cc_codes:
        notes.append(
            f"CC found: {', '.join(s.code for s in cc_codes)} — "
            f"contributes to DRG weight"
        )

    # Suggest HF upgrade if EF available
    if d.has_hf and d.ef_value is None:
        notes.append(
            "Optimize: ขอ Echo report เพื่อระบุ EF → "
            "ถ้า EF <40% ใช้ I50.21 (MCC) แทน I50.9"
        )

    # Suggest DM upgrade
    if d.has_dm and d.hba1c_value is None:
        notes.append(
            "Optimize: ขอ HbA1c → ถ้า >7% ใช้ E11.65 (CC) มีหลักฐานรองรับ"
        )

    # Suggest CKD staging
    if d.has_ckd and d.egfr_value is None:
        notes.append(
            "Optimize: ขอ eGFR → ถ้า <30 ใช้ N18.4 (MCC), 30-59 ใช้ N18.3 (CC)"
        )

    # Diagnostic cath + PCI same day reminder
    has_pci_code = any(p.code.startswith("36.") for p in procs)
    has_cath_code = any(p.code in ("37.22", "88.56") for p in procs)
    if has_pci_code and has_cath_code:
        notes.append(
            "Code ทั้ง diagnostic (37.22+88.56) AND therapeutic (36.xx) — "
            "ไม่ bundle ใน Thai DRG"
        )

    # Warnings
    if pdx.confidence < 0.60:
        warnings.append(
            f"Low confidence PDx ({pdx.confidence:.0%}): "
            f"ข้อมูล clinical notes ไม่เพียงพอ — ตรวจสอบ chart"
        )

    if d.is_stemi and not any(p.code.startswith("36.") for p in procs):
        warnings.append(
            "STEMI without PCI: ถ้าไม่ได้ทำ PCI ต้อง document เหตุผล"
            " (contraindication, thrombolysis, transfer)"
        )

    if pdx.code == "I21.9":
        warnings.append(
            "Avoid I21.9 (unspecified MI): ควรระบุ wall (I21.0-I21.4)"
        )

    if any(s.code == "N18.9" for s in sdx):
        warnings.append(
            "N18.9 (CKD unspecified) ไม่ได้ CC/MCC: ขอ eGFR เพื่อ staging"
        )

    if any(s.code == "I50.9" for s in sdx):
        warnings.append(
            "I50.9 (HF unspecified) ไม่ได้ MCC: ขอ Echo เพื่อระบุ EF"
        )

    return notes, warnings


# ═══════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════

def auto_code(clinical_text: str) -> CodingResult:
    """Auto-generate ICD-10/ICD-9-CM codes from Thai/English clinical notes.

    Takes free-text clinical notes and returns:
    - PDx (principal diagnosis) with ICD-10
    - SDx (secondary diagnoses) with CC/MCC optimization
    - Procedures with ICD-9-CM
    - Expected DRG, RW, and payment estimate
    - Optimization notes and warnings

    Args:
        clinical_text: Free-text clinical notes in Thai or English.

    Returns:
        CodingResult with all coding suggestions and DRG estimate.
    """
    # Step 1: Extract clinical info
    extracted = _extract(clinical_text)

    # Step 2: Map to ICD codes
    pdx = _determine_pdx(extracted)
    sdx = _determine_sdx(extracted)
    procs = _determine_procedures(extracted)

    # Step 3: Estimate DRG
    drg_code, rw, payment = _estimate_drg(pdx, sdx, procs)

    # Step 4: Generate notes
    opt_notes, warnings = _generate_notes(extracted, pdx, sdx, procs)

    return CodingResult(
        pdx=pdx,
        sdx=sdx,
        procedures=procs,
        expected_drg=drg_code,
        expected_rw=rw,
        expected_payment=payment,
        optimization_notes=opt_notes,
        warnings=warnings,
    )
