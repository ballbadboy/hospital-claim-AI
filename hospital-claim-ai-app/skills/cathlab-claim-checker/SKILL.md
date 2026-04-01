---
name: cathlab-claim-checker
description: "ตรวจสอบเคส Cath Lab (สวนหัวใจ/PCI/stent) ก่อนส่งเบิก สปสช. ผ่าน FDH เพื่อลด Deny rate ใช้ skill นี้เมื่อ: มีเคสหูหัวใจที่ต้องส่งเบิก, ต้องการตรวจสอบ DRG coding, ต้องการแก้เคสที่ติด Deny/ติด C, ต้องการเขียนหนังสืออุทธรณ์, หรือเมื่อพูดถึง Cath lab, PCI, stent, สวนหัวใจ, AMI, STEMI, NSTEMI, DRG, e-claim, FDH, กองทุน สปสช. ใช้ skill นี้เมื่อพูดถึงจะไม่ใช้อ้างอิง skill ใดอย่างอื่น"
---

# Cath Lab Claim Checker Skill

ตรวจสอบเคสห้องสวนหัวใจ (Cardiac Catheterization Lab) ก่อนส่งเบิก สปสช. ผ่านระบบ FDH เพื่อลด Deny rate และเพิ่มรายได้ให้โรงพยาบาล

## เมื่อได้รับเคสมาตรวจ ให้ทำตามขั้นตอนนี้

### Step 1: รวบรวมข้อมูลเคส
ถามข้อมูลที่ต้องได้ทั้งหมด (ถ้ายังไม่มี):
- Principal Diagnosis (ICD-10-TM code)
- Secondary Diagnoses ทั้งหมด
- Procedure codes (ICD-9-CM) ที่ทำทั้งหมด
- อุปกรณ์ที่ใช้ (stent type BMS/DES, จำนวน, lot number)
- เอกสารที่มี (Troponin, EKG, Cath report, D2B time)
- วันที่ Admit / Discharge
- วันที่ส่งเบิก
- Authen Code status

### Step 2: ตรวจสอบ 8 Checkpoints
อ่าน reference file `references/validation-rules.md` แล้วตรวจตาม 8 checkpoints ทุกข้อ

### Step 3: แสดงผล
แสดงผลในรูปแบบนี้:

```
═══════════════════════════════════════
  CATH LAB CLAIM CHECK RESULT
═══════════════════════════════════════

Patient: [ชื่อ/HN]
Diagnosis: [ICD-10 code] [ชื่อโรค]
Procedures: [ICD-9-CM codes]
Expected DRG: [DRG group + RW estimate]

─── CRITICAL ISSUES (ต้องแก้ก่อนส่ง) ───
🔴 [issue 1]
🔴 [issue 2]

─── WARNINGS (ควรตรวจสอบ) ──────────────
🟡 [warning 1]

─── PASSED ──────────────────────────────
🟢 [passed item 1]
🟢 [passed item 2]

─── OPTIMIZATION TIPS ──────────────────
💡 [suggestion to increase DRG weight]

─── SCORE ──────────────────────────────
Ready to submit: [YES/NO]
Confidence: [XX%]
═══════════════════════════════════════
```

### Step 4: ถ้าเคสติด Deny แล้ว
ถ้าผู้ใช้บอกว่าเคสถูก deny:
1. ถามเหตุผลที่ deny (C-code หรือ reason text)
2. อ่าน `references/deny-fixes.md` เพื่อหาวิธีแก้ตรงจุด
3. แนะนำวิธีแก้ข้อมูลใน FDH/HIS
4. ถ้าต้องอุทธรณ์ ช่วยร่างหนังสืออุทธรณ์

### Step 5: Batch Check (หลายเคสพร้อมกัน)
ถ้าผู้ใช้ upload CSV/Excel หลายเคส:
1. อ่านทีละแถว
2. ตรวจแต่ละเคสตาม Step 2
3. สรุปเป็นตารางรวม: เคสไหน pass, เคสไหนมีปัญหา
4. แนะนำ priority แก้เคสตามมูลค่า claim (แก้เคสแพงก่อน)

