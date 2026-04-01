"""Deny Analyzer — Root cause analysis for denied Cath Lab claims."""

from core.cathlab_models import CathLabClaim, DenyAnalysis, DenyCodeExplained
from core.drg_calculator import lookup_drg, BASE_RATE_IN_ZONE

# Deny code definitions (from deny-codes.md + real e-Claim data)
DENY_CODE_DB: dict[str, dict] = {
    # HC codes (High Cost / Device)
    "HC09": {
        "meaning": "อุปกรณ์ และอวัยวะเทียมในการทำหัตถการโรค (Instrument)",
        "category": "device",
        "fix": "ตรวจ stent serial/lot number ตรง GPO VMI, ตรวจ ADP file TYPE/CODE, ตรวจจำนวนตรง procedure note",
        "recovery": 0.85,
    },
    "HC01": {
        "meaning": "ไม่มีค่าชั่ง/รับสีรักษา ในการรักษาโรคมะเร็งทั่วไป",
        "category": "device",
        "fix": "ตรวจสอบเอกสารประกอบ",
        "recovery": 0.70,
    },
    "HC13": {
        "meaning": "เงื่อนไข HC เพิ่มเติม (device/instrument documentation)",
        "category": "device",
        "fix": "ตรวจเอกสารอุปกรณ์ครบถ้วน ตรง GPO VMI record",
        "recovery": 0.80,
    },
    # IP codes
    "IP01": {
        "meaning": "IP ในเขต — การจ่าย IP ตามปกติ",
        "category": "payment",
        "fix": "ตรวจสอบ HCODE/HMAIN/RG ถูกต้อง",
        "recovery": 0.90,
    },
    "IP02": {
        "meaning": "IP ข้ามเขต",
        "category": "payment",
        "fix": "ตรวจ refer form, สิทธิ์ข้ามเขต",
        "recovery": 0.80,
    },
    # D codes (Deny reasons)
    "D01": {"meaning": "ไม่มีสิทธิ UC", "category": "eligibility", "fix": "ตรวจสิทธิ์ + ลงทะเบียน", "recovery": 0.40},
    "D02": {"meaning": "สิทธิ์ซ้ำซ้อน", "category": "eligibility", "fix": "ตรวจสิทธิ์ที่แท้จริง", "recovery": 0.50},
    "D05": {"meaning": "ข้อมูลซ้ำซ้อน (Duplicate)", "category": "data_error", "fix": "ตรวจไม่ส่งซ้ำ ใช้ e-Appeal", "recovery": 0.70},
    "D06": {"meaning": "ส่งเกินกำหนดเวลา", "category": "timing", "fix": "ส่งภายใน 30 วัน", "recovery": 0.20},
    "D07": {"meaning": "DRG Grouping Error", "category": "coding_error", "fix": "ตรวจ ICD-10/ICD-9-CM/ข้อมูลพื้นฐาน", "recovery": 0.80},
    "D10": {"meaning": "รหัสโรค/หัตถการไม่สอดคล้อง", "category": "coding_error", "fix": "ตรวจ Dx-Proc match", "recovery": 0.85},
    # C codes (common)
    "C201": {"meaning": "ไม่มีรหัสวินิจฉัยโรคหลัก (No PDx)", "category": "coding_error", "fix": "ใส่ PDx ใน DIA file", "recovery": 0.95},
    "C210": {"meaning": "จัดกลุ่ม DRG ไม่ได้", "category": "coding_error", "fix": "ตรวจ ICD-10/ICD-9-CM ทั้งหมด", "recovery": 0.80},
    "C305": {"meaning": "Approve Code ไม่ตรง", "category": "auth", "fix": "ขอ Approve Code ใหม่จาก EDC", "recovery": 0.75},
    "C438": {"meaning": "สิทธิประโยชน์ไม่ตรง", "category": "eligibility", "fix": "ตรวจสิทธิ์ เลือกให้ตรง", "recovery": 0.85},
    "C999": {"meaning": "ไม่พบข้อมูลในฐานตรวจสอบสิทธิ", "category": "eligibility", "fix": "ตรวจ PID/CID ถูกต้อง", "recovery": 0.60},
}

# Denied item to category mapping
DENIED_ITEM_CATEGORIES = {
    "INST": "device",
    "CLOPIDOGREL_DRUG": "drug_catalog",
    "IPINRGR": "payment",
    "IPINRGC": "payment",
    "DRUG": "drug_catalog",
    "OPBKK": "payment",
}


