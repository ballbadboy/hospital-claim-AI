"""Deny Predictor — Predicts claim denial probability BEFORE submission.

Analyzes 10 risk factors and produces a weighted probability score (0-100%)
with verdict: SAFE / CAUTION / HIGH_RISK / ALMOST_CERTAIN.
"""

import re
from datetime import datetime

from pydantic import BaseModel, Field

from core.cathlab_models import CathLabClaim
from core.cathlab_validator import (
    _normalize_code, _check_cid_checksum,
    ACUTE_MI_CODES, STEMI_CODES, NSTEMI_CODES, UA_CODES, CHRONIC_IHD_CODES,
    PCI_CODES, CATH_CODES, ANGIO_CODES,
    MCC_CODES, CC_CODES, NO_EFFECT_CODES,
)
from core.drg_calculator import lookup_drg, BASE_RATE_IN_ZONE, CARDIAC_DRG_TABLE


# ═══════════════════════════════════════════════
# Output Models
# ═══════════════════════════════════════════════

class RiskFactor(BaseModel):
    name: str
    status: str = Field(description="pass/fail/warning")
    weight: int
    risk_score: int = Field(ge=0, le=100, description="0-100 risk for this factor")
    detail: str


class DenyPrediction(BaseModel):
    an: str
    deny_probability: float = Field(ge=0, le=1, description="0.0-1.0")
    verdict: str = Field(description="SAFE/CAUTION/HIGH_RISK/ALMOST_CERTAIN")
    risk_factors: list[RiskFactor]
    top_risks: list[str]
    estimated_loss_if_denied: float
    recommendation: str


# ═══════════════════════════════════════════════
# Known drug names for catalog matching (RF5)
# ═══════════════════════════════════════════════

KNOWN_CATH_DRUGS = {
    "clopidogrel", "aspirin", "ticagrelor", "prasugrel",
    "heparin", "enoxaparin", "bivalirudin",
    "atorvastatin", "rosuvastatin",
    "nitroglycerin", "morphine", "metoprolol",
    "alteplase", "tenecteplase", "reteplase",
    "eptifibatide", "tirofiban", "abciximab",
    "dopamine", "dobutamine", "norepinephrine",
}

# ICD-10 patterns that are valid cardiac PDx
VALID_CARDIAC_PDX_PREFIXES = (
    "I20", "I21", "I22", "I23", "I24", "I25",
    "I26", "I27", "I28",
    "I30", "I31", "I32", "I33", "I34", "I35", "I36", "I37", "I38",
    "I40", "I41", "I42", "I43", "I44", "I45", "I46", "I47", "I48", "I49",
    "I50", "I51",
    "I60", "I61", "I62", "I63", "I64", "I65", "I66", "I67", "I68", "I69",
    "I70", "I71", "I72", "I73", "I74", "I77", "I78", "I79",
    "I80", "I81", "I82", "I83", "I84", "I85", "I86", "I87",
)


# ═══════════════════════════════════════════════
# Risk Factor Evaluators
# ═══════════════════════════════════════════════

def _rf1_cid_checksum(claim: CathLabClaim) -> RiskFactor:
    """RF1: CID checksum valid? (weight: 5)"""
    valid = _check_cid_checksum(claim.pid)
    if valid:
        return RiskFactor(
            name="RF1: CID Checksum",
            status="pass", weight=5, risk_score=0,
            detail=f"CID {claim.pid} checksum ถูกต้อง",
        )
    return RiskFactor(
        name="RF1: CID Checksum",
        status="fail", weight=5, risk_score=100,
        detail=f"CID {claim.pid} checksum ไม่ถูกต้อง — claim จะถูก reject ทันที",
    )


def _rf2_pdx_valid(claim: CathLabClaim) -> RiskFactor:
    """RF2: PDx exists and valid ICD-10? (weight: 15)"""
    if not claim.principal_dx or claim.principal_dx.strip() == "":
        return RiskFactor(
            name="RF2: PDx Valid",
            status="fail", weight=15, risk_score=100,
            detail="ไม่มี Principal Diagnosis — DRG Error 1 (deny แน่นอน)",
        )

    pdx = _normalize_code(claim.principal_dx)

    # Check basic ICD-10 format: letter + digits
    if not re.match(r"^[A-Z]\d{2,5}$", pdx):
        return RiskFactor(
            name="RF2: PDx Valid",
            status="fail", weight=15, risk_score=90,
            detail=f"PDx '{claim.principal_dx}' ไม่ตรงรูปแบบ ICD-10 (ต้องขึ้นต้นด้วยตัวอักษร ตามด้วยตัวเลข)",
        )

    return RiskFactor(
        name="RF2: PDx Valid",
        status="pass", weight=15, risk_score=0,
        detail=f"PDx {claim.principal_dx} รูปแบบ ICD-10 ถูกต้อง",
    )


