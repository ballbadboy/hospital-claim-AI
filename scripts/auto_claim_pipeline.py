#!/usr/bin/env python3
"""
Auto Claim Pipeline — CSV in → DOCX out, zero AI intervention.

Usage:
    python scripts/auto_claim_pipeline.py eclaim_export.csv [output_dir]

Reads e-Claim CSV → parses all rows → generates Deny Report + Appeal Letter
for every denied case. 100 cases in seconds.
"""

import csv, io, os, sys, time
from datetime import datetime
from pathlib import Path

# ── Inline CSV parser (no external model dependency) ──────────

# Deny code meanings lookup
DENY_MEANINGS = {
    "HC01": "ไม่มีคำสั่ง/รับสีรักษา โรคมะเร็ง",
    "HC02": "การรักษาโรคมะเร็งตามโปรโตคอล",
    "HC03": "Peritoneal/Haemo Dialysis",
    "HC04": "Crytococcal Meningitis ใน HIV",
    "HC05": "CMV Retinitis ใน HIV",
    "HC06": "Decompression Sickness",
    "HC07": "Methadone Maintenance",
    "HC08": "การตรวจวิเคราะห์ราคาและหัตถการหัวใจ",
    "HC09": "อุปกรณ์และอวัยวะเทียม ในการทำหัตถการ (Instrument)",
    "HC10": "จัดเตรียมประราชกาศ",
    "HC13": "ยา Clopidogrel / High-cost drug",
    "IP01": "IP เกณฑ์ (ผู้ป่วยในไม่ผ่านเกณฑ์)",
    "IP02": "IP ข้ามเขต",
    "IP03": "มาตรา 7 กรณีหนุสมควร",
    "IP05": "แผนกรณีผู้ป่วยใน สิทธิอื่น",
}

DENY_FIXES = {
    "HC09": {
        "causes": [
            "ข้อมูล ADP file ไม่ครบ (TYPE, CODE, Serial/Lot Number)",
            "ราคาอุปกรณ์ไม่ตรงกับ Fee Schedule",
            "Device ไม่อยู่ในบัญชี สปสช. อนุมัติ",
            "ตั้งแต่ 1 เม.ย. 69: ไม่ส่ง Serial/Barcode ผ่าน Standard API",
        ],
        "fixes": [
            "ตรวจ ADP file: TYPE, CODE, QTY, RATE, SERIALNO",
            "ตรวจ stent code ตรง NHSO Device Catalog",
            "เพิ่ม Lot/Serial Number",
            "ตรวจราคาไม่เกินเพดาน",
        ],
    },
    "HC13": {
        "causes": [
            "GPUID/TMT code ไม่ตรง Drug Catalog สปสช.",
            "ราคายาเกิน median price",
            "ข้อมูลใน DRU file ผิด format",
        ],
        "fixes": [
            "ตรวจ DRU file: GPUID ตรง TMT catalog",
            "ตรวจ Drug ID 24 หลัก",
            "ตรวจราคายาไม่เกิน median price",
        ],
    },
    "IP01": {
        "causes": [
            "LOS สั้นเกินไปสำหรับ DRG",
            "Authen Code หมดอายุ/ไม่ตรง",
            "เอกสาร Refer ไม่ครบ (กรณี HMAIN ≠ HCODE)",
            "ข้อมูล IPD file ไม่ครบ",
        ],
        "fixes": [
            "ตรวจ Authen Code valid ณ วันที่ admit",
            "ตรวจ IPD file: DATEADM, DATEDSC, DISCHT ครบ",
            "ตรวจใบ Refer (ถ้าเป็นเคส refer)",
            "เตรียม Cath report + clinical indication",
        ],
    },
}

# ─── Knowledge-based Smart Analyzer ─────────────────────
# ดึงจาก: cath-lab.md, deny-fixes.md, inst-payment-reform-fy69.md, cardiac-codes.md

# Dx-Proc match rules (จาก cath-lab.md Checkpoint 1)
DX_PROC_RULES = {
    # PDx pattern → required procedures → expected DRG scenario
    "I21.0": {"name": "STEMI anterior", "need_proc": ["36.06","36.07"], "need_doc": ["Troponin","EKG","D2B time","Cath report"], "drg_hint": "Acute MI w/ PCI", "rw_range": "3.5-8.6"},
    "I21.1": {"name": "STEMI inferior", "need_proc": ["36.06","36.07"], "need_doc": ["Troponin","EKG","D2B time","Cath report"], "drg_hint": "Acute MI w/ PCI", "rw_range": "3.5-8.6"},
    "I21.2": {"name": "STEMI other sites", "need_proc": ["36.06","36.07"], "need_doc": ["Troponin","EKG","D2B time","Cath report"], "drg_hint": "Acute MI w/ PCI", "rw_range": "3.5-8.6"},
    "I21.3": {"name": "STEMI unspecified", "need_proc": ["36.06","36.07"], "need_doc": ["Troponin","EKG","Cath report"], "drg_hint": "Acute MI w/ PCI", "rw_range": "3.5-8.6"},
    "I21.4": {"name": "NSTEMI", "need_proc": ["36.06","36.07"], "need_doc": ["Troponin trend","EKG","Risk score","Cath report"], "drg_hint": "Acute MI w/ PCI", "rw_range": "2.0-5.0"},
    "I20.0": {"name": "Unstable Angina", "need_proc": ["88.56","37.22"], "need_doc": ["Symptoms","EKG","Troponin NORMAL"], "drg_hint": "Circ dx w/ cath หรือ PTCA", "rw_range": "1.0-2.5"},
    "I25.1": {"name": "Chronic IHD (CCS)", "need_proc": ["88.56","37.22"], "need_doc": ["Clinical indication","Cath report"], "drg_hint": "Circ dx except AMI w/ cath", "rw_range": "0.8-1.5", "pre_auth": True},
    "I25.5": {"name": "Ischemic cardiomyopathy", "need_proc": [], "need_doc": ["Echo","Clinical indication"], "drg_hint": "Medical DRG", "rw_range": "0.5-1.5", "pre_auth": True},
    "I25.8": {"name": "Other chronic IHD", "need_proc": ["88.56"], "need_doc": ["Clinical indication"], "drg_hint": "Circ dx", "rw_range": "0.5-1.5", "pre_auth": True},
    "I25.9": {"name": "Chronic IHD unspecified", "need_proc": ["88.56"], "need_doc": ["Clinical indication"], "drg_hint": "Circ dx", "rw_range": "0.5-1.5", "pre_auth": True},
}

