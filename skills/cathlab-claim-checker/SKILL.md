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

## สิ่งสำคัญ

- **ใช้ภาษาไทยเป็นหลัก** ในการสื่อสารกับผู้ใช้ ยกเว้นศัพท์เทคนิคจะใช้ภาษาอังกฤษ
- **ระบุเหตุผลชัดเจน** ว่าทำไม flag แต่ละ issue
- **ให้วิธีแก้ที่ actionable** ไม่ใช่แค่บอกว่าผิด
- **ถ้าไม่แน่ใจ ให้ถาม** ไม่ใช่เดาเอง
- **เคสฉุกเฉิน (STEMI primary PCI)** ต้องเข้าใจว่า documentation อาจไม่ครบในช่วงแรก → แนะนำให้เพิ่มภายหลังก่อนส่งเบิก
