# Hospital Claim AI

> AI ช่วยลด deny rate ของ claim ที่ส่งไป สปสช. — จาก 10% เหลือ 3%
> เงินที่กู้คืนได้: 3.5-7 ล้านบาท/ปี สำหรับ รพ. 200 เตียง

## ปัญหาที่แก้

โรงพยาบาลส่ง claim ไป สปสช. แล้วถูก deny 5-15% ของ claim ทั้งหมด สาเหตุหลัก:

| สาเหตุ | ตัวอย่าง | AI ช่วย? |
|--------|---------|---------|
| ICD-10 ไม่ตรงหัตถการ | J18.9 + Thoracoscopy | ✅ |
| เอกสารไม่ครบ | ไม่แนบใบรับรองแพทย์ | ✅ |
| DRG ไม่ตรง | Grouper จัดกลุ่มผิด | ✅ |
| CC/MCC ไม่ครบ | ลืม code I50.21 เสียเงิน 23,000 | ✅ |
| ส่งเลยกำหนด | เกิน 30 วัน | ✅ |

## AI ช่วย 4 งาน

```
📋 Coding        → พิมพ์ clinical data → AI แนะนำ ICD-10 + CC/MCC + DRG + เงิน
🔍 Pre-Submit    → AI ตรวจ 8 checkpoints → score + สิ่งที่ต้องแก้
🔬 Deny Analysis → พิมพ์ deny code → AI บอกสาเหตุ + วิธีแก้ + recovery chance
📝 Appeal        → AI ร่างหนังสืออุทธรณ์ภาษาราชการ → คนแค่ตรวจ + เซ็น
```

## วิธีใช้ (สำหรับเจ้าหน้าที่)

### 1. ตรวจเคสก่อนส่ง e-Claim

เปิด Claude Code แล้วพิมพ์:

```
ตรวจเคส Cath Lab:

AN: 69-03556
หญิง 65 ปี สิทธิ์ UC
Admit: 27/02/69  D/C: 01/03/69

แพทย์วินิจฉัย: STEMI anterior
EKG: ST elevation V1-V4
Troponin: 15.2
Echo EF: 35%
eGFR: 45
โรคร่วม: DM, HT, CKD

ทำ PCI ใส่ DES LAD 1 ตัว
D2B: 78 นาที
```

AI จะตอบ:
- ICD codes ที่ควรใช้ (PDx + SDx + Procedures)
- Score ว่าพร้อมส่งไหม
- CC/MCC ที่ขาด → เพิ่มแล้วได้เงินเพิ่มเท่าไหร่
- DRG + RW + เงินที่คาดว่าจะได้

### 2. เคสถูก Deny — วิเคราะห์

```
เคสถูก deny:

AN: 69-03556
DRG: 05290  RW: 8.6544
ยอดที่ควรได้: 71,322 บาท

Deny codes: HC09, IP01, HC13
รายการที่ถูก deny: CLOPIDOGREL_DRUG, INST 31,490 บาท
```

AI จะตอบ:
- สาเหตุแต่ละ deny code
- วิธีแก้ทีละขั้น
- โอกาสได้เงินคืน %
- ควร auto_fix / appeal / escalate / write_off

### 3. Upload CSV ทั้งไฟล์

```
อ่าน REP file นี้แล้ววิเคราะห์ทุกเคสที่ถูก deny:
[ลากไฟล์ CSV วาง]
```

### 4. ร่างหนังสืออุทธรณ์

```
ร่างหนังสืออุทธรณ์:

AN: 69-03556
วินิจฉัย: STEMI anterior ทำ PCI ใส่ DES
ถูก deny: HC09 เรื่อง stent document
ยอด: 71,322 บาท
ส่งถึง: สปสช. เขต 6
```

### 5. ถามอะไรก็ได้

```
DRG 05290 คืออะไร ได้เงินเท่าไหร่
HC09 แก้ยังไง
ถ้า EF 35% ควร code อะไร
เคสนี้ควร appeal ไหม
```

## จำไว้ 3 ข้อ

```
1. AI แนะนำ → คนตรวจทาน → คนตัดสินใจ
2. ทุก ICD code ต้องมีหลักฐานใน chart
3. ไม่แน่ใจ → ถาม AI เพิ่ม ดีกว่าเดา
```

---

## Architecture

```
┌────────────┐     ┌──────────────────┐     ┌───────────┐
│  HIS (SSB) │────▶│   Claude Code    │────▶│  e-Claim  │
│  Hospital  │     │   + Skills/Agent │     │  (สปสช.)  │
└────────────┘     └──────┬───────────┘     └───────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Knowledge│ │ FastAPI  │ │  DOCX    │
        │   Base   │ │   API    │ │ Reports  │
        │ (30+docs)│ │(20 tests)│ │(auto-gen)│
        └──────────┘ └──────────┘ └──────────┘
```