# INST เพดาน (จาก inst-payment-reform-fy69.md)
INST_LIMITS = {
    "4301": ("Guiding Catheter", 2),
    "4302": ("PTCA Guide Wire", 3),
    "4303": ("PTCA Balloon", 5),
    "4304": ("BMS Stent", 3),
    "4305A": ("DES อัลลอยด์", 3),
    "4305B": ("DES สแตนเลส", 1),
    "4305C": ("DES polymer ย่อยสลาย", 3),
    "4305D": ("DES ไม่มี polymer", 1),
    "4306": ("Stent Graft", 2),
    "4307": ("Rota Burr", 2),
    "4308": ("Rota Burr Advancer", 1),
    "4309": ("Cutting/Scoring Balloon", 2),
    "4310": ("Thrombectomy Catheter", 1),
    "4313": ("IVUS", 1),
    "4314": ("FFR Wire", 1),
    "4319": ("CTO PTCA Guide Wire", 3),
    "4320": ("Rotablator Guide Wire", 1),
    "4321": ("CTO PTCA Balloon", 1),
    "4401": ("Diag Catheter", 3),
    "4407": ("Diag Angiography Catheter", 3),
    "4701": ("Sheath", 3),
    "4702": ("Closure Device", 4),
}

# Device-Procedure Matching — อุปกรณ์ต้องมี procedure code คู่กัน ไม่งั้น deny
# แจ้งจาก สปสช. มี.ค. 2569: device 4307-4310, 4320 ต้องมี 17.55
DEVICE_PROC_MATCH = {
    "4307": {"name": "Rota Burr", "require_proc": "17.55", "proc_name": "Transluminal coronary atherectomy"},
    "4308": {"name": "Rota Burr Advancer", "require_proc": "17.55", "proc_name": "Transluminal coronary atherectomy"},
    "4309": {"name": "Cutting/Scoring Balloon", "require_proc": "17.55", "proc_name": "Transluminal coronary atherectomy"},
    "4310": {"name": "Thrombectomy Catheter", "require_proc": "17.55", "proc_name": "Transluminal coronary atherectomy"},
    "4320": {"name": "Rotablator Guide Wire", "require_proc": "17.55", "proc_name": "Transluminal coronary atherectomy"},
    "4306": {"name": "Stent Graft", "require_proc": "36.06", "proc_name": "Insertion of coronary stent"},
}

# CC/MCC ที่เพิ่ม RW (จาก cath-lab.md Checkpoint 6)
CC_MCC_CODES = {
    "E11.65": ("DM with hyperglycemia", "CC", "ถ้ามี DM → code เป็น E11.65 แทน E11.9 ได้ RW สูงกว่า"),
    "N18.4":  ("CKD Stage 4", "MCC", "MCC = RW สูงสุดในกลุ่ม"),
    "N18.3":  ("CKD Stage 3", "CC", "ตรวจ eGFR ถ้า 30-59 = CKD3"),
    "I50.21": ("Acute systolic HF", "MCC", "ถ้ามี HF ให้ code acute specific"),
    "I50.31": ("Acute diastolic HF", "MCC", "ถ้ามี HF ให้ code acute specific"),
    "I48":    ("Atrial fibrillation", "CC", "ตรวจ EKG ว่ามี AF ไหม"),
    "J44.1":  ("COPD acute exacerbation", "MCC", "MCC = RW สูงสุด"),
}


