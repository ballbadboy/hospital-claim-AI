# Hospital Claim AI — คู่มือติดตั้งและใช้งาน

> ระบบ AI ช่วยตรวจ claim + สร้างหนังสืออุทธรณ์อัตโนมัติ
> สำหรับ รพ.พญาไทศรีราชา (11855) เขต 6 ชลบุรี

---

## สารบัญ

1. [ติดตั้ง](#1-ติดตั้ง)
2. [วิธีใช้งาน](#2-วิธีใช้งาน)
3. [คำสั่งลัด](#3-คำสั่งลัด)
4. [โครงสร้างไฟล์](#4-โครงสร้างไฟล์)
5. [Knowledge ที่ติดตั้ง](#5-knowledge-ที่ติดตั้ง)
6. [FAQ](#6-faq)

---

## 1. ติดตั้ง

### 1.1 สิ่งที่ต้องมี

- Python 3.10+
- python-docx (`pip install python-docx`)
- Claude Code CLI (ติดตั้งจาก https://claude.ai/code)
- Git

### 1.2 Clone + Setup

```bash
# Clone repo
git clone <repo-url> "Hospital claim AI"
cd "Hospital claim AI"

# ติดตั้ง dependencies
pip install python-docx lxml

# ทดสอบว่า pipeline ทำงานได้
python scripts/auto_claim_pipeline.py --help
```

### 1.3 ติดตั้ง Claude Code Skills

Skills อยู่ใน `~/.claude/skills/` ถ้า clone repo แล้วไม่มี ให้ copy:

```bash
# Copy skills ไปที่ Claude Code
cp -r hospital-claim-ai-app/skills/cathlab-claim-checker ~/.claude/skills/
cp -r hospital-claim-ai-app/skills/appeal-drafter ~/.claude/skills/

# Copy slash command
mkdir -p .claude/commands
cp .claude/commands/claim-batch.md .claude/commands/
```

### 1.4 ตรวจสอบการติดตั้ง

```bash
# ตรวจว่า pipeline ทำงานได้
python -c "from scripts.docx_generators import generate_deny_report; print('OK')"

# ตรวจว่า skill โหลดได้ (ใน Claude Code)
# พิมพ์ /cathlab-claim-checker แล้วดูว่า skill ตอบกลับ
```

---

## 2. วิธีใช้งาน

### 2.1 ตรวจเคสเดียว (Interactive)

เปิด Claude Code แล้วพิมพ์:

```
/cathlab-claim-checker
```

จากนั้นแปะข้อมูลเคส เช่น:
- วาง CSV แถวเดียวจาก e-Claim
- หรือพิมพ์ข้อมูลเอง: HN, AN, Dx, Procedures, DRG

AI จะวิเคราะห์ให้ทันทีพร้อม:
- 8 Checkpoints ตรวจสอบ
- แนะนำ CC/MCC เพิ่ม RW
- ทำนาย Deny Probability
- สร้าง Deny Report DOCX
- สร้าง Appeal Letter DOCX

### 2.2 ตรวจหลายเคส (Batch — เร็ว)

```
/claim-batch
```

แล้วแนบไฟล์ CSV จาก e-Claim export

หรือรันตรงใน terminal:

```bash
python scripts/auto_claim_pipeline.py eclaim_export.csv
```

**ผลลัพธ์:**
```
claim_reports/
├── Deny_Report_69-03556.docx    ← รายงานวิเคราะห์
├── Appeal_69-03556.docx         ← หนังสืออุทธรณ์
├── Deny_Report_69-03557.docx
├── Appeal_69-03557.docx
└── ... (ทุกเคสที่ deny)
```

**Performance:** 100 เคส = ~7 วินาที

### 2.3 ระบุ output folder

```bash
python scripts/auto_claim_pipeline.py eclaim_export.csv /path/to/output
```

### 2.4 เคสติด Deny — วิเคราะห์ + อุทธรณ์

```
/cathlab-claim-checker
```

บอกว่า "เคสถูก deny" พร้อม deny code (เช่น HC09, IP01, HC13)
AI จะ:
1. วิเคราะห์สาเหตุ
2. แนะนำวิธีแก้
3. สร้างหนังสืออุทธรณ์ DOCX

### 2.5 ร่างหนังสืออุทธรณ์อย่างเดียว

```
/appeal-drafter
```

---

## 3. คำสั่งลัด

| คำสั่ง | ทำอะไร |
|--------|--------|
| `/cathlab-claim-checker` | ตรวจเคส Cath Lab (1 เคส, ละเอียด) |
| `/claim-batch` | ตรวจหลายเคสจาก CSV (เร็ว) |
| `/appeal-drafter` | ร่างหนังสืออุทธรณ์ |
| `/deny-analyzer` | วิเคราะห์เคสที่ถูก deny |
| `/icd-coding` | ช่วย coding ICD-10/ICD-9 |
| `/smart-coder` | แปลง clinical notes → ICD codes |
| `/deny-predictor` | ทำนายว่าจะถูก deny ไหม |

---

## 4. โครงสร้างไฟล์

```
Hospital claim AI/
├── scripts/
│   ├── auto_claim_pipeline.py   ← Main: CSV → DOCX อัตโนมัติ
│   └── docx_generators.py       ← Template engine สร้าง DOCX
├── hospital-claim-ai-app/
│   ├── knowledge/               ← Knowledge base (11 ไฟล์)
│   │   ├── cath-lab.md          ← Cath Lab rules + INST limit ปีงบ69
│   │   ├── deny-fixes.md        ← Deny code → วิธีแก้
│   │   └── core-rules.md        ← Thai DRG v6.3, FDH, timing
│   ├── references/
│   │   └── nhso-rules/
│   │       ├── inst-payment-reform-fy69.md  ← ประกาศใหม่ ปีงบ69
│   │       ├── eclaim-system-guide.md
│   │       └── deny-codes.md
│   └── core/
│       ├── eclaim_parser.py     ← CSV parser
│       └── cathlab_models.py    ← Data models
├── .claude/
│   └── commands/
│       └── claim-batch.md       ← Slash command /claim-batch
├── claim_reports/               ← Output DOCX (auto-created)
└── docs/
    └── SETUP-GUIDE.md           ← คุณอยู่ที่นี่
```

---

## 5. Knowledge ที่ติดตั้ง

### กฎปีงบ 2569 (ใหม่)

| หัวข้อ | สิ่งที่เปลี่ยน |
|--------|--------------|
| **Pre Authorized** | CCS (I25.x) ต้องขออนุมัติก่อนทำทุกราย |
| **เพดานอุปกรณ์** | 28 รายการ เช่น DES อัลลอยด์ ≤3, สแตนเลส ≤1 |
| **Serial/Barcode** | บังคับส่งผ่าน Standard API ตั้งแต่ 1 เม.ย. 69 |
| **จ่ายตามจริง** | เปลี่ยนจากอัตราคงที่ → จ่ายจริงไม่เกินเพดาน |
| **ห้ามแบ่ง Episode** | ≤270 วัน ต่อเนื่อง |
| **Base Rate** | ในเขต 8,350 / นอกเขต 9,600 บาท/AdjRW |

### Smart Analysis ตรวจอะไรบ้าง

Pipeline จะ auto-analyze ทุกเคสโดย:
- ดู DRG + RW → ระบุว่าเป็นเคสอะไร (PCI, Diagnostic cath, etc.)
- จับ deny code → ระบุสาเหตุเฉพาะเคส
- ตรวจ Refer case (HMAIN ≠ HCODE)
- ตรวจ Pre Auth สำหรับ CCS
- ตรวจเพดานอุปกรณ์ปีงบ69
- แนะนำ CC/MCC ที่อาจเพิ่ม RW ได้
- สร้าง appeal justification อัตโนมัติ (อ้าง guideline)

---

## 6. FAQ

### Q: ต้องมี internet ไหม?
**ไม่ต้อง** สำหรับ batch pipeline — ทุกอย่างรันบนเครื่อง ไม่เรียก API

### Q: รองรับ CSV format ไหนบ้าง?
e-Claim export จาก สปสช. (REP file) ที่มี header "REP No." หรือ "TRAN_ID"

### Q: DOCX เปิดด้วยอะไร?
Microsoft Word หรือ LibreOffice — ฟอนต์ TH Sarabun New (ต้องติดตั้ง)

### Q: แก้ข้อมูล รพ. ยังไง?
แก้ใน `scripts/auto_claim_pipeline.py` ตัวแปร `HOSPITAL`:
```python
HOSPITAL = {
    "hospcode": "11855",
    "hosp_name": "โรงพยาบาลพญาไทศรีราชา",
    "hosp_province": "จังหวัดชลบุรี",
    "nhso_region": "6",
    "nhso_region_name": "ระยอง",
    "base_rate_in": 8350,
    "base_rate_out": 9600,
}
```

### Q: เพิ่ม deny code ใหม่ยังไง?
แก้ใน `scripts/auto_claim_pipeline.py`:
- `DENY_MEANINGS` — เพิ่มชื่อ deny code
- `DENY_FIXES` — เพิ่มสาเหตุ + วิธีแก้

### Q: เพิ่ม knowledge ใหม่ยังไง?
ใช้คำสั่ง `/claim-knowledge-updater` หรือเพิ่มไฟล์ .md ใน:
- `hospital-claim-ai-app/knowledge/`
- `hospital-claim-ai-app/references/nhso-rules/`
- `~/.claude/skills/cathlab-claim-checker/references/`

### Q: Timeline อุทธรณ์?
- ครั้งที่ 1: ภายใน **15 วันทำการ** หลังรับแจ้ง deny
- สปสช. พิจารณา: ภายใน 30 วัน
- ครั้งที่ 2: ภายใน 15 วันทำการ หลังรับผลครั้งที่ 1
- อุทธรณ์ได้สูงสุด **2 ครั้ง**
