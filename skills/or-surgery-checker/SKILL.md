---
name: or-surgery-checker
description: "ตรวจสอบเคสห้องผ่าตัด (OR/Surgery) ก่อนส่งเบิก สปสช. ผ่าน FDH เพื่อลด Deny rate ใช้ skill นี้เมื่อ: มีเคสผ่าตัดที่ต้องส่งเบิก, ตรวจสอบ DRG coding ศัลยกรรม, เคสผ่าตัดติด Deny, หรือเมื่อพูดถึง OR, surgery, ผ่าตัด, implant, prosthesis, ortho, spine, hernia, appendectomy, cholecystectomy, C-section, ศัลยกรรม"
---

# OR Surgery Claim Checker

ตรวจสอบเคสห้องผ่าตัดก่อนส่งเบิก สปสช. — ครอบคลุม Ortho, Neuro, GI, Vascular, OB/GYN

## เมื่อได้รับเคสมาตรวจ

### Step 1: รวบรวมข้อมูลเคส
- Principal Diagnosis (ICD-10-TM)
- Secondary Diagnoses ทั้งหมด
- Procedure codes (ICD-9-CM) — ลำดับ main procedure ก่อน
- OPTYPE: Major OR(1) / Minor OR(2) / Non-OR(3)
- อุปกรณ์/Implant ที่ใช้ (type, lot, serial, GPO match)
- Anesthesia type (GA/Regional)
- Operative note + consent form status
- วันที่ Admit / Discharge / ส่งเบิก

### Step 2: ตรวจสอบ 8 Checkpoints
อ่าน `references/validation-rules.md` แล้วตรวจทุกข้อ

### Step 3: แสดงผล
```
═══════════════════════════════════════
  OR SURGERY CLAIM CHECK RESULT
═══════════════════════════════════════
Patient: [HN/AN]
Procedure: [main ICD-9-CM] [ชื่อ]
OPTYPE: [Major/Minor/Non-OR]
Expected DRG: [surgical DRG + RW]

─── CRITICAL ──────────────────────────
🔴 [issues]

─── WARNINGS ──────────────────────────
🟡 [warnings]

─── PASSED ────────────────────────────
🟢 [passed items]

─── OPTIMIZATION ──────────────────────
💡 [DRG/CC/MCC suggestions]

Score: [XX%] Ready: [YES/NO]
═══════════════════════════════════════
```

### Step 4: ถ้าเคสติด Deny
อ่าน `references/deny-fixes.md` → แนะนำวิธีแก้ + ร่างอุทธรณ์ถ้าต้องการ

## Reference Files
| File | เนื้อหา | อ่านเมื่อ |
|------|---------|----------|
| `references/validation-rules.md` | 8 checkpoints | ทุกเคส |
| `references/surgical-codes.md` | ICD-9-CM families | เช็ค code |
| `references/implant-catalog.md` | High-value implants + ADP | เคสมี implant |
| `references/deny-fixes.md` | Deny causes + fixes | เคสติด deny |
| `references/drg-surgical.md` | DRG optimization | เพิ่ม RW |

## สิ่งสำคัญ
- ใช้ภาษาไทยเป็นหลัก ยกเว้นศัพท์เทคนิค
- Procedure ลำดับแรก = main procedure → กำหนด DRG group
- Surgical DRG weight สูงกว่า Medical มาก → ต้อง code OR procedure ให้ถูก
- Post-op complications = MCC → code ถ้ามี documentation