def smart_analyze(claim):
    """Knowledge-based analysis — ไม่ต้องเรียก AI API.

    Returns dict of analysis results to enrich DOCX output.
    """
    findings = []       # สิ่งที่พบ
    warnings = []       # ข้อควรระวัง
    optimizations = []  # โอกาสเพิ่ม RW
    appeal_points = []  # เหตุผลสำหรับอุทธรณ์

    drg = claim.get("drg", "")
    rw = claim.get("rw", 0)
    is_refer = claim.get("is_refer", False)
    fund_main = claim.get("fund_main", [])
    fund_sub = claim.get("fund_sub", [])
    los = claim.get("los", 1)
    admit_str = claim.get("admit", "")

    # ── 1. DRG-based analysis ──
    if drg.startswith("052"):
        findings.append("DRG กลุ่ม 052xx = MDC 05 Circulatory System → เคส Cath Lab/หัวใจ")
        if rw >= 5.0:
            findings.append(f"RW {rw:.4f} สูง → มี MCC ร่วม หรือ PCI with DES + complications")
            appeal_points.append(
                f"เคสนี้มี RW {rw:.4f} (สูง) แสดงว่ามีภาวะแทรกซ้อนร่วม "
                "การรักษาเป็นผู้ป่วยในมีความจำเป็นทาง clinical "
                "ตามแนวทางเวชปฏิบัติของสมาคมโรคหัวใจแห่งประเทศไทย"
            )
        elif rw >= 2.0:
            findings.append(f"RW {rw:.4f} ปานกลาง → PCI หรือ Diagnostic cath with CC")
        else:
            findings.append(f"RW {rw:.4f} ต่ำ → Diagnostic cath only หรือ medical management")
            optimizations.append("ตรวจสอบว่ามี CC/MCC ที่ยังไม่ได้ code → อาจเพิ่ม RW ได้")

    # ── 2. Deny code specific analysis ──
    for code in fund_main:
        code = code.strip()

        if code == "HC09":
            # ตรวจว่าเป็นก่อนหรือหลัง 1 เม.ย. 69
            is_post_april = False
            try:
                if admit_str:
                    day = int(admit_str[:2])
                    month = int(admit_str[3:5])
                    year = int(admit_str[6:10])
                    if year >= 2026 and month >= 4:
                        is_post_april = True
                    elif year > 2026:
                        is_post_april = True
            except Exception:
                pass

            if is_post_april:
                findings.append(
                    "HC09 + Admit หลัง 1 เม.ย. 69 → บังคับส่ง Serial/Barcode/QR "
                    "ผ่าน Standard API ตามประกาศ สปสช. ข้อ 5.2.2"
                )
                appeal_points.append(
                    "อุปกรณ์อยู่ในบัญชี สปสช. และมี Serial Number ครบ "
                    "แต่อาจยังไม่ได้ส่งผ่าน Standard API ตามเงื่อนไขใหม่ "
                    "ซึ่งเริ่มบังคับ 1 เม.ย. 69 (ข้อ 5.2.2 ร่างประกาศ สปสช.) "
                    "ทางโรงพยาบาลได้ดำเนินการส่งข้อมูลผ่าน API แล้ว"
                )
            else:
                findings.append(
                    "HC09 + Admit ก่อน 1 เม.ย. 69 → ปัญหาน่าจะเป็น "
                    "ADP file ไม่ครบ (TYPE/CODE/Serial) หรือราคาเกินเพดาน"
                )
                appeal_points.append(
                    "อุปกรณ์ที่ใช้อยู่ในบัญชี สปสช. อนุมัติ "
                    "ข้อมูลใน ADP file ได้แก้ไขให้ครบถ้วนแล้ว (TYPE, CODE, SERIALNO) "
                    "ดังเอกสารแนบ"
                )

            # ตรวจเพดานอุปกรณ์
            warnings.append(
                "ตรวจจำนวนอุปกรณ์: DES อัลลอยด์ ≤3 ชุด, DES สแตนเลส ≤1 ชุด, "
                "Guiding ≤2, Wire ≤3, Balloon ≤5 ต่อครั้ง (ปีงบ69 ข้อ 5.2.1)"
            )

            # ตรวจ Device-Procedure Matching (17.55 rule — แจ้งจาก สปสช. มี.ค. 69)
            proc_codes = claim.get("proc_codes", [])
            device_codes = claim.get("device_codes", [])
            for dev_code, rule in DEVICE_PROC_MATCH.items():
                if dev_code in device_codes:
                    req = rule["require_proc"]
                    if req not in proc_codes:
                        warnings.append(
                            f"CRITICAL: ใช้อุปกรณ์ {dev_code} ({rule['name']}) "
                            f"แต่ไม่มีรหัสหัตถการ {req} ({rule['proc_name']}) → "
                            f"ถูก deny แน่นอน! ต้องเพิ่ม {req} ใน OPR file"
                        )
                        appeal_points.append(
                            f"อุปกรณ์ {rule['name']} (รหัส {dev_code}) ที่ใช้ในหัตถการ "
                            f"ได้ดำเนินการเพิ่มรหัส {req} ({rule['proc_name']}) "
                            f"ใน OPR file แล้ว ตามข้อกำหนด ICD-9-CM 2015 สำหรับ DRG v6"
                        )

            # ตรวจข้อมูลก่อน 17/3/69 ต้องส่งใหม่ (Thrombuster)
            if "4310" in device_codes:
                try:
                    admit_chk = admit_str or claim.get("admit_date", "")
                    if "/" in admit_chk:
                        parts = admit_chk.split("/")
                        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                        if y > 2500:
                            y -= 543
                        from datetime import date as _date
                        admit_dt = _date(y, m, d)
                        cutoff = _date(2026, 3, 17)  # 17/3/2569
                        if admit_dt < cutoff:
                            warnings.append(
                                "CRITICAL: เคสนี้ใช้ Thrombectomy (4310) + admit ก่อน 17/3/69 "
                                "→ ต้องส่งข้อมูลใหม่ (แจ้งจาก สปสช. มี.ค. 69)"
                            )
                except Exception:
                    pass

        elif code == "IP01":
            if is_refer:
                findings.append(
                    "IP01 + เคส Refer (HMAIN≠HCODE) → สาเหตุหลักน่าจะเป็น "
                    "Authen Code หรือเอกสาร Refer ไม่ครบ"
                )
                appeal_points.append(
                    "ผู้ป่วยถูกส่งตัว (Refer) จาก รพ.ต้นสังกัดมารับการรักษา "
                    "มีใบส่งตัวและ Authen Code ครบถ้วน "
                    "การรับไว้เป็นผู้ป่วยในมีความจำเป็นเพื่อทำหัตถการสวนหัวใจ "
                    "และเฝ้าระวังภาวะแทรกซ้อนหลังทำหัตถการ"
                )
            else:
                findings.append(
                    "IP01 + ไม่ใช่เคส Refer → สาเหตุน่าจะเป็น "
                    "LOS สั้นเกินไป หรือ Authen Code หมดอายุ"
                )
            if los <= 1:
                warnings.append(
                    f"LOS = {los} วัน (สั้นมาก) → สปสช. อาจมองว่าเป็น day case "
                    "ไม่จำเป็นต้อง admit → ต้องเตรียม clinical justification"
                )

        elif code == "HC13":
            findings.append(
                "HC13 = ยา Clopidogrel → GPUID/TMT code ไม่ตรง Drug Catalog "
                "หรือราคาเกิน median price"
            )
            appeal_points.append(
                "ยา Clopidogrel เป็นยาต้านเกล็ดเลือดที่จำเป็นหลังทำ PCI "
                "ตาม ACC/AHA Guidelines ต้องให้ Dual Antiplatelet Therapy (DAPT) "
                "หลังใส่ stent ทุกราย การที่ข้อมูลไม่ผ่านเกิดจาก GPUID ไม่ตรง "
                "ซึ่งได้แก้ไขใน DRU file แล้ว"
            )

    # ── 3. Refer case analysis ──
    if is_refer:
        warnings.append(
            "เคส Refer: ต้องมี (1) ใบส่งตัว (2) Authen Code valid (3) "
            "HMAIN2 ต้องเป็นรหัส 5 หลัก ไม่ใช่รหัสเขต"
        )

    # ── 4. CC/MCC optimization hints ──
    if rw < 3.0 and drg.startswith("052"):
        optimizations.append(
            "RW ต่ำกว่า 3.0 ในเคส Cath Lab → ตรวจ medical record ว่ามี: "
            "DM (E11.65), CKD (N18.3-4), HF (I50.21/31), AF (I48), COPD (J44.1) "
            "ที่ยังไม่ได้ code → เพิ่ม CC/MCC จะได้ RW สูงขึ้น"
        )
    if rw >= 3.0 and rw < 5.0:
        optimizations.append(
            "ตรวจว่ามี MCC (เช่น CKD4, Acute HF, COPD exacerbation) "
            "ที่ documented แต่ยังไม่ได้ code → MCC 1 ตัว = RW กระโดดสูงสุดในกลุ่ม"
        )

    # ── 5. CCS Pre-Auth check (ปีงบ69 ใหม่) ──
    # ถ้า DRG ต่ำ + ไม่มี acute code → น่าจะเป็น CCS
    if rw and rw < 3.0 and drg.startswith("052"):
        warnings.append(
            "RW ต่ำ + DRG กลุ่ม Circulatory → อาจเป็น CCS (Chronic Coronary Syndromes) "
            "ซึ่งปีงบ69 ต้อง Pre Authorized ก่อนให้บริการทุกราย (ข้อ 5.2.1(1))"
        )

    # ── 6. Financial impact ──
    expected = claim.get("expected_payment", 0)
    if expected > 50000:
        findings.append(f"มูลค่าเคส {expected:,.0f} บาท → คุ้มค่ามากที่จะอุทธรณ์/resubmit")
    elif expected > 20000:
        findings.append(f"มูลค่าเคส {expected:,.0f} บาท → ควรแก้ไข resubmit")

    # ══════════════════════════════════════════════════
    # Standard Coding Guidelines 2026 — Knowledge Rules
    # อ้างอิง: references/nhso-rules/standard-coding-guidelines-2026.md
    # ══════════════════════════════════════════════════

    # ── 7. Sepsis coding rules (SCG ข้อ 1-2) ──
    # ตรวจจาก DRG กลุ่ม MDC 18 (Infectious) หรือ DRG ที่มี sepsis
    if drg.startswith("18") or any("sepsis" in s.lower() for s in fund_sub):
        warnings.append(
            "[SCG 2026 ข้อ 1-2] R65 (SIRS) เลิกใช้แล้ว — "
            "Sepsis (A41.9) ห้ามเป็น PDx ต้องใช้ organ infection เป็น PDx เสมอ "
            "(เช่น N10, K81.0, J18.9) แล้วใส่ A41.9 เป็น SDx "
            "ถ้าไม่พบเชื้อ/organ → ใช้ A49.9 หรือ R50.9 เป็น PDx "
            "Septic shock R57.2 เป็น PDx ได้เฉพาะไม่พบ source"
        )

    # ── 8. ACS specific coding (SCG ข้อ 25) ──
    if drg.startswith("052"):
        optimizations.append(
            "[SCG 2026 ข้อ 25] STEMI ต้องระบุ wall: "
            "I21.0 (anterior), I21.1 (inferior), I21.2 (other), I21.3 (unspecified site) "
            "— ห้ามใช้ I21.9 ถ้าระบุ wall ได้ เพราะ specific code อาจได้ RW สูงกว่า. "
            "NSTEMI = I21.4 เท่านั้น. "
            "Subsequent MI ภายใน 28 วัน = I22.- (ไม่ใช่ I21)"
        )
        # Ischemic cardiomyopathy
        if rw and rw < 2.0:
            optimizations.append(
                "[SCG 2026 ข้อ 26] ถ้ามี LVEF <40% + Hx MI หรือ LAD/LM >75% → "
                "code I25.5 Ischemic cardiomyopathy ได้ (ได้ CC เพิ่ม)"
            )

    # ── 9. Heart Failure EF classification (SCG ข้อ 32) ──
    # ทุกเคสหัวใจ ควรตรวจ HF coding
    if drg.startswith("05"):
        optimizations.append(
            "[SCG 2026 ข้อ 32] Heart failure ต้องระบุ EF: "
            "HFrEF (EF<40%) → I50.2x = MCC เพิ่ม RW 20-40%, "
            "HFmrEF (41-49.9%) → I50.4x, "
            "HFpEF (>50%) → I50.3x. "
            "ห้ามใช้ I50.9 ถ้ามีผล Echo ระบุ EF ได้ — "
            "de novo HF: สาเหตุ=PDx + HF=SDx / known HF exacerbation: HF=PDx"
        )

    # ── 10. CKD 4-5 บังคับลง (SCG ข้อ 52) ──
    # ทุกเคส IP ต้องเตือน
    optimizations.append(
        "[SCG 2026 ข้อ 52] CKD stage 4 (N18.4) = MCC เพิ่ม RW 20-40%! "
        "CKD 5 (N18.5) เช่นกัน — บังคับลงรหัสทุกกรณี IP "
        "ตรวจ eGFR: 15-29 = stage 4, <15 = stage 5. "
        "ถ้ามี CKD 3 (N18.3) ก็ได้ CC เพิ่ม RW 5-15%"
    )

    # ── 11. DM complication coding (SCG ข้อ 15) ──
    optimizations.append(
        "[SCG 2026 ข้อ 15] DM ต้อง code specific: "
        "E11.65 (hyperglycemia) ดีกว่า E11.9 (unspecified). "
        "DM+neuropathy=E11.4, DM+PVD=E11.5, ทั้งคู่=E11.7. "
        "ถ้ามาด้วยติดเชื้อ (cellulitis/osteo) → ติดเชื้อ=PDx, DM=SDx"
    )

    # ── 12. AF specific type (SCG ข้อ 31) ──
    if drg.startswith("05"):
        optimizations.append(
            "[SCG 2026 ข้อ 31] AF ต้องระบุชนิด: "
            "Paroxysmal I48.0, Persistent I48.1, Permanent I48.2 "
            "— ห้ามใช้ I48.9 ถ้าระบุชนิดได้ (specific = CC ที่แม่นยำกว่า)"
        )

    # ── 13. Stroke territory (SCG ข้อ 22, 33) ──
    if drg.startswith("01") or drg.startswith("045"):
        warnings.append(
            "[SCG 2026 ข้อ 33] Stroke ห้ามใช้ I64 ถ้าเลี่ยงได้ → "
            "ต้องระบุ I63.- (infarction) + embolism/thrombosis + territory. "
            "ใส่ G46.- (vascular syndrome) เป็น SDx เสมอ: "
            "MCA G46.0, ACA G46.1, PCA G46.2, Brainstem G46.3, "
            "Cerebellar G46.4, Lacunar G46.5-7"
        )

    # ── 14. Anemia in chronic disease (SCG ข้อ 11) ──
    optimizations.append(
        "[SCG 2026 ข้อ 11] Anemia in chronic disease/CKD/malignancy "
        "code ได้เมื่อ severe จนต้องให้เลือดหรือตรวจเพิ่ม DDx — "
        "D63.0 (neoplasm), D63.1 (CKD), D63.8 (other chronic) = CC"
    )

    # ── 15. Respiratory failure intubation rule (SCG ข้อ 42) ──
    if drg.startswith("04") or (rw and rw >= 5.0):
        optimizations.append(
            "[SCG 2026 ข้อ 42] Respiratory failure: "
            "วินิจฉัยได้แม้ O2 sat ยังปกติ ถ้าแพทย์ตัดสินใจ intubate — "
            "Type I J96.00 (hypoxemic) = MCC, Type II J96.01 (hypercapnic) = MCC. "
            "ถ้าใส่ ventilator → ต้อง code respiratory failure ด้วย"
        )

    # ── 16. COPD exacerbation = MCC (SCG ข้อ 38) ──
    optimizations.append(
        "[SCG 2026 ข้อ 38] COPD exacerbation J44.1 = MCC "
        "เพิ่ม RW 20-40%! ถ้ามี COPD + admit → ตรวจว่ามี exacerbation ไหม "
        "อย่าใช้ J44.9 ถ้ามี acute symptoms"
    )

    # ── 17. Gastritis needs endoscopy (SCG ข้อ 43) ──
    warnings.append(
        "[SCG 2026 ข้อ 43] Gastritis ต้องมี endoscopy ยืนยัน — "
        "ถ้าไม่ได้ scope → ใช้ dyspepsia (K30) ไม่ใช่ gastritis. "
        "เลือดออก + ไม่ scope → ใช้ haematemesis K92.0 / melaena K92.1"
    )

    # ── 18. AKI prerenal ≠ N17 (SCG ข้อ 51) ──
    warnings.append(
        "[SCG 2026 ข้อ 51] AKI prerenal (ดีขึ้นใน 1-3 วันหลังให้น้ำ) → "
        "ใช้ R39.2 Extrarenal uraemia ไม่ใช่ N17! "
        "N17 = MCC แต่ถ้าใช้ผิด = audit risk. "
        "KDIGO: Cr เพิ่ม >0.3 ใน 48ชม. หรือ ≥50% ใน 7 วัน"
    )

    # ── 19. DIC needs ISTH ≥5 (SCG ข้อ 14) ──
    warnings.append(
        "[SCG 2026 ข้อ 14] DIC (D65) ต้อง ISTH score ≥5 — "
        "ถ้าไม่ถึงเกณฑ์ → ใช้ D69.5 + D68.4 แทน"
    )

    # ── 20. Obesity Asian BMI (SCG ข้อ 19) ──
    optimizations.append(
        "[SCG 2026 ข้อ 19] Obesity ใช้ Asian BMI: "
        "Class I ≥25, Class II ≥30, Class III ≥35 กก/ม². "
        "IP: code ≥Class II+comorbidity หรือ Class III เท่านั้น (E66.8/E66.9)"
    )

    # ── 21. Electrolyte - when to code (SCG ข้อ 20) ──
    warnings.append(
        "[SCG 2026 ข้อ 20] Electrolyte imbalance: "
        "ลง code เฉพาะ severe — Na<120, K<2.5, Mg<0.5 "
        "หรือ hyperK ที่มี ECG change + urgent treatment. "
        "ถ้าเป็นแค่อาการของโรค (เช่น diarrhea, CKD) ห้ามลง"
    )

    # ── 22. Viral hepatitis as comorbidity (SCG ข้อ 4) ──
    optimizations.append(
        "[SCG 2026 ข้อ 4] Viral hepatitis (B18.x) สามารถเป็นโรคร่วมได้ "
        "แม้จะไม่ได้รักษา hepatitis โดยตรง — เพราะเพิ่มความเสี่ยง (WHO criteria). "
        "ถ้ามี cirrhosis + HBV/HCV → ลง hepatitis เป็น SDx ได้"
    )

    # ── 23. Cancer primary/secondary rules (SCG ข้อ 5) ──
    if drg.startswith("17") or drg.startswith("08"):
        warnings.append(
            "[SCG 2026 ข้อ 5] Cancer: รับไว้รักษา primary → primary=PDx. "
            "รับไว้รักษา secondary (brain/liver met) → secondary=PDx. "
            "Primary ผ่าตัดแล้วยังรักษาอยู่ → ยังใช้ primary code. "
            "หายแล้ว + new secondary → secondary=PDx + Z85.x=SDx"
        )

    return {
        "findings": findings,
        "warnings": warnings,
        "optimizations": optimizations,
        "appeal_points": appeal_points,
    }

