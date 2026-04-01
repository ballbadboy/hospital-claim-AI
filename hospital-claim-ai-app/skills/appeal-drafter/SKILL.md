---
name: appeal-drafter
description: ร่างหนังสืออุทธรณ์ claim ถูก deny ส่ง สปสช. — ภาษาราชการไทย, อ้างอิงหลักเกณฑ์, แนะนำเอกสารแนบ, พร้อมส่ง
---

# Appeal Drafter

> ร่างหนังสืออุทธรณ์ภาษาราชการไทยที่พร้อมส่ง สปสช.
> อ้างอิงหลักเกณฑ์ทางการ + เหตุผล clinical + เอกสารประกอบ

## Trigger Keywords
อุทธรณ์, appeal, ร่างหนังสือ, ขออุทธรณ์, ทบทวน, ส่งใหม่, ขอทบทวน, PPFS, eMA

---

## Workflow

### Step 1: รับข้อมูล
รับจาก deny-analyzer หรือถามผู้ใช้:
- ข้อมูลผู้ป่วย: HN, AN, ชื่อ, วันที่ admit/discharge
- การวินิจฉัย: PDx + SDx (ICD-10) + ชื่อโรค
- หัตถการ: Procedures (ICD-9-CM) + ชื่อ
- Deny reason: C-code หรือ deny text
- Root cause (จาก deny-analyzer)

### Step 2: เลือก Appeal Strategy

| สถานการณ์ | Strategy | ช่องทาง |
|-----------|----------|--------|
| Data error (C10-C49) | **แก้ไขข้อมูลส่งใหม่** | e-Claim / 43 แฟ้ม + DATA_CORRECT |
| DRG mismatch | **ขอทบทวนผล DRG** | หนังสือถึง สปสช. เขต |
| Clinical disagreement | **อุทธรณ์เป็นทางการ** | หนังสือทางการ + เอกสาร clinical |
| Post-audit deny | **ขอทบทวนผล audit** | ระบบ PPFS / eMA |
| Late submission | **ขอผ่อนผัน** | หนังสือ + เหตุผล |

### Step 3: ร่างหนังสือ

ใช้ template จาก `knowledge/deny-fixes.md` + ปรับตาม case:

**กฎการร่าง:**
- ภาษาราชการไทย (สุภาพ, เป็นทางการ)
- อ้างอิงประกาศ/หลักเกณฑ์ สปสช. ที่เกี่ยวข้อง
- เหตุผล clinical ชัดเจน (ไม่กำกวม)
- ระบุเอกสารแนบ

### Step 4: Output — หนังสืออุทธรณ์

```
══════════════════════════════════════
  APPEAL LETTER (DRAFT)
══════════════════════════════════════

ที่ [เลขหนังสือ]
                        [ชื่อ รพ.]
                        วันที่ [วันที่]

เรื่อง  ขอทบทวนผลการตรวจสอบการขอรับค่าใช้จ่ายเพื่อบริการสาธารณสุข

เรียน  ผู้อำนวยการสำนักงานหลักประกันสุขภาพแห่งชาติ เขต [X] [ชื่อเขต]

        ตามที่ [ชื่อ รพ.] รหัสหน่วยบริการ [HOSPCODE] ได้ส่งข้อมูล
การขอรับค่าใช้จ่ายเพื่อบริการสาธารณสุข สำหรับผู้ป่วย

        ชื่อ-สกุล    [ชื่อผู้ป่วย]
        HN           [หมายเลข HN]
        AN           [หมายเลข AN]
        วันที่รับเข้า  [วันที่ admit]
        วันที่จำหน่าย  [วันที่ discharge]
        การวินิจฉัย   [ICD-10 code] [ชื่อโรค]
        หัตถการ      [ICD-9-CM code] [ชื่อหัตถการ]

        ทางโรงพยาบาลได้รับแจ้งว่าข้อมูลดังกล่าวไม่ผ่านการตรวจสอบ
เนื่องจาก [ระบุ deny reason / C-code] ทั้งนี้ ขอชี้แจงดังนี้

        1. [เหตุผลทาง clinical]
           [อธิบาย clinical context ที่สนับสนุน]

        2. [อ้างอิงหลักเกณฑ์]
           ตามประกาศสำนักงานหลักประกันสุขภาพแห่งชาติ
           เรื่อง [ชื่อประกาศ] ข้อ [X] กำหนดว่า [อ้างข้อความ]

        3. [เอกสารสนับสนุน]
           ดังปรากฏตามเอกสารแนบ

        จึงเรียนมาเพื่อโปรดพิจารณาทบทวนผลการตรวจสอบ
และขอให้ดำเนินการจ่ายชดเชยค่าบริการตามหลักเกณฑ์ที่กำหนด
จะเป็นพระคุณยิ่ง

                        ขอแสดงความนับถือ

                        [ลายเซ็น]
                        ([ชื่อ-สกุล ผอ.รพ.])
                        ตำแหน่ง ผู้อำนวยการโรงพยาบาล [ชื่อ]

เอกสารแนบ:
[✅ รายการเอกสาร]
══════════════════════════════════════
```