def _classify_category(deny_codes: list[str], denied_items: list[str]) -> str:
    """Classify the primary deny category."""
    categories = []

    for code in deny_codes:
        info = DENY_CODE_DB.get(code, {})
        if info:
            categories.append(info.get("category", "unknown"))

    for item in denied_items:
        cat = DENIED_ITEM_CATEGORIES.get(item)
        if cat:
            categories.append(cat)

    if "device" in categories:
        return "device_documentation"
    if "coding_error" in categories:
        return "coding_error"
    if "drug_catalog" in categories:
        return "drug_catalog_mismatch"
    if "eligibility" in categories:
        return "eligibility_issue"
    if "timing" in categories:
        return "timeline_violation"
    if "payment" in categories:
        return "payment_calculation"

    return "unknown"


def _build_root_cause(claim: CathLabClaim, category: str) -> str:
    """Build human-readable root cause explanation."""
    parts = []

    if category == "device_documentation":
        parts.append(f"อุปกรณ์/เวชภัณฑ์ในการทำหัตถการมีปัญหาด้านเอกสาร")
        if "INST" in claim.denied_items:
            parts.append(f"ค่าอุปกรณ์ (INST) {claim.inst_amount:,.0f} บาท ถูกปฏิเสธ")
            parts.append("สาเหตุที่เป็นไปได้: stent serial/lot number ไม่ตรง GPO VMI, ADP file TYPE/CODE ไม่ถูกต้อง, จำนวนไม่ตรง procedure note")
        if "CLOPIDOGREL_DRUG" in claim.denied_items:
            parts.append("Clopidogrel drug ถูกปฏิเสธ — TMT code อาจไม่ตรง Drug Catalog ของ สปสช.")

    elif category == "coding_error":
        parts.append(f"รหัสวินิจฉัย/หัตถการมีปัญหา")
        parts.append(f"PDx: {claim.principal_dx} | Procedures: {claim.procedures}")

    elif category == "drug_catalog_mismatch":
        parts.append("รหัสยาไม่ตรง Drug Catalog ของ สปสช.")
        if "CLOPIDOGREL_DRUG" in claim.denied_items:
            parts.append("Clopidogrel: ตรวจ TMT code (ต้อง map Hosp Drug Code → TMT ใน Drug Catalog)")

    elif category == "eligibility_issue":
        parts.append(f"สิทธิ์ผู้ป่วยมีปัญหา (สิทธิ์: {claim.fund})")

    elif category == "timeline_violation":
        parts.append(f"ส่งข้อมูลเกินกำหนด ({claim.days_since_discharge} วันหลัง D/C)")

    else:
        parts.append(f"สาเหตุที่ยังวิเคราะห์ไม่ได้ — deny codes: {claim.deny_codes}")

    return " | ".join(parts)


def _build_fix_steps(claim: CathLabClaim, category: str) -> list[str]:
    """Build actionable fix steps."""
    steps = []

    if category == "device_documentation":
        steps.extend([
            "1. ตรวจ ADP file: TYPE (3/4/5), CODE ตรงกับ สปสช. กำหนด",
            "2. ตรวจ stent serial/lot number ตรงกับ GPO VMI record",
            "3. ตรวจจำนวน stent ตรง procedure note (Cath report)",
            "4. ตรวจ rate ไม่เกิน ceiling price ที่ สปสช. กำหนด",
        ])
        if "CLOPIDOGREL_DRUG" in claim.denied_items:
            steps.extend([
                "5. ตรวจ Clopidogrel TMT code ตรง Drug Catalog (ดาวน์โหลดจาก drug.nhso.go.th)",
                "6. Map Hosp Drug Code → TMT code ใน DRU file",
            ])
        steps.append(f"สุดท้าย: แก้ไขข้อมูลแล้วส่งใหม่ผ่าน e-Claim")

    elif category == "coding_error":
        steps.extend([
            "1. ตรวจ PDx: ICD-10 ถูกต้อง + specific (ไม่ใช่ unspecified)",
            "2. ตรวจ SDx: CC/MCC ที่มีจริงครบถ้วน",
            "3. ตรวจ Procedures: ICD-9-CM ถูกต้อง + ตรง PDx",
            "4. ตรวจ DRG grouping ตรงกับที่คาดหวัง",
            "5. แก้ไขแล้วส่งใหม่",
        ])

    elif category == "drug_catalog_mismatch":
        steps.extend([
            "1. ดาวน์โหลด Drug Catalog ล่าสุดจาก drug.nhso.go.th",
            "2. Map รหัสยาใน HIS กับ GPUID/TMT ที่ สปสช. กำหนด",
            "3. แก้ DRU file แล้วส่งใหม่",
        ])

    elif category == "eligibility_issue":
        steps.extend([
            "1. ตรวจสิทธิ์ผ่านระบบ สปสช. ณ วันที่รับบริการ",
            "2. ถ้าสิทธิ์ถูกต้อง → ติดต่อ สปสช. เขต",
            "3. ถ้าสิทธิ์ผิด → แก้ INS file แล้วส่งใหม่",
        ])

    elif category == "timeline_violation":
        steps.extend([
            "1. ส่งหนังสือขอผ่อนผันพร้อมเหตุผล",
            "2. แนบเอกสารสนับสนุน (เช่น ระบบขัดข้อง)",
        ])

    return steps