# Hospital info (from CLAUDE.md)
HOSPITAL = {
    "hospcode": "11855",
    "hosp_name": "โรงพยาบาลพญาไทศรีราชา",
    "hosp_province": "จังหวัดชลบุรี",
    "nhso_region": "6",
    "nhso_region_name": "ระยอง",
    "base_rate_in": 8350,
    "base_rate_out": 9600,
}


def parse_float(s):
    if not s or s.strip() in ("-", ""):
        return 0.0
    return float(s.replace(",", "").strip())


def parse_csv_rows(csv_content):
    """Parse e-Claim CSV → list of claim dicts. No external dependencies."""
    reader = csv.reader(io.StringIO(csv_content))
    rows = list(reader)

    # Find header row
    header_idx = None
    for i, row in enumerate(rows):
        joined = ",".join(row)
        if "REP No." in joined or "TRAN_ID" in joined:
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("ไม่พบ header row (REP No. / TRAN_ID) ในไฟล์ CSV")

    claims = []
    for row in rows[header_idx + 1:]:
        if len(row) < 36:
            continue
        # Must have HN + AN
        hn = row[3].strip() if row[3] else ""
        an = row[4].strip() if row[4] else ""
        if not hn or not an:
            continue
        # Must have admit date
        if not row[8] or row[8].strip() in ("-", ""):
            continue

        # Detect deny
        first_20 = ",".join(row[:20]).upper()
        is_denied = "DENY" in first_20

        # Parse fund codes (col 14) and sub-fund (col 15)
        fund_main = [x.strip() for x in row[14].split(",") if x.strip()] if len(row) > 14 and row[14] else []
        fund_sub = [x.strip() for x in row[15].split(",") if x.strip()] if len(row) > 15 and row[15] else []

        # Find DRG and RW — columns 34,35 in standard format
        drg = row[34].strip() if len(row) > 34 and row[34].strip() else "-"
        rw = parse_float(row[35]) if len(row) > 35 else 0

        # Financial columns: around cols 37-50
        # Central reimburse typically col 38, charge col 37
        charge = parse_float(row[10]) if len(row) > 10 else 0
        central_reimburse = parse_float(row[38]) if len(row) > 38 else 0
        actual_paid = parse_float(row[39]) if len(row) > 39 else 0

        # Calculate expected & loss
        expected = round(rw * HOSPITAL["base_rate_in"]) if rw else 0
        if central_reimburse > 0:
            expected = max(expected, int(central_reimburse))
        loss = expected - int(actual_paid) if is_denied else 0

        # HCODE / HMAIN
        hcode = row[24].strip() if len(row) > 24 else ""
        hmain = row[25].strip() if len(row) > 25 else ""
        href = row[23].strip() if len(row) > 23 else ""
        fund_type = row[22].strip() if len(row) > 22 else "UCS"

        # LOS
        try:
            from datetime import datetime as dt
            admit_dt = dt.strptime(row[8].strip()[:10], "%d/%m/%Y")
            disch_dt = dt.strptime(row[9].strip()[:10], "%d/%m/%Y")
            los = max((disch_dt - admit_dt).days, 1)
        except Exception:
            los = 1

        claims.append({
            "rep_no": row[0].strip(),
            "hn": hn,
            "an": an,
            "pid": row[5].strip() if len(row) > 5 else "",
            "patient_name": row[6].strip() if len(row) > 6 else "",
            "patient_type": row[7].strip() if len(row) > 7 else "IP",
            "admit": row[8].strip(),
            "discharge": row[9].strip(),
            "los": los,
            "hcode": hcode,
            "hmain": hmain,
            "href": href,
            "fund": fund_type,
            "drg": drg,
            "rw": rw,
            "charge": charge,
            "central_reimburse": central_reimburse,
            "expected_payment": expected,
            "actual": int(actual_paid),
            "loss": loss,
            "is_denied": is_denied,
            "fund_main": fund_main,
            "fund_sub": fund_sub,
            "is_refer": hcode != hmain and hcode and hmain,
        })

    return claims


