---
name: icd-coding
description: ช่วย coding ICD-10-TM และ ICD-9-CM จาก clinical notes ภาษาไทย — ตรวจรหัส, แนะนำ CC/MCC, จับคู่ Dx-Proc, เพิ่ม DRG weight
---

# ICD Coding Assistant

> แปลง clinical notes ภาษาไทย → ICD-10-TM / ICD-9-CM codes พร้อมเหตุผล
> ช่วย coder ลดเวลา + ลด coding error + เพิ่ม DRG weight

## Trigger Keywords
icd, รหัสโรค, coding, icd-10, icd-9, diagnosis, procedure, cc, mcc, drg, pdx, sdx, clinical notes, แปลงรหัส

---

## Workflow

### Step 1: รับ Input

รับได้ 2 แบบ:

**แบบ 1: Clinical Notes (ภาษาไทย)**
```
ผู้ป่วยชาย 65 ปี มาด้วยเจ็บหน้าอกรุนแรง 2 ชม.
EKG: ST elevation V1-V4
Troponin I: 15.2 ng/ml (สูงมาก)
Echo: EF 35%, anterior wall hypokinesis
ทำ primary PCI ใส่ stent LAD 1 ตัว
มีประวัติ DM, HT, CKD stage 3
```

**แบบ 2: รหัสที่มีอยู่แล้ว (ตรวจสอบ)**
```
PDx: I21.0
SDx: I10, E11.9
Proc: 36.06
```

### Step 2: วิเคราะห์ Clinical Notes

ถ้าได้ clinical notes → แปลงเป็น codes:

1. **หา Principal Diagnosis (PDx)**
   - โรคหลักที่ทำให้ admit / มารับบริการ
   - ใช้ code ที่ specific ที่สุด (4th-5th character)
   - ห้ามใช้: V/W/X/Y codes เป็น PDx, symptom codes ถ้ามี definitive dx

2. **หา Secondary Diagnosis (SDx)**
   - Comorbidities ทั้งหมดที่มีผลต่อการรักษา
   - **เน้น CC/MCC** ที่เพิ่ม DRG weight

3. **หา Procedure Codes**
   - ICD-9-CM สำหรับทุก procedure ที่ทำ
   - ต้อง match กับ PDx (Dx-Proc consistency)

### Step 3: CC/MCC Optimization

อ้างอิง `knowledge/core-rules.md` — ตรวจทุกเคส IPD:

**MCC (Major CC) — เพิ่ม RW 20-40%:**

| Code | Description | ดูจากอะไร |
|------|-------------|----------|
| A41.x | Sepsis (ระบุ organism) | Blood culture, ไข้สูง, WBC สูง |
| R65.2x | Severe sepsis | Sepsis + organ dysfunction |
| J96.0x | Acute respiratory failure | ใส่ ventilator, O2 sat ต่ำ |
| N17.x | Acute kidney injury | Cr สูงขึ้นเฉียบพลัน |
| I50.2x | Acute systolic HF | EF <40% + อาการเฉียบพลัน |
| I50.3x | Acute diastolic HF | EF ≥50% + อาการเฉียบพลัน |
| N18.4 | CKD stage 4 | eGFR 15-29 |
| J44.1 | COPD acute exacerbation | COPD + acute worsening |

**CC — เพิ่ม RW 5-15%:**

| Code | Description | ดูจากอะไร |
|------|-------------|----------|
| E11.2-E11.6 | DM type 2 with complications | Lab: HbA1c, Cr, eye exam |
| N18.3 | CKD stage 3 | eGFR 30-59 |
| I48.x | Atrial fibrillation | EKG |
| E87.x | Electrolyte disorders | Lab: Na, K, Ca |
| D64.x | Anemia | Hb/Hct |

**ไม่มีผลต่อ RW (อย่า code เพื่อเพิ่ม weight):**

| Code | Description |
|------|-------------|
| I10 | Essential hypertension |
| E78.5 | Dyslipidemia |

**กฎสำคัญ:**
- MCC 1 ตัว = RW สูงสุดในกลุ่มแล้ว (ไม่ต้อง stack)
- CC Exclusion: บาง SDx ถูกตัดจาก CC เมื่อเกี่ยวกับ PDx → ตรวจ Appendix F2
- **Code ทุก comorbidity ที่มีจริง** — ไม่ใช่แค่ที่ส่งผลต่อ DRG

### Step 4: Dx-Proc Consistency Check

ตรวจว่า PDx สอดคล้องกับ procedures:

| PDx Category | Expected Procedures | ถ้าไม่มี |
|-------------|--------------------|---------|
| I21.x (Acute MI) | 36.06/36.07 (PCI) หรือ 36.1x (CABG) | OK ถ้า medical treatment |
| I20.0 (Unstable angina) | 36.06 (PCI) | ถ้าทำ PCI ควรเปลี่ยน PDx เป็น I21.x? |
| C-codes (Cancer) | 99.25 (Chemo) หรือ surgical | ต้องมี cancer PDx ถ้า claim chemo |
| N18.5 (CKD stage 5) | 39.95 (Hemodialysis) | OK |
| J18.x (Pneumonia) | ไม่ควรมี Thoracoscopy | ถ้ามี → เพิ่ม Pleural effusion (J91) |

### Step 5: Output

```
══════════════════════════════════════
  ICD CODING RECOMMENDATION
══════════════════════════════════════

📋 จาก Clinical Notes:
"ผู้ป่วยชาย 65 ปี STEMI anterior wall..."

──────────────────────────────────────
🏥 PRINCIPAL DIAGNOSIS (PDx)
──────────────────────────────────────
I21.0 — Acute transmural MI of anterior wall
เหตุผล: ST elevation V1-V4 + Troponin สูง = STEMI anterior

──────────────────────────────────────
📋 SECONDARY DIAGNOSIS (SDx)
──────────────────────────────────────
1. I50.21 — Acute systolic HF (EF 35%) ⭐ MCC
   เหตุผล: EF <40% + acute presentation
   Impact: MCC → RW +20-40%

2. E11.65 — DM type 2 with hyperglycemia ⭐ CC
   เหตุผล: ประวัติ DM (ใช้ code ที่ specific กว่า E11.9)

3. N18.3 — CKD stage 3 ⭐ CC
   เหตุผล: ประวัติ CKD stage 3

4. I10 — Essential HT
   เหตุผล: ประวัติ HT (ไม่มีผลต่อ RW)

──────────────────────────────────────
🔪 PROCEDURES
──────────────────────────────────────
1. 36.06 — Insertion of non-drug-eluting coronary stent
   เหตุผล: PCI ใส่ stent LAD
   Dx match: ✅ I21.0 + 36.06 = Acute MI + PCI

──────────────────────────────────────
💡 OPTIMIZATION
──────────────────────────────────────
1. ⚠️ เปลี่ยน E11.9 → E11.65 (DM with hyperglycemia)
   เหตุผล: E11.9 ไม่มีผลเป็น CC, แต่ E11.65 เป็น CC
   ต้องมี: blood sugar > 250 mg/dL documented

2. ✅ I50.21 เป็น MCC อยู่แล้ว → RW สูงสุด

──────────────────────────────────────
📊 DRG ESTIMATE
──────────────────────────────────────
Expected DRG: 05051 (PCI + Acute MI + MCC)
Estimated RW: ~4.2
Base Rate: 8,350 บาท/RW (ปีงบ 69)
Estimated payment: ~35,070 บาท
══════════════════════════════════════
```

---

## Department-Specific Coding

อ้างอิง knowledge files ตามแผนก:

| แผนก | Knowledge File | รหัสที่ใช้บ่อย |
|------|---------------|---------------|
| Cath Lab | `knowledge/cath-lab.md` | I21.x, I20.x, 36.0x, 37.2x |
| OR | `knowledge/or-surgery.md` | Various surgical codes |
| Chemo | `knowledge/chemo.md` | C-codes, 99.25 |
| Dialysis | `knowledge/dialysis.md` | N18.x, 39.95 |
| ICU/NICU | `knowledge/icu-nicu.md` | J96.x, ventilator codes |
| ER/UCEP | `knowledge/er-ucep.md` | Emergency codes |
| ODS/MIS | `knowledge/ods-mis.md` | Same-day surgery codes |
| OPD/NCD | `knowledge/opd-ncd.md` | E11.x, I10, chronic codes |
| Rehab | `knowledge/rehab-palliative.md` | Z50.x, rehabilitation |

---

## Rules สำคัญ

1. **ใช้ code ที่ specific ที่สุดเสมอ** — 4th/5th character
2. **E11.9 → ไม่เป็น CC** — ต้องระบุ complication (E11.2x-E11.6x)
3. **I50.9 → ไม่เป็น CC** — ต้องระบุ systolic/diastolic/combined + acute/chronic
4. **PDx ต้อง code ตาม clinical reality** — ไม่ upcode
5. **ทุก code ต้องมี documentation สนับสนุน** ในเวชระเบียน
6. **DRG v6 (ปีงบ 69)** — ตรวจว่า code ที่ใช้ compatible กับ DRG version ใหม่

---

## Integration

- **→ claim-validator**: ส่ง codes ที่แนะนำไปตรวจ 8 checkpoints
- **→ deny-analyzer**: เมื่อ deny เพราะ coding error → ส่งกลับมาที่นี่แนะนำ code ใหม่
