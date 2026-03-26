"""Cath Lab Validator — 8 Checkpoints for pre-submission validation."""

import re
from datetime import datetime

from core.cathlab_models import (
    CathLabClaim, CheckpointResult, CheckResult, Optimization,
)
from core.drg_calculator import lookup_drg, calculate_payment, BASE_RATE_IN_ZONE

# ICD-10 cardiac Dx codes
ACUTE_MI_CODES = {"I210", "I211", "I212", "I213", "I214", "I219", "I21.0", "I21.1", "I21.2", "I21.3", "I21.4", "I21.9"}
STEMI_CODES = {"I210", "I211", "I212", "I213", "I21.0", "I21.1", "I21.2", "I21.3"}
NSTEMI_CODES = {"I214", "I21.4"}
UA_CODES = {"I200", "I20.0"}
CHRONIC_IHD_CODES = {"I251", "I250", "I25.0", "I25.1"}

# ICD-9-CM procedure codes
PCI_CODES = {"3601", "3602", "3605", "3606", "3607", "3609", "36.01", "36.02", "36.05", "36.06", "36.07", "36.09"}
CATH_CODES = {"3721", "3722", "3723", "37.21", "37.22", "37.23"}
ANGIO_CODES = {"8855", "8856", "8857", "88.55", "88.56", "88.57"}

# CC/MCC codes
MCC_CODES = {
    "A41": "Sepsis", "R652": "Severe sepsis",
    "J960": "Acute respiratory failure", "N17": "AKI",
    "I5021": "Acute systolic HF", "I5031": "Acute diastolic HF",
    "N184": "CKD stage 4", "J441": "COPD acute exacerbation",
}
CC_CODES = {
    "E112": "DM type 2 w renal", "E113": "DM type 2 w ophthalmic",
    "E114": "DM type 2 w neurological", "E115": "DM type 2 w peripheral circ",
    "E116": "DM type 2 w other", "E1165": "DM type 2 w hyperglycemia",
    "N183": "CKD stage 3", "I48": "Atrial fibrillation",
    "E87": "Electrolyte disorders", "D64": "Anemia",
}
NO_EFFECT_CODES = {"I10", "E785"}


def _normalize_code(code: str) -> str:
    return code.replace(".", "").strip().upper()


def _check_cid_checksum(cid: str) -> bool:
    if len(cid) != 13 or not cid.isdigit():
        return False
    total = sum(int(cid[i]) * (13 - i) for i in range(12))
    check_digit = (11 - (total % 11)) % 10
    return check_digit == int(cid[12])