def _rf3_dx_proc_match(claim: CathLabClaim) -> RiskFactor:
    """RF3: Dx-Proc match? STEMI needs PCI code, PCI needs acute Dx. (weight: 20)"""
    pdx = _normalize_code(claim.principal_dx) if claim.principal_dx else ""
    procs = {_normalize_code(p) for p in claim.procedures}

    has_pci = bool(procs & PCI_CODES)
    has_cath = bool(procs & CATH_CODES)
    has_angio = bool(procs & ANGIO_CODES)
    is_acute_mi = any(pdx.startswith(c.replace(".", "")) for c in ACUTE_MI_CODES)
    is_stemi = any(pdx.startswith(c.replace(".", "")) for c in STEMI_CODES)
    is_chronic = any(pdx.startswith(c.replace(".", "")) for c in CHRONIC_IHD_CODES)

    issues = []

    # STEMI/Acute MI without PCI — major mismatch for Cath Lab claim
    if is_acute_mi and not has_pci and not has_cath:
        issues.append(f"PDx {claim.principal_dx} (Acute MI) ไม่มี PCI/Cath procedure — DRG จะเป็น medical MI (RW ต่ำมาก)")

    # PCI without acute diagnosis
    if has_pci and is_chronic and not is_acute_mi:
        issues.append(f"PCI procedure + Chronic IHD PDx ({claim.principal_dx}) — DRG ต่ำกว่า Acute MI + PCI")

    # No procedures at all for Cath Lab claim
    if not procs:
        issues.append("ไม่มี Procedure code เลย — Cath Lab claim ต้องมี")

    if not issues:
        return RiskFactor(
            name="RF3: Dx-Proc Match",
            status="pass", weight=20, risk_score=0,
            detail=f"PDx {claim.principal_dx} สอดคล้องกับ procedures {claim.procedures}",
        )

    severity = 90 if "ไม่มี Procedure" in " ".join(issues) else 70
    return RiskFactor(
        name="RF3: Dx-Proc Match",
        status="fail", weight=20, risk_score=severity,
        detail=" | ".join(issues),
    )


def _rf4_device_docs(claim: CathLabClaim) -> RiskFactor:
    """RF4: Device docs complete? (serial, lot, TYPE, CODE) (weight: 15)"""
    issues = []

    # Has INST charges but no device records
    if not claim.devices and claim.inst_amount > 0:
        return RiskFactor(
            name="RF4: Device Docs",
            status="fail", weight=15, risk_score=90,
            detail=f"ค่า INST {claim.inst_amount:,.0f} บาท แต่ไม่มีข้อมูล devices (ADP file) — ถูก deny ค่าอุปกรณ์แน่นอน",
        )

    for dev in claim.devices:
        if dev.type not in (3, 4, 5):
            issues.append(f"Device {dev.code} TYPE={dev.type} ไม่ถูกต้อง")
        if not dev.serial_no:
            issues.append(f"Device {dev.code} ไม่มี Serial/Lot")
        if not dev.code:
            issues.append("Device ไม่มี CODE สปสช.")

    # PCI procedures should have stent devices
    procs = {_normalize_code(p) for p in claim.procedures}
    has_pci = bool(procs & PCI_CODES)
    if has_pci and not claim.devices:
        issues.append("PCI procedure แต่ไม่มีข้อมูล stent device — ค่า stent อาจถูก deny")

    if not issues:
        return RiskFactor(
            name="RF4: Device Docs",
            status="pass", weight=15, risk_score=0,
            detail=f"เอกสารอุปกรณ์ครบถ้วน ({len(claim.devices)} devices)",
        )

    risk = min(90, 30 + len(issues) * 20)
    return RiskFactor(
        name="RF4: Device Docs",
        status="fail" if risk >= 60 else "warning", weight=15, risk_score=risk,
        detail=" | ".join(issues),
    )