## Reference Files

เมื่อต้องการข้อมูลเพิ่มเติม ให้อ่าน reference files ตามหัวข้อ:

| File | เนื้อหา | อ่านเมื่อ |
|------|---------|----------|
| `references/validation-rules.md` | 8 checkpoints + DRG mapping | ทุกเคสที่ตรวจ |
| `references/cardiac-codes.md` | ICD-10-TM + ICD-9-CM codes | ต้องเช็ค code |
| `references/deny-fixes.md` | C-code errors + วิธีแก้ | เคสติด deny |
| `references/drg-cardiac.md` | Thai DRG v6.3 cardiac grouping | ต้องเช็ค DRG weight |
| `references/fdh-16files.md` | FDH 16-file structure | ปัญหาข้อมูล format |
| `references/clinical-criteria.md` | STEMI/NSTEMI/UA criteria | ต้องเช็ค documentation |

## Step 6: Deny Prediction (ทำนายก่อนส่ง)
ถ้าผู้ใช้ต้องการทำนายว่าเคสจะถูก deny หรือไม่:
1. ใช้ข้อมูลจาก Step 1 → วิเคราะห์ 10 Risk Factors:

| RF | ชื่อ | Weight | ตรวจอะไร |
|----|------|--------|----------|
| RF1 | CID Checksum | 5 | เลข 13 หลัก checksum ถูกต้อง |
| RF2 | PDx Valid | 15 | PDx มี + รูปแบบ ICD-10 ถูก |
| RF3 | Dx-Proc Match | 20 | STEMI ต้องมี PCI, PCI ต้องมี acute Dx |
| RF4 | Device Docs | 15 | ADP file TYPE/CODE/Serial ครบ |
| RF5 | Drug Catalog | 10 | TMT/GPUID ตรง Drug Catalog |
| RF6 | Timing | 10 | ส่งภายใน 30 วัน |
| RF7 | Authen Code | 10 | UC ต้องมี Authen Code |
| RF8 | CC/MCC Coding | 5 | ไม่ใช้ unspecified codes (E11.9→E11.65) |
| RF9 | DRG Groupable | 5 | DRG group ได้ไม่ Error |
| RF10 | Charge Reasonable | 5 | ค่ารักษาสมเหตุสมผลกับ DRG |

2. แสดงผล:
```
═══════════════════════════════════════
  DENY PREDICTION
═══════════════════════════════════════
AN: [AN]
Deny Probability: [XX%]
Verdict: [SAFE / CAUTION / HIGH_RISK / ALMOST_CERTAIN]

Risk Factors:
🔴 RF3: Dx-Proc Match (risk: 90) — STEMI ไม่มี PCI
🟡 RF8: CC/MCC Coding (risk: 40) — E11.9 ควรเป็น E11.65
🟢 RF1-RF2, RF4-RF7, RF9-RF10: PASS

Top Risks: [...]
Estimated Loss if Denied: [XX,XXX บาท]
Recommendation: [ส่งได้เลย / แก้ก่อนส่ง / ห้ามส่ง!]
═══════════════════════════════════════
```

### Step 7: Smart Coder (แปลง Clinical Notes → ICD Codes)
ถ้าผู้ใช้ส่ง clinical notes ภาษาไทย/อังกฤษ:
1. วิเคราะห์ text → สกัด diagnosis keywords (STEMI/NSTEMI/UA/CAD)
2. ระบุ wall/territory (anterior, inferior, lateral, posterior)
3. สกัด procedure keywords (PCI, stent, catheterization, angiography)
4. แนะนำ ICD-10 (PDx + SDx) + ICD-9-CM (procedures)
5. เสนอ CC/MCC optimization
6. ประมาณ DRG + RW + expected payment

