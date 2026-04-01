---
name: deny-analyzer
description: >
  วิเคราะห์ claim ที่ถูก deny จาก สปสช. หาสาเหตุรากของปัญหา
  แนะนำวิธีแก้ไข และประเมินโอกาสสำเร็จถ้า appeal
---

# Deny Analyzer Skill

## Overview
วิเคราะห์ claim ที่ถูก deny จาก สปสช. หาสาเหตุรากของปัญหา
แนะนำวิธีแก้ไข และประเมินโอกาสสำเร็จถ้า appeal

## When to trigger
- User ป้อน claim ที่ถูก deny (deny code + reason)
- User ถามว่า "ทำไม claim นี้ถูก deny"
- User ต้องการ appeal claim
- Denial Fighter Agent เรียกใช้ใน Step 2-3

## Input format
```
Deny Code: [รหัส deny จาก สปสช.]
Deny Reason: [เหตุผลที่ สปสช. ระบุ]
ICD-10 Primary: [รหัสโรคหลัก]
ICD-10 Secondary: [รหัสโรคร่วม ถ้ามี]
Procedure Codes: [รหัสหัตถการ]
DRG: [กลุ่มวินิจฉัยโรคร่วม]
Charge Amount: [จำนวนเงิน]
Clinical Notes: [บันทึกทางคลินิก ถ้ามี]
```

---

## Analysis Workflow

### Step 1: จำแนกประเภท deny
ดู deny code + reason text แล้วจัดหมวดหมู่:

| Category | ตัวอย่าง deny reason | Recovery chance |
|----------|---------------------|----------------|
| Coding Error | ICD ไม่ตรง, DRG ผิด, procedure ไม่ match | 70-90% |
| Document Missing | เอกสารไม่ครบ, ไม่มี pre-auth | 60-85% |
| Eligibility | สิทธิ์ไม่ตรง, CID ผิด | 40-60% |
| Timeline | ส่งเกินกำหนด | 20-40% |
| Clinical Criteria | ไม่เข้าเกณฑ์, admission ไม่จำเป็น | 50-70% |

### Step 2: วิเคราะห์สาเหตุราก

**ถ้า Coding Error:**
- ตรวจ ICD-10 ว่าตรงกับ clinical notes ไหม
- ดู `references/nhso-rules/icd10-common-errors.md`
- ตรวจว่า procedure code สอดคล้องกับ diagnosis ไหม
- ตรวจ DRG grouping ถูกต้องไหม
- ตรวจ CC/MCC ที่อาจขาด → อ้างอิง `knowledge/core-rules.md`

**ถ้า Document Missing:**
- ระบุว่าขาดเอกสารอะไร (ใบรับรองแพทย์? Pre-authorization? ผลตรวจ lab?)
- อ้างอิง `references/nhso-rules/eclaim-system-guide.md` สำหรับเอกสารที่ต้องแนบแต่ละ tab

**ถ้า Eligibility:**
- CID ถูกต้องไหม (13 หลัก + checksum)
- สิทธิ์ยังไม่หมดอายุ
- ไม่ซ้ำซ้อนกับสิทธิ์อื่น
- Authen Code มี + ไม่หมดอายุ
- ปีงบ 69: ตรวจ W305 แทน C30

**ถ้า Timeline:**
- IPD ≤30 วัน / OPD ≤15 วัน หลัง D/C
- Fast track ≤24 ชม.
- เกินกำหนด → ประเมินว่าขอผ่อนผันได้ไหม

**ถ้า Clinical Criteria:**
- ตรวจเวชระเบียนว่าสนับสนุน admission หรือไม่
- ตรวจ LOS เหมาะสมไหม (Trim Low/High)
- อ้างอิง `knowledge/[department].md` สำหรับ clinical criteria เฉพาะแผนก

### Step 3: แนะนำ action
ตาม decision matrix:

| Condition | Action |
|-----------|--------|
| confidence > 85% + coding error | **AUTO_FIX** (ส่งเลย แจ้ง LINE) |
| confidence 60-85% | **APPEAL** (ต้องคน review) |
| confidence < 60% + มูลค่าต่ำ | **WRITE_OFF** (เก็บ pattern) |
| eligibility issue | **ESCALATE** ให้เจ้าหน้าที่สิทธิ์ |
| clinical criteria dispute | **ESCALATE** ให้แพทย์ |
| มูลค่า > 50,000 | **FLAG PRIORITY** เสมอ |

### Step 4: สร้าง output

---

## Output format

```json
{
  "claim_id": "CLM-2026-001",
  "category": "coding_error",
  "severity": "high",
  "root_cause": "ICD-10 primary J18.9 (Pneumonia, unspecified) ไม่สอดคล้องกับ procedure Thoracoscopy (34.21) ควรใช้ J93.9 (Pleural effusion) หรือ J86.9 (Empyema) แทน",
  "correct_icd10": "J86.9",
  "missing_documents": [],
  "recovery_chance": 0.85,
  "recommended_action": "auto_fix",
  "appeal_argument": null,
  "confidence": 0.88,
  "estimated_recovery": 15000
}
```

---

## Common Deny Patterns (Quick Reference)

### DRG Grouper Errors