def _rf5_drug_catalog(claim: CathLabClaim) -> RiskFactor:
    """RF5: Drug catalog likely match? (weight: 10)"""
    issues = []

    # No drugs but significant charge
    if not claim.drugs and claim.charge_amount > 10000:
        issues.append("ค่ารักษาสูงแต่ไม่มีข้อมูลยา (DRU file)")

    # Check drugs have TMT/GPUID
    for drug in claim.drugs:
        if not drug.did:
            issues.append(f"ยา {drug.name or 'unknown'} ไม่มี TMT/GPUID code")

    # Previously denied drug items
    if "CLOPIDOGREL_DRUG" in claim.denied_items:
        issues.append("Clopidogrel เคยถูก deny — TMT code อาจไม่ตรง Drug Catalog")

    if not issues:
        return RiskFactor(
            name="RF5: Drug Catalog",
            status="pass", weight=10, risk_score=0,
            detail="Drug catalog match OK",
        )

    risk = min(80, 30 + len(issues) * 25)
    return RiskFactor(
        name="RF5: Drug Catalog",
        status="fail" if risk >= 50 else "warning", weight=10, risk_score=risk,
        detail=" | ".join(issues),
    )


def _rf6_timing(claim: CathLabClaim) -> RiskFactor:
    """RF6: Timing within 30 days? (weight: 10)"""
    days = claim.days_since_discharge

    if days > 30:
        return RiskFactor(
            name="RF6: Timing",
            status="fail", weight=10, risk_score=90,
            detail=f"เกินกำหนดส่ง 30 วัน (ผ่านมาแล้ว {days} วัน) — ถูกปรับลดหรือ reject",
        )
    elif days > 25:
        return RiskFactor(
            name="RF6: Timing",
            status="warning", weight=10, risk_score=40,
            detail=f"เหลือเวลาส่ง {30 - days} วัน — ควรส่งด่วน",
        )
    else:
        return RiskFactor(
            name="RF6: Timing",
            status="pass", weight=10, risk_score=0,
            detail=f"ยังอยู่ในกำหนด (เหลือ {max(30 - days, 0)} วัน)",
        )


def _rf7_authen_code(claim: CathLabClaim) -> RiskFactor:
    """RF7: Authen code present for UC? (weight: 10)"""
    if claim.fund != "UCS":
        return RiskFactor(
            name="RF7: Authen Code",
            status="pass", weight=10, risk_score=0,
            detail=f"สิทธิ {claim.fund} ไม่ต้องใช้ Authen Code",
        )

    if claim.authen_code:
        return RiskFactor(
            name="RF7: Authen Code",
            status="pass", weight=10, risk_score=0,
            detail=f"Authen Code: {claim.authen_code}",
        )

    return RiskFactor(
        name="RF7: Authen Code",
        status="fail", weight=10, risk_score=80,
        detail="สิทธิ UC แต่ไม่มี Authen Code — claim จะถูก reject",
    )


def _rf8_ccmcc_coding(claim: CathLabClaim) -> RiskFactor:
    """RF8: CC/MCC coded properly? (E11.9 vs E11.65, I50.9 vs I50.21) (weight: 5)"""
    all_dx = {_normalize_code(claim.principal_dx)} if claim.principal_dx else set()
    all_dx |= {_normalize_code(d) for d in claim.secondary_dx}

    issues = []
    optimizations = []

    # Check for unspecified codes that should be more specific
    for dx in all_dx:
        if dx.startswith("E119"):
            issues.append("E11.9 (DM unspecified) → ควรเป็น E11.65 (DM w hyperglycemia) เพื่อได้ CC")
            optimizations.append("E11.9 → E11.65")
        if dx.startswith("I509"):
            issues.append("I50.9 (HF unspecified) → ควรระบุ I50.21/I50.31 (systolic/diastolic) เพื่อได้ MCC")
            optimizations.append("I50.9 → I50.21/I50.31")

    # Check if any secondary Dx adds value
    has_cc_or_mcc = False
    for dx in all_dx:
        if any(dx.startswith(c.replace(".", "")) for c in MCC_CODES):
            has_cc_or_mcc = True
            break
        if any(dx.startswith(c.replace(".", "")) for c in CC_CODES):
            has_cc_or_mcc = True
            break

    # Only no-effect codes as secondary
    all_secondary = {_normalize_code(d) for d in claim.secondary_dx}
    only_no_effect = all_secondary and all(
        any(dx.startswith(c.replace(".", "")) for c in NO_EFFECT_CODES)
        for dx in all_secondary
    )
    if only_no_effect and not has_cc_or_mcc:
        issues.append("Secondary Dx ทั้งหมดเป็น no-effect codes (I10, E78.5) — ไม่ช่วยเพิ่ม DRG weight")

    if not issues:
        return RiskFactor(
            name="RF8: CC/MCC Coding",
            status="pass", weight=5, risk_score=0,
            detail="CC/MCC coding สมบูรณ์",
        )

    # Not a deny risk per se, but missed revenue
    risk = min(60, 20 + len(issues) * 15)
    return RiskFactor(
        name="RF8: CC/MCC Coding",
        status="warning", weight=5, risk_score=risk,
        detail=" | ".join(issues),
    )