### Step 5: แนะนำเอกสารแนบ

เลือกตามประเภท deny:

| Deny Type | เอกสารที่ต้องแนบ |
|-----------|----------------|
| **Coding error** | สำเนาเวชระเบียน (OPD/IPD), ผลตรวจ Lab ที่สนับสนุน diagnosis |
| **DRG mismatch** | สำเนาเวชระเบียน, Operative note, ผล Lab/Imaging |
| **Device/Drug** | ใบรายงานผลหัตถการ, GPO VMI record, Drug Catalog mapping |
| **Cath Lab** | Cath report, EKG, Troponin, Echo report |
| **Surgery** | Operative note, Pathology report |
| **Chemo** | Protocol, Staging, Lab monitoring |
| **ICU** | ICU chart, Ventilator settings, ABG |
| **Dialysis** | Lab (BUN/Cr/eGFR), Dialysis protocol |
| **Clinical audit** | ทุกอย่างข้างต้น + ใบรับรองแพทย์ |

---

## Appeal Timeline (ปีงบ 69)

อ้างอิง `references/youtube-extracted/zSUuHM9Y2Vk/analysis.md`:

| ขั้นตอน | ระยะเวลา |
|---------|---------|
| **อุทธรณ์ครั้งที่ 1** | ภายใน 15 วันทำการ หลังรับแจ้ง deny |
| **สปสช. พิจารณา** | ภายใน 30 วัน |
| **อุทธรณ์ครั้งที่ 2** | ภายใน 15 วันทำการ หลังรับผลครั้งที่ 1 |
| **สปสช. พิจารณาสุดท้าย** | ภายใน 30 วัน |
| **รวมสูงสุด** | **อุทธรณ์ได้ 2 ครั้ง** |

---

## Appeal ผ่านระบบ

### PPFS (Post-Payment Financial Statement)
อ้างอิง `references/nhso-rules/eclaim-system-guide.md`:
- เข้าระบบ PPFS
- Mark Audit → จ่ายเพิ่ม / เรียกคืน
- ขอทบทวนผ่านระบบ PPFS ได้

### eMA (Electronic Medical Audit)
อ้างอิง `references/youtube-extracted/nhso-video-index.md` (video `oPLMLOxJhAg`):
- ตรวจสอบผลเวชระเบียนผ่านระบบ eMA
- ขอทบทวนผ่านระบบ eMA ได้

---

## Clinical Justification Templates

### Template 1: Dx-Proc Mismatch
```
1. ผู้ป่วยรายนี้เข้ารับการรักษาด้วยอาการ [อาการ]
   ตรวจพบ [ผลตรวจ] ซึ่งเข้ากับ [diagnosis]
2. จากการตรวจประเมินโดย [แพทย์เฉพาะทาง] พบว่า
   มีข้อบ่งชี้ในการทำ [procedure] ตามแนวทาง
   เวชปฏิบัติ [guideline name]
3. การวินิจฉัยรหัส [ICD-10] และหัตถการรหัส [ICD-9-CM]
   มีความสอดคล้องทาง clinical ดังที่ปรากฏในเวชระเบียนแนบ
```

### Template 2: CC/MCC Dispute
```
1. ผู้ป่วยมีโรคร่วม [comorbidity] ซึ่งมีผลต่อ
   ความรุนแรงของโรคและการรักษา
2. จากผลตรวจ [Lab/Imaging] เมื่อวันที่ [date]
   พบว่า [ค่าที่ผิดปกติ] ซึ่งสนับสนุนการวินิจฉัยรหัส [ICD-10]
3. โรคร่วมดังกล่าวจัดเป็น [CC/MCC] ตาม Thai DRG v6
   จึงส่งผลต่อ DRG weight และค่าชดเชย
```

### Template 3: Late Submission
```
1. ทางโรงพยาบาลไม่สามารถส่งข้อมูลภายในกำหนดได้
   เนื่องจาก [เหตุผล: ระบบขัดข้อง / เวชระเบียนไม่ครบ / etc.]
2. ปัจจุบันได้แก้ไขปัญหาดังกล่าวเรียบร้อยแล้ว
   และส่งข้อมูลครบถ้วนตามที่แนบมาพร้อมนี้
3. จึงขอให้พิจารณาผ่อนผันการรับข้อมูลเพื่อจ่ายชดเชย
   ตามหลักเกณฑ์ที่กำหนด
```

---

## Knowledge References