| Error | สาเหตุ | Fix |
|-------|--------|-----|
| 1 | ไม่มี PDx | ใส่ PDx ใน DIA file (DXTYPE=1) |
| 2 | ICD-10 ไม่ valid | ตรวจ code กับ ICD-10-TM library |
| 3 | PDx ไม่ยอมรับ | ห้ามใช้ V/W/X/Y codes เป็น PDx |
| 4 | PDx ไม่ตรงอายุ | P-codes สำหรับ newborn เท่านั้น |
| 5 | PDx ไม่ตรงเพศ | N40 (BPH) ในผู้หญิง |
| 7 | เพศผิด | แก้ข้อมูลเพศ |
| 8 | Discharge type ผิด | แก้ DISCHT |
| 9 | LOS error | ตรวจ DATEADM/DATEDSC |

### C-Code Quick Fix

| C-Code | สาเหตุ | Fix |
|--------|--------|-----|
| C-438 | สิทธิประโยชน์ไม่ตรง | ตรวจสิทธิ์ → เลือกให้ตรง |
| C30/W305 | ไม่พบการปิดสิทธิ์ | ตรวจ Authen Code |
| C555 | OP REFER error | ตรวจรหัส refer |
| Drug mismatch | รหัสยาไม่ตรง | Map Hosp Drug Code → TMT |
| Lab mismatch | รหัส Lab ไม่ตรง | Map กับ FDH standard |
| ADP error | รหัสอุปกรณ์ผิด | TYPE 3/4/5, lot number ตรง GPO VMI |

### Dx-Proc Mismatch (พบบ่อยสุด)

| สถานการณ์ | ปัญหา | Fix |
|-----------|-------|-----|
| Acute MI + ไม่มี PCI | Group เป็น medical MI (RW ต่ำ) | เพิ่ม 36.06/36.07 |
| PCI + chronic IHD | RW ต่ำกว่า acute + PCI | เปลี่ยน PDx → I21.x |
| Pneumonia + Thoracoscopy | Dx-Proc ไม่สัมพันธ์ | เพิ่ม J91 (Pleural effusion) |
| Chemo + ไม่มี cancer PDx | Grouper reject | ใส่ C-code เป็น PDx |

### Timing Rules

| ประเภท | กำหนด | ผลถ้าเกิน |
|--------|-------|----------|
| Fast track | ≤24 ชม. | สปสช. จ่ายใน 72 ชม. |
| IPD ปกติ | ≤30 วัน | จ่ายปกติ |
| OPD ปกติ | ≤15 วัน | จ่ายปกติ |
| เกินกำหนด | >30 วัน | ลดอัตราจ่าย / reject |

---

## ปีงบ 69 Updates (สำคัญ)

อ้างอิง `references/youtube-extracted/zSUuHM9Y2Vk/analysis.md`:

- **Zero C system** — ไม่มี C error แบบเดิม จ่าย 0 บาทต่อรายการแทน reject ทั้ง case
- **W305 แทน C30** — ระบบใหม่สำหรับปิดสิทธิ์
- **DRG v6** — version ใหม่ ตรวจ compatibility
- **AI/OCR ตรวจสอบ** เครื่องมือแพทย์และ claim
- **อุทธรณ์ได้ 2 ครั้ง** (ครั้งละ 15 วันทำการ)
- **IP Base Rate:** ในเขต 8,350 / นอกเขต 9,600 บาท/Adj.RW

---

## References ที่ต้องอ่าน

| File | ใช้สำหรับ |
|------|----------|
| `knowledge/deny-fixes.md` | C-code solutions, DRG denials, appeal template |
| `knowledge/core-rules.md` | DRG grouping, 16-file validation, CC/MCC codes |
| `references/nhso-rules/eclaim-system-guide.md` | e-Claim system, tabs, Drug Catalog |
| `references/nhso-rules/43-file-spec.md` | 43-file validation, DATA_CORRECT |
| `references/nhso-rules/deny-codes.md` | Full deny code list (ต้องสร้าง) |
| `references/nhso-rules/icd10-common-errors.md` | ICD-10 common mistakes (ต้องสร้าง) |
| `references/hospital-data/deny-patterns.md` | Historical deny patterns (สร้างจาก data) |
| `references/hospital-data/successful-appeals.md` | Cases ที่ appeal สำเร็จ (feedback loop) |
| `references/youtube-extracted/zSUuHM9Y2Vk/analysis.md` | ปีงบ 69 changes |
| `references/youtube-extracted/v9ZPwJhBqoc/analysis.md` | หน่วยนวัตกรรม billing |
| `knowledge/[department].md` | Department-specific rules (11 files) |

---

## Important Rules

1. **ห้าม hallucinate ICD code** — ถ้าไม่แน่ใจ ให้ confidence ต่ำ + แนะนำ escalate
2. **ต้องอ้างอิง deny code จาก deny-codes.md เสมอ**
3. **Clinical notes เป็นข้อมูลผู้ป่วย ห้ามเปิดเผยออกนอกระบบ** (PDPA)
4. **ถ้า claim มูลค่าสูง (> 50,000 บาท) ให้ flag เป็น priority เสมอ**
5. **ทุก output ต้องมี confidence score** ห้ามข้าม
6. **Code ต้อง based on documented clinical findings** — ห้ามแนะนำ upcode

---

## Integration with Denial Fighter Agent

Agent เรียกใช้ skill นี้ใน:
- **Step 2 (Classify):** จำแนกประเภท deny + severity scoring
- **Step 3 (Analyze):** วิเคราะห์ root cause + แนะนำ action

Output ส่งต่อไปยัง:
- **→ icd-coding** (ถ้า coding error → แนะนำ code ใหม่)
- **→ claim-validator** (ตรวจก่อน resubmit)
- **→ appeal-drafter** (ร่างหนังสืออุทธรณ์)