def _rf9_drg_groupable(claim: CathLabClaim) -> RiskFactor:
    """RF9: DRG groupable? (no Error 1-9) (weight: 5)"""
    if not claim.principal_dx or claim.principal_dx.strip() == "":
        return RiskFactor(
            name="RF9: DRG Groupable",
            status="fail", weight=5, risk_score=100,
            detail="ไม่มี PDx — DRG Error 1 (group ไม่ได้)",
        )

    if not claim.procedures:
        # Medical DRG still possible, but for Cath Lab this is unusual
        return RiskFactor(
            name="RF9: DRG Groupable",
            status="warning", weight=5, risk_score=50,
            detail="ไม่มี Procedure — จะ group เป็น medical DRG (ไม่ใช่ surgical)",
        )

    if claim.drg:
        drg_info = lookup_drg(claim.drg)
        if drg_info:
            return RiskFactor(
                name="RF9: DRG Groupable",
                status="pass", weight=5, risk_score=0,
                detail=f"DRG {claim.drg}: {drg_info.description} (RW={drg_info.rw})",
            )
        else:
            # DRG exists but not in our cardiac table — still groupable
            return RiskFactor(
                name="RF9: DRG Groupable",
                status="pass", weight=5, risk_score=10,
                detail=f"DRG {claim.drg} ไม่อยู่ใน cardiac table แต่ยัง group ได้",
            )

    # No DRG assigned yet — check if data is sufficient
    return RiskFactor(
        name="RF9: DRG Groupable",
        status="warning", weight=5, risk_score=30,
        detail="ยังไม่ได้ assign DRG — ควรรัน grouper ก่อนส่ง",
    )


def _rf10_charge_reasonable(claim: CathLabClaim) -> RiskFactor:
    """RF10: Charge amount reasonable for DRG? (weight: 5)"""
    if not claim.drg:
        return RiskFactor(
            name="RF10: Charge Reasonable",
            status="warning", weight=5, risk_score=20,
            detail="ไม่มี DRG ให้เปรียบเทียบค่ารักษา",
        )

    drg_info = lookup_drg(claim.drg)
    if not drg_info:
        return RiskFactor(
            name="RF10: Charge Reasonable",
            status="pass", weight=5, risk_score=10,
            detail=f"DRG {claim.drg} ไม่อยู่ใน cardiac table — ไม่สามารถประเมินความสมเหตุสมผล",
        )

    expected_payment = drg_info.rw * BASE_RATE_IN_ZONE
    charge = claim.charge_amount

    if charge <= 0:
        return RiskFactor(
            name="RF10: Charge Reasonable",
            status="fail", weight=5, risk_score=80,
            detail="ค่ารักษา = 0 บาท — ผิดปกติ",
        )

    # Charge significantly less than expected payment suggests missing items
    ratio = charge / expected_payment if expected_payment > 0 else 0

    if ratio < 0.3:
        return RiskFactor(
            name="RF10: Charge Reasonable",
            status="warning", weight=5, risk_score=40,
            detail=f"ค่ารักษา {charge:,.0f} บาท ต่ำกว่า expected payment {expected_payment:,.0f} บาท มาก (ratio={ratio:.2f}) — อาจขาดรายการ",
        )
    elif ratio > 3.0:
        return RiskFactor(
            name="RF10: Charge Reasonable",
            status="warning", weight=5, risk_score=30,
            detail=f"ค่ารักษา {charge:,.0f} บาท สูงกว่า expected payment {expected_payment:,.0f} บาท มาก (ratio={ratio:.2f})",
        )

    return RiskFactor(
        name="RF10: Charge Reasonable",
        status="pass", weight=5, risk_score=0,
        detail=f"ค่ารักษา {charge:,.0f} บาท สมเหตุสมผลกับ DRG {claim.drg} (expected ~{expected_payment:,.0f} บาท)",
    )


# ═══════════════════════════════════════════════
# Main Predictor
# ═══════════════════════════════════════════════

