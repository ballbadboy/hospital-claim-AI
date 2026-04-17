"""
Rule Engine — Deterministic validation checks (no AI needed).
Runs in <1 second. Catches format errors, missing data, timing issues.
"""

import logging
from datetime import datetime, timedelta
from core.models import ClaimInput, CheckResult, Severity, Department, Fund

logger = logging.getLogger(__name__)

# ICD-10 cardiac codes
STEMI_CODES = {"I21.0", "I21.1", "I21.2", "I21.3"}
NSTEMI_CODES = {"I21.4"}
UA_CODES = {"I20.0"}
CHRONIC_IHD_CODES = {"I25.0", "I25.1", "I25.10", "I25.11", "I25.2", "I25.5"}
AMI_CODES = STEMI_CODES | NSTEMI_CODES

# ICD-9-CM procedure codes
PCI_CODES = {"36.01", "36.02", "36.05", "36.06", "36.07", "36.09"}
STENT_CODES = {"36.06", "36.07"}
DIAG_CATH_CODES = {"37.21", "37.22", "37.23"}
ANGIO_CODES = {"88.55", "88.56", "88.57"}
VENTILATOR_CODES = {"96.71", "96.72"}
HD_CODES = {"39.95"}
CAPD_CODES = {"54.98"}
CHEMO_DX = {f"C{i:02d}" for i in range(100)}  # C00-C99

# MCC codes
MCC_CODES = {
    "A41.0", "A41.1", "A41.2", "A41.3", "A41.4", "A41.5", "A41.8", "A41.9",
    "R65.20", "R65.21", "J96.00", "J96.01", "J96.02",
    "N17.0", "N17.1", "N17.2", "N17.8", "N17.9",
    "I50.21", "I50.23", "I50.31", "I50.33",
    "N18.4", "J44.1", "I46.2", "I46.8", "I46.9", "G93.1",
}

CC_CODES = {
    "E11.9", "E11.65", "E11.8", "N18.3", "I48.0", "I48.1", "I48.2", "I48.91",
    "E87.0", "E87.1", "E87.2", "E87.3", "E87.4", "E87.5", "E87.6",
    "D64.9", "D64.8",
}

NO_EFFECT_CODES = {"I10", "E78.5", "E78.0", "Z87.891"}


def detect_department(claim: ClaimInput) -> Department:
    """Auto-detect department from diagnosis + procedure codes."""
    pdx = claim.principal_dx.upper()
    procs = set(claim.procedures)

    # Cath Lab
    if (pdx.startswith(("I20", "I21", "I22", "I24", "I25"))
            and (procs & (PCI_CODES | DIAG_CATH_CODES | ANGIO_CODES))):
        return Department.CATH_LAB

    # Dialysis
    if pdx.startswith("N18") and (procs & (HD_CODES | CAPD_CODES)):
        return Department.DIALYSIS

    # Chemo
    if any(pdx.startswith(c) for c in CHEMO_DX):
        return Department.CHEMO

    # ICU (ventilator or ICU ward)
    if procs & VENTILATOR_CODES or (claim.ward and "icu" in claim.ward.lower()):
        return Department.ICU_NICU

    # ER/UCEP
    if claim.ward and ("er" in claim.ward.lower() or "emergency" in claim.ward.lower()):
        return Department.ER_UCEP

    # Check for surgical procedures (broad OR codes).
    # NOTE: (1, 86) is intentionally broad as a catch-all. More specific department
    # checks (dialysis, ICU, etc.) MUST appear above this block to take priority.
    surgical_ranges = [
        (1, 86), (77, 84), (38, 39), (42, 54), (55, 59), (65, 71)
    ]
    for proc in procs:
        try:
            proc_num = float(proc)
            for low, high in surgical_ranges:
                if low <= proc_num < high:
                    return Department.OR_SURGERY
        except ValueError:
            pass

    # Rehab
    rehab_procs = {p for p in procs if p.startswith("93.")}
    if rehab_procs:
        return Department.REHAB

    # OPD (no admission or short visit)
    if not claim.admit_date:
        return Department.OPD_NCD

    return Department.OR_SURGERY  # default for IPD with procedures