## Skills ที่ติดตั้ง

| Skill | ใช้เมื่อ |
|-------|---------|
| `cathlab-claim-checker` | ตรวจเคส Cath Lab (8 checkpoints + DRG RW จริง) |
| `deny-analyzer` | วิเคราะห์สาเหตุ deny + แนะนำวิธีแก้ |
| `icd-coding` | แนะนำ ICD-10/ICD-9-CM จาก clinical notes |
| `claim-validator` | ตรวจ claim ทุกแผนก |
| `appeal-drafter` | ร่างหนังสืออุทธรณ์ภาษาราชการ |

## Knowledge Base

```
references/
├── nhso-rules/          ← 15 files (deny codes, 43-file, e-Claim, DRG, drug catalog)
├── youtube-extracted/   ← 5 videos สปสช. (ปีงบ 69, นวัตกรรม, กองทุน)
└── hospital-data/       ← 30 test cases

skills/cathlab-claim-checker/references/
├── drg-rw-table-cardiac.md  ← 60+ cardiac DRGs with RW จริง
├── cardiac-codes.md         ← ICD-10 + ICD-9-CM cardiac
├── validation-rules.md      ← 8 checkpoints
├── clinical-criteria.md     ← STEMI/NSTEMI/UA + GRACE/TIMI
├── deny-fixes.md            ← C-code solutions + appeal template
├── drg-cardiac.md           ← Thai DRG v6.3 grouping logic
└── fdh-16files.md           ← FDH 16-file for Cath Lab
```

## Agents

| Agent | หน้าที่ | Pipeline |
|-------|--------|---------|
| `cathlab-auto-checker` | ตรวจ claim ก่อนส่ง | Scan → Validate → Fix → Submit |
| `denial-fighter` | แก้ claim ที่ถูก deny | Analyze → Fix → Appeal → Track |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cathlab/check` | ตรวจ 8 checkpoints + CC/MCC optimization |
| POST | `/api/v1/cathlab/analyze-deny` | วิเคราะห์ deny + แนะนำ fix |
| POST | `/api/v1/cathlab/parse-eclaim` | Upload CSV จาก e-Claim |
| GET | `/api/v1/cathlab/drg-lookup/{code}` | Lookup DRG + RW + payment |
| POST | `/api/v1/check` | ตรวจ claim ทุกแผนก |
| POST | `/api/v1/appeal` | สร้าง appeal letter |
| GET | `/api/v1/dashboard/stats` | KPI dashboard |

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run API
uvicorn api.main:app --reload

# Run Tests (20/20 pass)
pytest tests/test_cathlab.py -v

# Generate Report (DOCX)
python scripts/generate_full_report.py
```

## ข้อมูลโรงพยาบาล

| | |
|---|---|
| รหัส รพ. | 11855 |
| ชื่อ | รพ.พญาไทศรีราชา |
| เขต สปสช. | เขต 6 ระยอง |
| จังหวัด | ชลบุรี |
| HIS | SSB |
| Base Rate ปีงบ 69 | ในเขต 8,350 / นอกเขต 9,600 บาท/AdjRW |

## ตัวอย่างผลลัพธ์ (เคสจริง AN 69-03556)

```
DRG: 05290 (Acute MI w single vessel PTCA wo sig CCC)
RW: 8.6544 → Payment: 72,264 บาท
Status: DENY (HC09, IP01, HC13)

AI Analysis:
  Category: device_documentation
  Root Cause: Stent ADP file + Clopidogrel TMT mismatch
  Recovery Chance: 85%
  Action: AUTO_FIX

  💡 ถ้าเพิ่ม CC/MCC (I50.21):
     DRG: 05291 → RW: 11.4820 → Payment: 95,858 บาท
     เงินเพิ่ม: +23,594 บาท
```

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL
- **AI:** Claude Code Skills + Claude API
- **Frontend:** React 19 + Vite + TailwindCSS + Recharts
- **HIS:** SSB (API)
- **Reports:** python-docx (DOCX generation)
- **Tests:** pytest (20/20 pass)

## License

Proprietary — Phyathai Sriracha Hospital / MedGuard AI

## Credits

- **Dr.Kasemson Kasemwong** — Project Lead
- **Claude AI (Opus 4.6)** — AI Development Partner
- **สปสช.** — NHSO rules and knowledge base source
- **TCMC** — Thai DRG v6.3.3 data