def checkpoint_1_basic_data(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 1: Basic Data Validation."""
    issues = []

    if not claim.an:
        issues.append("ไม่มี AN")
    if not claim.hn:
        issues.append("ไม่มี HN")
    if not _check_cid_checksum(claim.pid):
        issues.append(f"CID {claim.pid} checksum ไม่ถูกต้อง")
    if not claim.principal_dx:
        issues.append("ไม่มี Principal Diagnosis (PDx) — DRG Error 1")
    if claim.discharge_date <= claim.admit_date:
        issues.append(f"วัน D/C ({claim.discharge_date}) ≤ วัน Admit ({claim.admit_date})")
    if not claim.procedures:
        issues.append("ไม่มี Procedure code (Cath Lab ควรมี)")

    if issues:
        return CheckpointResult(
            checkpoint=1, name="Basic Data",
            status="critical" if any("ไม่มี PDx" in i or "ไม่มี AN" in i for i in issues) else "warning",
            message=" | ".join(issues),
        )
    return CheckpointResult(checkpoint=1, name="Basic Data", status="pass", message="ข้อมูลพื้นฐานครบถ้วน")


def checkpoint_2_dx_proc_match(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 2: Diagnosis-Procedure Match."""
    pdx = _normalize_code(claim.principal_dx)
    procs = {_normalize_code(p) for p in claim.procedures}
    issues = []

    has_pci = bool(procs & PCI_CODES)
    has_cath = bool(procs & CATH_CODES)
    is_acute_mi = any(pdx.startswith(c.replace(".", "")) for c in ACUTE_MI_CODES)
    is_stemi = any(pdx.startswith(c.replace(".", "")) for c in STEMI_CODES)
    is_ua = any(pdx.startswith(c.replace(".", "")) for c in UA_CODES)
    is_chronic = any(pdx.startswith(c.replace(".", "")) for c in CHRONIC_IHD_CODES)

    if is_acute_mi and not has_pci and not has_cath:
        issues.append(f"PDx {claim.principal_dx} (Acute MI) แต่ไม่มี PCI/Cath procedure → DRG จะเป็น medical MI (RW ต่ำมาก)")

    if has_pci and is_chronic and not is_acute_mi:
        issues.append(f"PCI procedure แต่ PDx {claim.principal_dx} (Chronic IHD) → DRG เป็น PTCA wo CCC (RW ต่ำกว่า Acute MI + PCI)")

    if has_pci and is_ua:
        issues.append(f"PCI procedure แต่ PDx {claim.principal_dx} (UA) → ถ้า Troponin สูง ควรเปลี่ยนเป็น I21.4 (NSTEMI) เพื่อ DRG ที่ถูกต้อง")

    if is_stemi and has_pci and not has_cath:
        issues.append("STEMI + PCI แต่ไม่มี diagnostic cath code (37.22/88.56) → ควรเพิ่ม")

    if not issues:
        msg = f"PDx {claim.principal_dx} สอดคล้องกับ Procedures {claim.procedures}"
        return CheckpointResult(checkpoint=2, name="Dx-Proc Match", status="pass", message=msg)

    return CheckpointResult(
        checkpoint=2, name="Dx-Proc Match",
        status="critical" if any("RW ต่ำมาก" in i for i in issues) else "warning",
        message=" | ".join(issues),
    )


def checkpoint_3_device_docs(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 3: Device Documentation (Stent)."""
    issues = []

    if not claim.devices and claim.inst_amount > 0:
        issues.append(f"มีค่า INST {claim.inst_amount:,.0f} บาท แต่ไม่มีข้อมูล devices ใน ADP file")

    for dev in claim.devices:
        if dev.type not in (3, 4, 5):
            issues.append(f"Device TYPE {dev.type} ไม่ถูกต้อง (ต้อง 3/4/5)")
        if not dev.serial_no:
            issues.append(f"Device {dev.code} ไม่มี Serial/Lot number (ต้องตรง GPO VMI)")
        if dev.qty <= 0:
            issues.append(f"Device {dev.code} qty={dev.qty} ไม่ถูกต้อง")

    if not issues:
        return CheckpointResult(checkpoint=3, name="Device Docs", status="pass", message="เอกสารอุปกรณ์ครบถ้วน")

    return CheckpointResult(
        checkpoint=3, name="Device Docs",
        status="critical" if "ไม่มีข้อมูล devices" in " ".join(issues) else "warning",
        message=" | ".join(issues),
    )


def checkpoint_4_file_completeness(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 4: 16-File Completeness."""
    issues = []
    if not claim.principal_dx:
        issues.append("DIA file: ไม่มี PDx (DXTYPE=1)")
    if not claim.procedures:
        issues.append("OPR file: ไม่มี Procedure codes")
    if claim.charge_amount <= 0:
        issues.append("CHA file: ยอดค่ารักษา = 0")
    if not claim.fund:
        issues.append("INS file: ไม่ระบุสิทธิ")

    if not issues:
        return CheckpointResult(checkpoint=4, name="16-File Completeness", status="pass", message="ข้อมูล 16 แฟ้มครบ")
    return CheckpointResult(checkpoint=4, name="16-File Completeness", status="warning", message=" | ".join(issues))


def checkpoint_5_timing(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 5: Timing & Authorization."""
    issues = []
    days = claim.days_since_discharge

    if days > 30:
        issues.append(f"ส่งข้อมูลเกิน 30 วัน ({days} วัน) → ถูกปรับลดอัตราจ่ายหรือ reject")
    elif days > 25:
        issues.append(f"เหลือเวลาส่ง {30 - days} วัน — ควรส่งด่วน!")

    if claim.fund == "UCS" and not claim.authen_code:
        issues.append("สิทธิ UC แต่ไม่มี Authen Code")

    if not issues:
        status = "pass"
        los = claim.los
        if los <= 1:
            msg = f"LOS={los} วัน (≤24 ชม. = fast track) | ส่งได้ภายใน {30 - days} วัน"
        else:
            msg = f"LOS={los} วัน | ส่งได้ภายใน {30 - days} วัน"
        return CheckpointResult(checkpoint=5, name="Timing & Auth", status=status, message=msg)

    return CheckpointResult(
        checkpoint=5, name="Timing & Auth",
        status="critical" if days > 30 else "warning",
        message=" | ".join(issues),
    )


def checkpoint_6_ccmcc(claim: CathLabClaim) -> tuple[CheckpointResult, list[Optimization]]:
    """Checkpoint 6: CC/MCC Optimization."""
    all_dx = {_normalize_code(claim.principal_dx)} | {_normalize_code(d) for d in claim.secondary_dx}
    optimizations = []

    has_mcc = any(any(dx.startswith(c.replace(".", "")) for c in MCC_CODES) for dx in all_dx)

    if not has_mcc:
        for code, desc in MCC_CODES.items():
            norm = code.replace(".", "")
            if not any(dx.startswith(norm) for dx in all_dx):
                if norm == "I5021":
                    optimizations.append(Optimization(
                        suggested_code="I50.21", reason=f"ถ้า EF <40% → เพิ่ม {desc} (MCC)",
                        clinical_evidence="ดู Echo EF%", rw_impact=2.8, money_impact=round(2.8 * BASE_RATE_IN_ZONE),
                    ))
                elif norm == "N184":
                    optimizations.append(Optimization(
                        suggested_code="N18.4", reason=f"ถ้า eGFR 15-29 → เพิ่ม {desc} (MCC)",
                        clinical_evidence="ดู Cr/eGFR", rw_impact=2.8, money_impact=round(2.8 * BASE_RATE_IN_ZONE),
                    ))

    for dx in all_dx:
        if dx.startswith("E119"):
            optimizations.append(Optimization(
                current_code="E11.9", suggested_code="E11.65",
                reason="DM unspecified → เปลี่ยนเป็น DM w hyperglycemia (CC)",
                clinical_evidence="ดู blood sugar", rw_impact=0.5, money_impact=round(0.5 * BASE_RATE_IN_ZONE),
            ))
        if dx.startswith("I509"):
            optimizations.append(Optimization(
                current_code="I50.9", suggested_code="I50.21/I50.31",
                reason="HF unspecified → ระบุ systolic/diastolic + acute/chronic",
                clinical_evidence="ดู Echo EF%", rw_impact=2.0, money_impact=round(2.0 * BASE_RATE_IN_ZONE),
            ))

    if optimizations:
        total = sum(o.money_impact for o in optimizations[:1])
        msg = f"พบ {len(optimizations)} optimization(s) เพิ่มเงินได้ ~{total:,.0f} บาท"
        return CheckpointResult(checkpoint=6, name="CC/MCC Optimization", status="pass", message=msg), optimizations

    return CheckpointResult(checkpoint=6, name="CC/MCC Optimization", status="pass", message="CC/MCC ครบถ้วน"), []


def checkpoint_7_drg_verify(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 7: DRG Verification."""
    if not claim.drg:
        return CheckpointResult(checkpoint=7, name="DRG Verification", status="warning", message="ไม่มี DRG code ให้ตรวจ")

    drg_info = lookup_drg(claim.drg)
    if not drg_info:
        return CheckpointResult(
            checkpoint=7, name="DRG Verification", status="warning",
            message=f"DRG {claim.drg} ไม่อยู่ใน cardiac RW table (อาจเป็น MDC อื่น)",
        )

    issues = []
    if claim.rw and abs(claim.rw - drg_info.rw) > 0.01:
        issues.append(f"RW claim ({claim.rw}) ≠ RW table ({drg_info.rw})")

    if claim.los > drg_info.ot:
        issues.append(f"LOS {claim.los} > OT {drg_info.ot} (outlier ยาว — ได้ per diem เพิ่ม)")

    msg = f"DRG {claim.drg}: {drg_info.description} | RW={drg_info.rw} | WtLOS={drg_info.wtlos} | OT={drg_info.ot}"
    if issues:
        msg += " | " + " | ".join(issues)

    return CheckpointResult(
        checkpoint=7, name="DRG Verification", status="pass" if not issues else "warning",
        message=msg,
        details={"drg_info": drg_info.model_dump()},
    )


def checkpoint_8_drug_lab(claim: CathLabClaim) -> CheckpointResult:
    """Checkpoint 8: Drug/Lab Catalog Match."""
    issues = []

    if not claim.drugs and claim.charge_amount > 10000:
        issues.append("ค่ารักษาสูงแต่ไม่มีข้อมูลยา (DRU file)")

    for drug in claim.drugs:
        if not drug.did:
            issues.append(f"ยา {drug.name} ไม่มี TMT/GPUID code")

    if "CLOPIDOGREL_DRUG" in claim.denied_items:
        issues.append("Clopidogrel ถูก deny — ตรวจ TMT code ตรง Drug Catalog หรือไม่")

    if not issues:
        return CheckpointResult(checkpoint=8, name="Drug/Lab Catalog", status="pass", message="Drug/Lab catalog ถูกต้อง")

    return CheckpointResult(checkpoint=8, name="Drug/Lab Catalog", status="warning", message=" | ".join(issues))


def validate_cathlab_claim(claim: CathLabClaim) -> CheckResult:
    """Run all 8 checkpoints on a Cath Lab claim."""
    checkpoints = []
    auto_fixes = []
    optimizations = []
    warnings = []
    errors = []

    # Run checkpoints
    cp1 = checkpoint_1_basic_data(claim)
    checkpoints.append(cp1)

    cp2 = checkpoint_2_dx_proc_match(claim)
    checkpoints.append(cp2)

    cp3 = checkpoint_3_device_docs(claim)
    checkpoints.append(cp3)

    cp4 = checkpoint_4_file_completeness(claim)
    checkpoints.append(cp4)

    cp5 = checkpoint_5_timing(claim)
    checkpoints.append(cp5)

    cp6, opts = checkpoint_6_ccmcc(claim)
    checkpoints.append(cp6)
    optimizations = opts

    cp7 = checkpoint_7_drg_verify(claim)
    checkpoints.append(cp7)

    cp8 = checkpoint_8_drug_lab(claim)
    checkpoints.append(cp8)

    # Calculate score
    critical_count = sum(1 for cp in checkpoints if cp.status == "critical")
    warning_count = sum(1 for cp in checkpoints if cp.status == "warning")
    opt_count = len(optimizations)

    score = 100 - (critical_count * 20) - (warning_count * 5) + (opt_count * 2)
    score = max(0, min(100, score))

    if critical_count > 0:
        status = "critical"
    elif warning_count > 0:
        status = "warning"
    else:
        status = "pass"

    for cp in checkpoints:
        if cp.status == "critical":
            errors.append(f"CP{cp.checkpoint} {cp.name}: {cp.message}")
        elif cp.status == "warning":
            warnings.append(f"CP{cp.checkpoint} {cp.name}: {cp.message}")

    # DRG/payment estimate
    drg_info = lookup_drg(claim.drg) if claim.drg else None
    expected_rw = drg_info.rw if drg_info else claim.rw
    expected_payment = round(expected_rw * BASE_RATE_IN_ZONE, 2) if expected_rw else None

    return CheckResult(
        an=claim.an,
        score=score,
        status=status,
        checkpoints=checkpoints,
        optimizations=optimizations,
        auto_fixes_applied=auto_fixes,
        expected_drg=claim.drg,
        expected_rw=expected_rw,
        expected_payment=expected_payment,
        warnings=warnings,
        errors=errors,
    )