def run_rule_engine(claim: ClaimInput) -> list[CheckResult]:
    """Run all deterministic checks. Returns list of results."""
    results = []

    # === Checkpoint 1: Basic data validation ===
    if not claim.principal_dx:
        results.append(CheckResult(
            severity=Severity.CRITICAL,
            checkpoint="Dx-Proc Match",
            message="ไม่มี Principal Diagnosis (PDx)",
            fix_action="เพิ่ม PDx ใน DIA file (DXTYPE=1)"
        ))

    if not claim.procedures:
        results.append(CheckResult(
            severity=Severity.WARNING,
            checkpoint="Dx-Proc Match",
            message="ไม่มี Procedure codes — ถ้าเป็น IPD ที่มีหัตถการ ต้อง code ให้ครบ",
            fix_action="เพิ่ม procedure codes ใน OPR file"
        ))

    # === Checkpoint 4: 16-File / Data Format ===
    if claim.admit_date and claim.discharge_date:
        if claim.discharge_date < claim.admit_date:
            results.append(CheckResult(
                severity=Severity.CRITICAL,
                checkpoint="16-File Completeness",
                message="วันที่ discharge ก่อนวันที่ admit — format date ผิด",
                fix_action="แก้ไข DATEADM / DATEDSC ใน IPD file"
            ))

        los = (claim.discharge_date - claim.admit_date).days
        if los == 0:
            results.append(CheckResult(
                severity=Severity.WARNING,
                checkpoint="16-File Completeness",
                message=f"LOS = 0 วัน — อาจเป็น ODS/same-day discharge ตรวจสอบ D/C type",
            ))
        elif los > 90:
            results.append(CheckResult(
                severity=Severity.WARNING,
                checkpoint="DRG Verification",
                message=f"LOS = {los} วัน (ยาวมาก) — ตรวจสอบว่าเป็น long-stay outlier หรือ date error",
            ))
    else:
        if claim.an:  # IPD should have dates
            results.append(CheckResult(
                severity=Severity.CRITICAL,
                checkpoint="16-File Completeness",
                message="ไม่มีวันที่ admit/discharge — IPD ต้องมี",
                fix_action="เพิ่ม DATEADM + DATEDSC ใน IPD file"
            ))

    # === Checkpoint 5: Timing & Authorization ===
    if claim.authen_code is None and claim.fund == Fund.UC:
        results.append(CheckResult(
            severity=Severity.CRITICAL,
            checkpoint="Timing & Auth",
            message="ไม่มี Authen Code — FDH ต้องการ Authen Code ที่ valid",
            fix_action="Verify ผู้ป่วยก่อน discharge เพื่อรับ Authen Code"
        ))

    if claim.discharge_date and claim.submit_date:
        days_to_submit = (claim.submit_date - claim.discharge_date).days
        if days_to_submit <= 1:
            results.append(CheckResult(
                severity=Severity.PASSED,
                checkpoint="Timing & Auth",
                message="ส่งภายใน 24 ชม. = Fast Track (สปสช. จ่ายใน 72 ชม.)"
            ))
        elif days_to_submit <= 30:
            results.append(CheckResult(
                severity=Severity.PASSED,
                checkpoint="Timing & Auth",
                message=f"ส่งภายใน {days_to_submit} วัน — อยู่ในเกณฑ์ปกติ"
            ))
        else:
            results.append(CheckResult(
                severity=Severity.CRITICAL,
                checkpoint="Timing & Auth",
                message=f"ส่งเกิน 30 วัน ({days_to_submit} วัน) — ถูกปรับลดอัตราจ่าย!",
                fix_action="ส่งเบิกให้เร็วที่สุด — ตั้ง alert system เตือนก่อนครบ 30 วัน"
            ))

    # === Checkpoint 6: CC/MCC Optimization ===
    sdx_set = set(claim.secondary_dx)
    has_mcc = bool(sdx_set & MCC_CODES)
    has_cc = bool(sdx_set & CC_CODES)

    if claim.an and not has_mcc and not has_cc:
        results.append(CheckResult(
            severity=Severity.OPTIMIZATION,
            checkpoint="CC/MCC Optimization",
            message="ไม่มี CC/MCC coded — ตรวจ medical record ว่าผู้ป่วยมี comorbidities (DM, CKD, HF, AF, COPD) ที่ยังไม่ได้ code หรือไม่",
            fix_action="เพิ่ม SDx ที่เป็น CC/MCC เพื่อเพิ่ม DRG weight ได้ 5-40%"
        ))
    elif has_mcc:
        results.append(CheckResult(
            severity=Severity.PASSED,
            checkpoint="CC/MCC Optimization",
            message="มี MCC documented — จะได้ DRG weight สูงสุดในกลุ่ม"
        ))
    elif has_cc:
        results.append(CheckResult(
            severity=Severity.PASSED,
            checkpoint="CC/MCC Optimization",
            message="มี CC documented — ตรวจว่ามี MCC ที่ยังไม่ได้ code เพื่อเพิ่ม RW อีก"
        ))

    # === Checkpoint 3: Device Documentation ===
    if claim.devices:
        for dev in claim.devices:
            if not dev.get("lot"):
                results.append(CheckResult(
                    severity=Severity.CRITICAL,
                    checkpoint="Device Documentation",
                    message=f"อุปกรณ์ {dev.get('type', 'unknown')} ไม่มี lot number — ต้องตรง GPO VMI",
                    fix_action="เพิ่ม lot/serial number ใน ADP file ให้ตรงกับ GPO record"
                ))
            if not dev.get("qty"):
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    checkpoint="Device Documentation",
                    message=f"อุปกรณ์ {dev.get('type', 'unknown')} ไม่ระบุจำนวน",
                ))
    elif any(p in PCI_CODES | STENT_CODES for p in claim.procedures):
        results.append(CheckResult(
            severity=Severity.CRITICAL,
            checkpoint="Device Documentation",
            message="มี PCI/Stent procedure แต่ไม่มีข้อมูลอุปกรณ์ (stent)",
            fix_action="เพิ่มข้อมูล stent (type, brand, size, lot, qty) ใน ADP file"
        ))

    return results


def calculate_score(results: list[CheckResult]) -> tuple[int, bool]:
    """Calculate overall score and readiness."""
    if not results:
        return 0, False

    total = len(results)
    passed = sum(1 for r in results if r.severity in (Severity.PASSED, Severity.OPTIMIZATION))
    critical = sum(1 for r in results if r.severity == Severity.CRITICAL)

    score = round((passed / total) * 100) if total > 0 else 0
    ready = critical == 0

    return score, ready
