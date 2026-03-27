---
name: er-ucep-checker
description: "ตรวจสอบเคสฉุกเฉิน (ER/UCEP) ก่อนส่งเบิก สปสช. ใช้ skill นี้เมื่อ: มีเคส ER ที่ต้องส่งเบิก, เคส UCEP, ตรวจสอบ triage level, 72-hour rule, emergency authen code, หรือเมื่อพูดถึง ER, ฉุกเฉิน, UCEP, trauma, อุบัติเหตุ, CPR, resuscitation, chest pain, stroke, accident"
---

# ER/UCEP Claim Checker

ตรวจสอบเคสฉุกเฉิน (ER) และ UCEP ก่อนส่งเบิก — 72-hour rule, triage, authen code

## เมื่อได้รับเคสมาตรวจ

### Step 1: รวบรวมข้อมูล
- Principal Diagnosis (ICD-10-TM)
- Triage level (Red/Orange/Yellow/Green)
- วันเวลา arrival / admission / discharge
- UCEP หรือ UC ปกติ?
- Emergency Authen Code status
- Procedures ที่ทำใน ER
- ER → IPD transition? (admit ภายใน 24 ชม.?)

### Step 2: ตรวจสอบ 8 Checkpoints
อ่าน `references/validation-rules.md`

### Step 3: แสดงผล
```
═══════════════════════════════════════
  ER/UCEP CLAIM CHECK RESULT
═══════════════════════════════════════
Triage: [🔴Red/🟠Orange/🟡Yellow]
UCEP: [YES/NO] | 72hr Window: [OK/EXCEEDED]
Authen: [OK/MISSING]
═══════════════════════════════════════
```

## Reference Files
| File | อ่านเมื่อ |
|------|----------|
| `references/validation-rules.md` | ทุกเคส |
| `references/triage-criteria.md` | เช็ค triage level |
| `references/er-procedure-codes.md` | เช็ค procedure codes |
| `references/ucep-rules.md` | เคส UCEP |
| `references/deny-fixes.md` | เคสติด deny |
