---
name: icu-checker
description: "ตรวจสอบเคส ICU/NICU ก่อนส่งเบิก สปสช. ใช้ skill นี้เมื่อ: มีเคส ICU ที่ต้องส่งเบิก, ตรวจสอบ ventilator coding, CC/MCC optimization, ICU admission criteria, หรือเมื่อพูดถึง ICU, NICU, วิกฤต, ventilator, เครื่องช่วยหายใจ, sepsis, respiratory failure, acute kidney injury, ผู้ป่วยหนัก"
---

# ICU/NICU Claim Checker

ตรวจสอบเคส ICU/NICU — ventilator coding, CC/MCC completeness, severity scoring

## เมื่อได้รับเคสมาตรวจ

### Step 1: รวบรวมข้อมูล
- Principal Diagnosis, Secondary Dx ทั้งหมด
- ICU admission criteria (ทำไมต้อง ICU)
- Ventilator: intubation time, extubation time, total hours
- Severity scores: APACHE II/III, SOFA, GCS
- NICU: birthweight, gestational age, APGAR
- ICU LOS vs total LOS

### Step 2: ตรวจ 8 Checkpoints
อ่าน `references/validation-rules.md`

### Step 3: แสดงผล (เหมือน cathlab pattern)

## Reference Files
| File | อ่านเมื่อ |
|------|----------|
| `references/validation-rules.md` | ทุกเคส |
| `references/cc-mcc-codes.md` | optimize CC/MCC |
| `references/ventilator-coding.md` | เคสใส่ ventilator |
| `references/nicu-rules.md` | เคส NICU |
| `references/deny-fixes.md` | เคสติด deny |