def claim_to_report_data(c):
    """Convert parsed claim dict → deny report data dict."""
    # Build issues from deny fund codes
    issues = []
    seen = set()
    for i, code in enumerate(c["fund_main"], 1):
        key = code.split(",")[0].strip() if code else ""
        if key in seen:
            continue
        seen.add(key)
        info = DENY_FIXES.get(key, {
            "causes": [f"รหัส {key}: ตรวจสอบข้อมูลในระบบ"],
            "fixes": ["ตรวจสอบข้อมูลและแก้ไขใน FDH"],
        })
        meaning = DENY_MEANINGS.get(key, key)
        subfund = c["fund_sub"][i-1] if i-1 < len(c["fund_sub"]) else "-"
        issues.append({
            "id": i,
            "title": f"{key} — {meaning}",
            "severity": "critical",
            "fund": f"{key} ({meaning})",
            "subfund": subfund,
            "deny_code": key,
            "causes": info["causes"],
            "fixes": info["fixes"],
        })

    # Build actions from issues
    impact_labels = ["สูงสุด", "สูง", "ปานกลาง", "ต่ำ"]
    actions = []
    for i, iss in enumerate(issues):
        actions.append({
            "priority": f"[{i+1}]",
            "item": f"แก้ {iss['deny_code']}",
            "action": iss["fixes"][0] if iss["fixes"] else "ตรวจสอบข้อมูล",
            "impact": impact_labels[min(i, len(impact_labels)-1)],
        })

    # ── Smart Analysis (knowledge-based) ──
    analysis = smart_analyze(c)

    # Enrich issues with smart findings
    for iss in issues:
        code = iss.get("deny_code", "")
        # เพิ่ม causes/fixes จาก analysis
        for f in analysis["findings"]:
            if code in f and f not in iss["causes"]:
                iss["causes"].insert(0, f)
        for w in analysis["warnings"]:
            if w not in iss["causes"]:
                iss["causes"].append(w)

    fmt_num = lambda n: f"{int(n):,}" if n else "0"
    today = datetime.now().strftime("%d/%m/%Y")

    return {
        "rep_no": c["rep_no"],
        "hn": c["hn"],
        "an": c["an"],
        "pid": c["pid"],
        "right": c["fund"],
        "admit": c["admit"],
        "discharge": c["discharge"],
        "los": c["los"],
        "hcode": c["hcode"],
        "hmain": c["hmain"],
        "href": c["href"],
        "drg": c["drg"],
        "rw": c["rw"],
        "status": "DENY",
        "central_reimburse": fmt_num(c["central_reimburse"]),
        "charge": fmt_num(c["charge"]),
        "expected_payment": fmt_num(c["expected_payment"]),
        "actual": fmt_num(c["actual"]),
        "loss": fmt_num(c["loss"]),
        "issues": issues,
        "actions": actions,
        "recommendation_a": "แก้ข้อมูลใน FDH แล้ว Resubmit",
        "recommendation_b": "ยื่นอุทธรณ์พร้อมเอกสาร clinical (ถ้า resubmit ไม่ผ่าน)",
        "report_date": today,
        # Smart analysis extras
        "smart_findings": analysis["findings"],
        "smart_warnings": analysis["warnings"],
        "smart_optimizations": analysis["optimizations"],
    }