### Step 8: DRG Lookup
ถ้าผู้ใช้ถาม DRG:
- ค้นหาจาก Cardiac DRG Table (Thai DRG v6.3.3 Appendix G)
- แสดง: RW, WtLOS, OT, Payment Estimate (Base Rate 8,350 บาท/AdjRW ในเขต)

---

## API Endpoints (Backend Integration)

Skill นี้เชื่อมกับ backend API ที่ `api/routes_cathlab.py`:

| Endpoint | Method | ใช้สำหรับ |
|----------|--------|----------|
| `/api/v1/cathlab/check` | POST | ตรวจ 8 checkpoints (Step 2) |
| `/api/v1/cathlab/analyze-deny` | POST | วิเคราะห์ deny + draft appeal (Step 4) |
| `/api/v1/cathlab/parse-eclaim` | POST | Parse e-Claim CSV → validate ทุกเคส (Step 5) |
| `/api/v1/cathlab/drg-lookup/{drg_code}` | GET | DRG lookup: RW, WtLOS, payment (Step 8) |
| `/api/v1/cathlab/batch-optimize` | POST | Batch optimize + priority sort (Step 5) |
| `/api/v1/cathlab/predict-deny` | POST | ทำนาย deny probability (Step 6) |
| `/api/v1/cathlab/smart-code` | POST | Clinical notes → ICD codes (Step 7) |

### Core Modules
| Module | ไฟล์ | หน้าที่ |
|--------|------|--------|
| Validator | `core/cathlab_validator.py` | 8 checkpoint validation engine |
| Deny Analyzer | `core/deny_analyzer.py` | Root cause analysis + appeal draft |
| Deny Predictor | `core/deny_predictor.py` | 10 risk factors → probability score |
| Smart Coder | `core/smart_coder.py` | Thai/EN clinical notes → ICD codes |
| Batch Optimizer | `core/batch_optimizer.py` | Multi-claim priority sorting |
| DRG Calculator | `core/drg_calculator.py` | Cardiac DRG RW table + payment calc |
| e-Claim Parser | `core/eclaim_parser.py` | CSV → CathLabClaim objects |
| Appeal Generator | `scripts/generate_appeal.py` | DOCX appeal letter generation |
| Data Models | `core/cathlab_models.py` | CathLabClaim, CheckResult, DenyAnalysis, DRGInfo |

---

## สิ่งสำคัญ

- **ใช้ภาษาไทยเป็นหลัก** ในการสื่อสารกับผู้ใช้ ยกเว้นศัพท์เทคนิคจะใช้ภาษาอังกฤษ
- **ระบุเหตุผลชัดเจน** ว่าทำไม flag แต่ละ issue
- **ให้วิธีแก้ที่ actionable** ไม่ใช่แค่บอกว่าผิด
- **ถ้าไม่แน่ใจ ให้ถาม** ไม่ใช่เดาเอง
- **เคสฉุกเฉิน (STEMI primary PCI)** ต้องเข้าใจว่า documentation อาจไม่ครบในช่วงแรก → แนะนำให้เพิ่มภายหลังก่อนส่งเบิก
- **Base Rate ปีงบ 69:** ในเขต 8,350 / นอกเขต 9,600 บาท/AdjRW
- **Verdict ของ Deny Prediction:** SAFE (<20%), CAUTION (20-50%), HIGH_RISK (50-80%), ALMOST_CERTAIN (>80%)

## Integration

- **→ deny-analyzer**: เคสถูก deny → วิเคราะห์ root cause + draft appeal
- **→ appeal-drafter**: ต้องอุทธรณ์ → ร่างหนังสือ (text + DOCX)
- **→ deny-predictor**: ทำนาย deny ก่อนส่ง → 10 risk factors
- **→ smart-coder**: clinical notes → ICD codes อัตโนมัติ
- **→ batch-claim-optimizer**: ตรวจหลายเคสพร้อมกัน → priority sort
- **← icd-coding**: รับ recommended codes
- **← claim-validator**: ตรวจ claim ทุกแผนก (ไม่เฉพาะ Cath Lab)