def _generate_appeal_draft(claim: CathLabClaim, root_cause: str) -> str:
    """Generate appeal letter draft in formal Thai."""
    drg_info = lookup_drg(claim.drg) if claim.drg else None
    drg_desc = drg_info.description if drg_info else claim.drg

    return f"""เรื่อง ขอทบทวนผลการตรวจสอบการขอรับค่าใช้จ่ายเพื่อบริการสาธารณสุข

เรียน ผู้อำนวยการสำนักงานหลักประกันสุขภาพแห่งชาติ เขต 6

    ตามที่โรงพยาบาลพญาไทศรีราชา รหัสหน่วยบริการ 11855 ได้ส่งข้อมูล
การขอรับค่าใช้จ่ายเพื่อบริการสาธารณสุข สำหรับผู้ป่วย

    HN: {claim.hn}
    AN: {claim.an}
    วันที่รับเข้า: {claim.admit_date.strftime('%d/%m/%Y')}
    วันที่จำหน่าย: {claim.discharge_date.strftime('%d/%m/%Y')}
    DRG: {claim.drg} ({drg_desc})
    ยอดเรียกเก็บ: {claim.charge_amount:,.2f} บาท

    ทางโรงพยาบาลได้รับแจ้งว่าข้อมูลดังกล่าวถูกปฏิเสธการจ่าย
เนื่องจาก: {', '.join(claim.deny_codes)}

    ข้อชี้แจง:
    {root_cause}

    ทั้งนี้ทางโรงพยาบาลได้แก้ไขข้อมูลเรียบร้อยแล้ว
จึงเรียนมาเพื่อโปรดพิจารณาทบทวนผลการตรวจสอบ

    ขอแสดงความนับถือ
    (ลายเซ็น ผอ.รพ.)
"""


def analyze_deny(claim: CathLabClaim) -> DenyAnalysis:
    """Analyze denied claim: find root cause, suggest fix, draft appeal."""
    category = _classify_category(claim.deny_codes, claim.denied_items)

    # Explain each deny code
    explained = []
    for code in claim.deny_codes:
        info = DENY_CODE_DB.get(code, {"meaning": f"รหัส {code} (ไม่พบในฐานข้อมูล)", "fix": "ตรวจสอบกับ สปสช."})
        explained.append(DenyCodeExplained(
            code=code,
            meaning=info.get("meaning", "ไม่ทราบ"),
            fix=info.get("fix", "ตรวจสอบกับ สปสช."),
        ))

    # Root cause
    root_cause = _build_root_cause(claim, category)

    # Fix steps
    fix_steps = _build_fix_steps(claim, category)

    # Recovery estimation
    recovery_chances = [DENY_CODE_DB.get(c, {}).get("recovery", 0.5) for c in claim.deny_codes]
    avg_recovery = sum(recovery_chances) / len(recovery_chances) if recovery_chances else 0.5

    # Estimated recovery amount
    drg_info = lookup_drg(claim.drg) if claim.drg else None
    estimated = claim.expected_payment or (drg_info.payment_estimate_in_zone if drg_info else claim.charge_amount)

    # Severity
    if estimated > 50000:
        severity = "high"
    elif estimated > 10000:
        severity = "medium"
    else:
        severity = "low"

    # Recommended action
    if avg_recovery >= 0.8 and category in ("device_documentation", "coding_error", "drug_catalog_mismatch"):
        action = "auto_fix"
    elif avg_recovery >= 0.5:
        action = "appeal"
    elif avg_recovery >= 0.3:
        action = "escalate"
    else:
        action = "write_off"

    # Appeal draft
    appeal_draft = None
    if action in ("appeal", "escalate"):
        appeal_draft = _generate_appeal_draft(claim, root_cause)

    confidence = min(avg_recovery + 0.1, 1.0) if len(claim.deny_codes) <= 3 else avg_recovery * 0.8

    return DenyAnalysis(
        an=claim.an,
        category=category,
        severity=severity,
        root_cause=root_cause,
        deny_codes_explained=explained,
        recommended_action=action,
        fix_steps=fix_steps,
        appeal_draft=appeal_draft,
        recovery_chance=round(avg_recovery, 2),
        estimated_recovery=round(estimated, 2),
        confidence=round(confidence, 2),
    )