def claim_to_appeal_data(c):
    """Convert parsed claim dict → appeal letter data dict."""
    # Smart analysis
    analysis = smart_analyze(c)

    # Build deny_codes table
    deny_codes = []
    for i, code in enumerate(c["fund_main"]):
        key = code.strip()
        meaning = DENY_MEANINGS.get(key, key)
        subfund = c["fund_sub"][i] if i < len(c["fund_sub"]) else "-"
        deny_codes.append({
            "code": key,
            "meaning": meaning,
            "item": subfund,
            "value": "-",
        })

    # Build justifications — enriched with smart appeal_points
    justifications = []
    appeal_pts = analysis.get("appeal_points", [])
    ap_idx = 0  # track which appeal point to use

    if any("IP" in code for code in c["fund_main"]):
        # ใช้ appeal_point ที่ smart_analyze สร้างให้ (ถ้ามี)
        smart_text = next((p for p in appeal_pts if "ผู้ป่วย" in p or "Refer" in p or "admit" in p.lower()), None)
        justifications.append({
            "title": f"{len(justifications)+1}. ความจำเป็นทาง clinical ในการรับเป็นผู้ป่วยใน",
            "text": smart_text or (
                "ผู้ป่วยรายนี้เข้ารับการรักษาด้วยอาการ [ระบุอาการ] "
                "ตรวจพบ [ระบุผลตรวจ] มีความจำเป็นต้องรับไว้เป็นผู้ป่วยในเพื่อทำหัตถการ "
                "และดูแลหลังทำหัตถการ ดังปรากฏตามเวชระเบียนแนบ"),
        })
    if any("HC09" in code for code in c["fund_main"]):
        smart_text = next((p for p in appeal_pts if "อุปกรณ์" in p or "ADP" in p or "Serial" in p), None)
        justifications.append({
            "title": f"{len(justifications)+1}. กรณีอุปกรณ์และอวัยวะเทียม (HC09)",
            "text": smart_text or (
                "อุปกรณ์ที่ใช้อยู่ในบัญชี สปสช. อนุมัติ "
                "ข้อมูลใน ADP file ได้แก้ไขให้ครบถ้วนแล้ว"),
        })
    if any("HC13" in code for code in c["fund_main"]):
        smart_text = next((p for p in appeal_pts if "Clopidogrel" in p or "DAPT" in p or "GPUID" in p), None)
        justifications.append({
            "title": f"{len(justifications)+1}. กรณียา Clopidogrel (HC13)",
            "text": smart_text or (
                "ยา Clopidogrel เป็นยาต้านเกล็ดเลือดที่จำเป็นหลังทำ PCI "
                "ตาม ACC/AHA Guidelines "
                "การที่ข้อมูลไม่ผ่านเกิดจาก GPUID ไม่ตรง Drug Catalog ซึ่งได้แก้ไขแล้ว"),
        })
    # เพิ่ม RW/clinical justification จาก smart analysis
    rw_point = next((p for p in appeal_pts if "RW" in p or "clinical" in p.lower()), None)
    if rw_point and rw_point not in [j["text"] for j in justifications]:
        justifications.append({
            "title": f"{len(justifications)+1}. ความจำเป็นทางการแพทย์",
            "text": rw_point,
        })
    if not justifications:
        justifications.append({
            "title": "1. ข้อชี้แจง",
            "text": "[ระบุเหตุผลทาง clinical ที่สนับสนุนการเบิก]",
        })

    return {
        **HOSPITAL,
        "patient_name": c["patient_name"] or "[ชื่อผู้ป่วย]",
        "pid": c["pid"],
        "hn": c["hn"],
        "an": c["an"],
        "right": c["fund"],
        "admit": c["admit"],
        "discharge": c["discharge"],
        "pdx": "[ระบุ ICD-10]",
        "pdx_name": "[ระบุชื่อโรค]",
        "procedures": "[ระบุ ICD-9-CM + ชื่อหัตถการ]",
        "drg": c["drg"],
        "rw": c["rw"],
        "charge": f'{int(c["central_reimburse"] or c["charge"]):,}',
        "deny_codes": deny_codes,
        "justifications": justifications,
        "corrections": [
            "แก้ไข ADP file: เพิ่ม TYPE, CODE, SERIALNO ตาม NHSO Device Catalog",
            "แก้ไข DRU file: ปรับ GPUID ตาม TMT Drug Catalog",
            "ตรวจสอบ IPD file ครบถ้วน",
            "ตรวจสอบ Authen Code และเอกสาร Refer",
        ],
        "attachments": [
            "สำเนาเวชระเบียนผู้ป่วยใน",
            "รายงานผลหัตถการ",
            "ผล EKG / Lab",
            "ใบส่งตัว (ถ้ามี)",
            "Authen Code",
            "เอกสารอุปกรณ์ (Lot/Serial)",
        ],
        "report_date": "...... ................. 2569",
    }