def predict_deny(claim: CathLabClaim) -> DenyPrediction:
    """Predict whether a claim will be denied BEFORE submission.

    Analyzes 10 risk factors, each with a weight, and returns
    a weighted probability score with verdict.
    """
    # Evaluate all 10 risk factors
    risk_factors = [
        _rf1_cid_checksum(claim),
        _rf2_pdx_valid(claim),
        _rf3_dx_proc_match(claim),
        _rf4_device_docs(claim),
        _rf5_drug_catalog(claim),
        _rf6_timing(claim),
        _rf7_authen_code(claim),
        _rf8_ccmcc_coding(claim),
        _rf9_drg_groupable(claim),
        _rf10_charge_reasonable(claim),
    ]

    # Calculate weighted deny probability
    # Hybrid scoring: weighted average of FAILED factors only (not diluted by passing ones)
    # plus a compound penalty when multiple critical issues exist simultaneously.
    #
    # Rationale: in NHSO claims, a single critical failure (e.g., no devices, no authen code)
    # is enough to deny the claim. Multiple failures compound the risk.

    total_weight = sum(rf.weight for rf in risk_factors)
    failed = [rf for rf in risk_factors if rf.status in ("fail", "warning")]
    critical_fails = [rf for rf in risk_factors if rf.status == "fail"]

    # Base: weighted average across ALL factors
    weighted_risk = sum(rf.weight * rf.risk_score for rf in risk_factors)
    base_probability = weighted_risk / (total_weight * 100) if total_weight > 0 else 0.0

    # Max weighted risk: the highest weight-adjusted single-factor risk.
    # Uses weight as a scaling factor so high-weight fails matter more.
    max_weighted_risk = max(
        (rf.risk_score * rf.weight / (total_weight) for rf in risk_factors),
        default=0.0,
    ) / 100 * total_weight  # normalize back: a weight-20 factor at 100 = 0.20

    # Compound penalty: multiple critical fails increase risk
    # Each critical fail adds 5% (e.g., 3 critical fails = +15%)
    compound_bonus = min(0.25, len(critical_fails) * 0.05)

    # Final: blend base average (50%) with max-weighted-risk (30%) + compound (up to 25%)
    deny_probability = (base_probability * 0.50) + (max_weighted_risk * 0.30) + compound_bonus
    deny_probability = max(0.0, min(1.0, deny_probability))

    # Determine verdict
    pct = deny_probability * 100
    if pct < 20:
        verdict = "SAFE"
    elif pct < 50:
        verdict = "CAUTION"
    elif pct < 80:
        verdict = "HIGH_RISK"
    else:
        verdict = "ALMOST_CERTAIN"

    # Top risks: sorted by risk_score descending, only non-pass
    failed_factors = [rf for rf in risk_factors if rf.status != "pass"]
    failed_factors.sort(key=lambda rf: rf.risk_score * rf.weight, reverse=True)
    top_risks = [f"{rf.name}: {rf.detail}" for rf in failed_factors[:5]]

    # Estimated loss if denied
    if claim.expected_payment:
        estimated_loss = claim.expected_payment
    elif claim.drg:
        drg_info = lookup_drg(claim.drg)
        if drg_info:
            estimated_loss = drg_info.rw * BASE_RATE_IN_ZONE
        else:
            estimated_loss = claim.charge_amount
    else:
        estimated_loss = claim.charge_amount

    # Recommendation
    if verdict == "SAFE":
        recommendation = "ส่งเบิกได้เลย — ความเสี่ยงต่ำ"
    elif verdict == "CAUTION":
        fixes = [rf.name.split(": ")[1] for rf in failed_factors[:3]]
        recommendation = f"แก้ไขก่อนส่ง: {', '.join(fixes)}" if fixes else "ตรวจสอบอีกครั้งก่อนส่ง"
    elif verdict == "HIGH_RISK":
        fixes = [rf.name.split(": ")[1] for rf in failed_factors[:3]]
        recommendation = f"ห้ามส่งก่อนแก้ไข! ปัญหาหลัก: {', '.join(fixes)}"
    else:
        recommendation = "อย่าส่ง! ต้องแก้ไขข้อมูลพื้นฐานให้ครบก่อน — claim จะถูก deny แน่นอน"

    return DenyPrediction(
        an=claim.an,
        deny_probability=round(deny_probability, 4),
        verdict=verdict,
        risk_factors=risk_factors,
        top_risks=top_risks,
        estimated_loss_if_denied=round(estimated_loss, 2),
        recommendation=recommendation,
    )