| File | ใช้สำหรับ |
|------|----------|
| `knowledge/deny-fixes.md` | Appeal template, C-code solutions |
| `knowledge/core-rules.md` | DRG rules, หลักเกณฑ์อ้างอิง |
| `references/nhso-rules/eclaim-system-guide.md` | PPFS/Statement/ช่องทาง |
| `references/youtube-extracted/zSUuHM9Y2Vk/analysis.md` | ปีงบ 69: อุทธรณ์ 2 ครั้ง, 15 วันทำการ |
| `references/youtube-extracted/R_g1VNkQ65w/analysis.md` | eMA, PPFS ขอทบทวน |
| `knowledge/[department].md` | Department-specific clinical justification |

---

## DOCX Generation (หนังสืออุทธรณ์พร้อมพิมพ์)

สร้างไฟล์ DOCX ภาษาราชการไทยพร้อมพิมพ์ลงนามส่ง สปสช. ด้วย `scripts/generate_appeal.py`:

**วิธีใช้:**
```bash
python scripts/generate_appeal.py [output_path]
# default: docs/appeal_AN69-03556.docx
```

**ฟีเจอร์ DOCX:**
- ฟอนต์ TH SarabunPSK ขนาด 14pt (มาตรฐานราชการ)
- Page margins: top/bottom 2.5cm, left 3cm, right 2.5cm
- ตาราง Patient Info (HN, AN, CID, Dx, Procedures, DRG, RW, charge, สิทธิ)
- ตาราง Deny Codes (รหัส, ความหมาย, รายการที่ถูกปฏิเสธ, มูลค่า)
- ข้อชี้แจง 4 ส่วน: ความจำเป็น clinical, อุปกรณ์ HC09/HC13, ยา Clopidogrel, ข้อมูลที่แก้ไข
- รายการเอกสารแนบ 9 รายการ
- ลงนาม ผอ.รพ.

**Helper Functions:**
- `set_thai_font(run, size, bold)` — ตั้งค่าฟอนต์ไทย
- `add_thai_paragraph(doc, text, size, bold, align, space_after)` — เพิ่มย่อหน้าภาษาไทย
- `add_table_row(table, cells_data, bold_first)` — เพิ่มแถวตาราง
- `generate_appeal_docx(output_path)` — สร้าง DOCX เต็มรูปแบบ

---

## API Integration (Backend)

### Deny Analysis → Auto Appeal Draft
**Endpoint:** `POST /api/v1/cathlab/analyze-deny`
- Input: `CathLabClaim` (ต้องมี `deny_codes`)
- Output: `DenyAnalysis` (มี `appeal_draft` อัตโนมัติ)
- Engine: `core/deny_analyzer.py` → `_generate_appeal_draft(claim, root_cause)`

### AI-Powered Appeal Generation
**Endpoint:** `POST /appeal` (ใน `api/routes.py`)
- Input: `AppealRequest` (hn, an, deny_reason, department, principal_dx, procedures, fund)
- Output: `AppealResponse` (letter_text, supporting_docs, estimated_recovery)
- Engine: `core/ai_engine.py` → `generate_appeal(claim_data, deny_reason, department)`
- AI: เรียก Claude API พร้อม knowledge base ตามแผนก

### Appeal State Machine
```
NONE → DRAFTED → SUBMITTED → APPROVED
                           → REJECTED → RE_DRAFTED → SUBMITTED
```

**State transitions:** `core/state_machine.py`
**Persistence:** `core/repositories.py` → `update_appeal_status(an, new_status)`
**Database:** `claim_records` table → `appeal_status` + `appeal_text` columns

---

## Core Modules

| Module | ไฟล์ | หน้าที่ |
|--------|------|--------|
| Deny Analyzer | `core/deny_analyzer.py` | Root cause + auto appeal draft |
| AI Engine | `core/ai_engine.py` | Claude API → formal appeal letter |
| DOCX Generator | `scripts/generate_appeal.py` | สร้าง DOCX พร้อมพิมพ์ |
| State Machine | `core/state_machine.py` | Appeal status transitions |
| Repository | `core/repositories.py` | DB persistence |
| Models | `core/models.py` | AppealRequest, AppealResponse, AppealStatus |

---

## Integration

- **← deny-analyzer**: รับ root cause + recommendation → ร่าง appeal อัตโนมัติ
- **← ai_engine**: Claude API สร้าง formal letter จาก knowledge base
- **← icd-coding**: รับ recommended codes → ใส่ในหนังสือ
- **→ claim-validator**: หลังแก้ไข → validate ก่อนส่งใหม่
- **→ DOCX output**: สร้างไฟล์พร้อมพิมพ์ลงนาม
- **→ Database**: บันทึก appeal_status + appeal_text
- **→ Audit Log**: ทุก action ถูก log ใน audit trail