def run_pipeline(csv_path, output_dir=None):
    """Main pipeline: CSV → parse → generate DOCX for all denied cases."""
    # Add parent dir to path for imports
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    from scripts.docx_generators import generate_deny_report, generate_appeal_letter

    # Read CSV
    with open(csv_path, encoding="utf-8-sig") as f:
        content = f.read()

    # Parse
    t0 = time.time()
    claims = parse_csv_rows(content)
    t_parse = time.time() - t0

    denied = [c for c in claims if c["is_denied"]]
    passed = [c for c in claims if not c["is_denied"]]

    if not output_dir:
        output_dir = Path(csv_path).parent / "claim_reports"
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Generate DOCX for each denied case
    t1 = time.time()
    generated = []
    for c in denied:
        an_safe = c["an"].replace("/", "-").replace(" ", "")

        report_path = output_dir / f"Deny_Report_{an_safe}.docx"
        appeal_path = output_dir / f"Appeal_{an_safe}.docx"

        report_data = claim_to_report_data(c)
        appeal_data = claim_to_appeal_data(c)

        generate_deny_report(report_data, str(report_path))
        generate_appeal_letter(appeal_data, str(appeal_path))

        generated.append({
            "an": c["an"],
            "hn": c["hn"],
            "drg": c["drg"],
            "rw": c["rw"],
            "loss": c["loss"],
            "deny_codes": c["fund_main"],
            "report": str(report_path),
            "appeal": str(appeal_path),
        })
    t_gen = time.time() - t1

    # Summary
    total_loss = sum(c["loss"] for c in denied)

    print(f"\n{'='*60}")
    print(f"  AUTO CLAIM PIPELINE — RESULT")
    print(f"{'='*60}")
    print(f"  CSV         : {csv_path}")
    print(f"  Total cases : {len(claims)}")
    print(f"  Denied      : {len(denied)}")
    print(f"  Passed      : {len(passed)}")
    print(f"  Total loss  : {total_loss:,.0f} baht")
    print(f"{'─'*60}")
    print(f"  Parse time  : {t_parse:.3f}s")
    print(f"  DOCX time   : {t_gen:.3f}s ({len(denied)*2} files)")
    print(f"  Total time  : {t_parse+t_gen:.3f}s")
    print(f"  Output dir  : {output_dir}")
    print(f"{'='*60}")

    if denied:
        print(f"\n  DENIED CASES (sorted by loss):")
        print(f"  {'AN':<15} {'DRG':<8} {'RW':<8} {'Loss':>12}  Deny Codes")
        print(f"  {'─'*65}")
        for c in sorted(denied, key=lambda x: x["loss"], reverse=True):
            codes = ",".join(c["fund_main"])
            print(f"  {c['an']:<15} {c['drg']:<8} {c['rw']:<8.4f} {c['loss']:>12,.0f}  {codes}")

    return {
        "total": len(claims),
        "denied": len(denied),
        "passed": len(passed),
        "total_loss": total_loss,
        "generated": generated,
        "time_parse": t_parse,
        "time_gen": t_gen,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/auto_claim_pipeline.py <eclaim.csv> [output_dir]")
        print("\nReads e-Claim CSV → generates Deny Report + Appeal Letter DOCX")
        print("for every denied case. Fully automatic, no AI needed.")
        sys.exit(1)

    csv_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None
    run_pipeline(csv_path, out_dir)
