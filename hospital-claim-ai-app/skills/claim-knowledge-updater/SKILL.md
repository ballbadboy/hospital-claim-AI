---
name: claim-knowledge-updater
description: "อัพเดตความรู้ให้ระบบ Hospital Claim AI — รับไฟล์ใหม่ (PDF/markdown/YouTube) แล้วกระจายไปอัพเดตทุกจุดอัตโนมัติ (knowledge, skill references, core modules, SKILL.md) ใช้ skill นี้เมื่อ: เพิ่มความรู้, update knowledge, อัพเดตหลักเกณฑ์, เพิ่ม deny code, เพิ่ม DRG, เพิ่มแผนกใหม่, อัพเดต base rate, เพิ่ม ICD code"
---

# Claim Knowledge Updater

> รับความรู้ใหม่ → อ่าน → สรุป → กระจายไปอัพเดตทุกจุดอัตโนมัติ

## Knowledge Architecture (3 ชั้น)

```
ชั้น 1: SKILL.md              ← วิธีคิด + workflow
ชั้น 2: skills/*/references/   ← ข้อมูลเฉพาะ skill
ชั้น 3: knowledge/ + references/nhso-rules/ ← ข้อมูลกลาง
ชั้น 4: core/*.py              ← logic ใน code
```

## Workflow

### Step 1: ตรวจสอบ Input
รับจากผู้ใช้:
- ไฟล์ใหม่ที่เพิ่มเข้ามา (path)
- หรือ YouTube URL
- หรือข้อความอธิบาย

ถ้าผู้ใช้ไม่บอกประเภท → อ่านเนื้อหาแล้วจำแนกเอง

### Step 2: จำแนกประเภทความรู้

| ประเภท | ตรวจจาก | ตัวอย่าง |
|--------|---------|---------|
| **หลักเกณฑ์ สปสช.** | ประกาศ, ระเบียบ, base rate, งบ | ปีงบ 70 base rate ใหม่ |
| **Deny code / วิธีแก้** | C-code, deny, reject, ปฏิเสธ | C-code ใหม่, deny pattern |
| **ICD / DRG** | ICD-10, ICD-9, DRG, RW, grouper | DRG v7, ICD-10-TM 2026 |
| **Clinical criteria** | guideline, criteria, protocol | ACC/AHA update |
| **Drug catalog** | ยา, TMT, GPUID, drug | Drug Catalog update |
| **Device / Instrument** | stent, implant, อุปกรณ์, GPO VMI | Instrument catalog update |
| **แผนกใหม่** | แผนกที่ยังไม่มี skill | rehab, ODS, MIS |

### Step 3: กระจายอัพเดตตามประเภท

#### A) หลักเกณฑ์ สปสช.
```
1. สรุป → references/nhso-rules/[ชื่อ].md
2. อัพเดต knowledge/core-rules.md (ถ้า base rate/งบ)
3. อัพเดต knowledge/[แผนก].md (ถ้าเฉพาะแผนก)
4. อัพเดต core/drg_calculator.py (ถ้า base rate เปลี่ยน: BASE_RATE_IN_ZONE, BASE_RATE_OUT_ZONE)
5. อัพเดต SKILL.md → Knowledge References table
6. อัพเดต CLAUDE.md → Key Business Rules section
```

#### B) Deny code / วิธีแก้
```
1. เพิ่ม → knowledge/deny-fixes.md
2. เพิ่ม → core/deny_analyzer.py → DENY_CODE_DB dict
3. เพิ่ม → skills/*/references/deny-fixes.md (skill ที่เกี่ยวข้อง)
4. อัพเดต SKILL.md ของ deny-analyzer + cathlab-claim-checker
```

#### C) ICD / DRG
```
1. เพิ่ม → skills/cathlab-claim-checker/references/cardiac-codes.md (ICD)
2. เพิ่ม → skills/cathlab-claim-checker/references/drg-cardiac.md (DRG)
3. เพิ่ม → core/drg_calculator.py → CARDIAC_DRG_TABLE dict (DRG + RW)
4. เพิ่ม → core/smart_coder.py → keyword patterns (ICD ใหม่)
5. เพิ่ม → core/cathlab_validator.py → code sets (STEMI_CODES, PCI_CODES, etc.)
6. เพิ่ม → core/deny_predictor.py → VALID_CARDIAC_PDX_PREFIXES (ถ้า prefix ใหม่)
```

#### D) Drug / Device catalog
```
1. เพิ่ม → references/nhso-rules/drug-catalog-spec.md หรือ instrument-catalog.md
2. เพิ่ม → skills/*/references/instrument-catalog.md
3. อัพเดต core/deny_predictor.py → KNOWN_CATH_DRUGS set (ยาใหม่)
```

#### E) YouTube สปสช.
```
1. /youtube-skill-extractor [URL]
2. สกัด → references/youtube-extracted/[videoID]/
3. อัพเดต nhso-video-index.md
4. อ่านเนื้อหา → จำแนกประเภท → กระจายตาม A-D
```

#### F) แผนกใหม่
```
1. สร้าง knowledge/[แผนก].md
2. สร้าง references/nhso-rules/[แผนก].md
3. สร้าง skills/[แผนก]-checker/SKILL.md + references/
4. เพิ่ม route ใน api/ (ถ้าต้องการ API)
5. อัพเดต CLAUDE.md → Skills table + Project Structure
```

### Step 4: Sync
ทุกครั้งที่แก้ skill → sync ทั้ง 2 ที่:
- **Global:** `~/.claude/skills/[skill]/`
- **Project-local:** `skills/[skill]/`

### Step 5: สรุปผล
แสดงสรุปว่าอัพเดตไฟล์ไหนบ้าง:

```
═══════════════════════════════════════
  KNOWLEDGE UPDATE SUMMARY
═══════════════════════════════════════
ประเภท: [ประเภทความรู้]
แหล่ง: [ไฟล์/URL ที่รับมา]

ไฟล์ที่อัพเดต:
✅ references/nhso-rules/xxx.md (สร้างใหม่)
✅ knowledge/core-rules.md (เพิ่ม section)
✅ core/drg_calculator.py (อัพเดต BASE_RATE)
✅ CLAUDE.md (อัพเดต Business Rules)
✅ Synced: global + project-local

Skills ที่ได้รับผล:
📌 cathlab-claim-checker
📌 deny-analyzer
═══════════════════════════════════════
```

---

## สิ่งสำคัญ

- **อ่านเนื้อหาก่อนจำแนก** — ไม่เดาจากชื่อไฟล์อย่างเดียว
- **อัพเดตทุกจุดที่เกี่ยว** — ไม่ใส่แค่ที่เดียว
- **Sync ทั้ง 2 copies** — global + project-local
- **แสดงสรุป** — ให้ผู้ใช้เห็นว่าแก้ไฟล์อะไรบ้าง
