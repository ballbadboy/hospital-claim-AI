# Hospital Claim AI — Cath Lab Module

> AI ช่วยลด deny rate ของ claim ที่ส่งไป สปสช. — จาก 10% เหลือ 3%
> โรงพยาบาล: พญาไทศรีราชา (11855) เขต 6 ชลบุรี
> HIS: SSB | แผนกหลัก: Cath Lab (สวนหัวใจ)

## วิธีใช้ AI ช่วยทำ Claim

เจ้าหน้าที่พิมพ์ข้อมูลเคสเป็นภาษาไทย → AI วิเคราะห์ให้ทันที

**4 งานที่ AI ช่วย:**
1. **ตรวจเคสก่อนส่ง** — พิมพ์ข้อมูลจาก chart → AI แนะนำ ICD codes + score + เงินที่คาดหวัง
2. **วิเคราะห์ deny** — พิมพ์ deny code จาก REP file → AI บอกสาเหตุ + วิธีแก้
3. **ตรวจหลายเคส** — วาง CSV จาก e-Claim → AI วิเคราะห์ทุกเคส
4. **ร่าง appeal** — บอกข้อมูลเคส → AI ร่างหนังสืออุทธรณ์ภาษาราชการ

**ดูคู่มือเจ้าหน้าที่:** `docs/staff-guide.md`

## Skills ที่ติดตั้ง

| Skill | ใช้เมื่อ |
|-------|---------|
| **cathlab-claim-checker** | ตรวจเคส Cath Lab ทุกเคส (8 checkpoints) |
| **deny-analyzer** | เคสถูก deny ต้องหาสาเหตุ |
| **icd-coding** | ต้องการ ICD-10/ICD-9-CM จาก clinical notes |
| **claim-validator** | ตรวจ claim ทุกแผนก (ไม่เฉพาะ Cath Lab) |
| **appeal-drafter** | ร่างหนังสืออุทธรณ์ |

## ข้อมูลโรงพยาบาล

- **รหัส รพ.:** 11855
- **ชื่อ:** รพ.พญาไทศรีราชา
- **เขต สปสช.:** เขต 6 ระยอง
- **จังหวัด:** ชลบุรี (2000)
- **HIS:** SSB
- **สิทธิ์หลัก:** UCS (บัตรทอง)
- **Base Rate ปีงบ 69:** ในเขต 8,350 / นอกเขต 9,600 บาท/AdjRW

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL
- **AI:** Claude API (claude-sonnet-4-20250514) + Rule Engine 8 checkpoints
- **Frontend:** React 19 + Vite + TailwindCSS + Recharts
- **HIS:** SSB (API) — ระบบหลักของ รพ.
- **Auth:** JWT (5 roles: admin, coder, dept_head, finance, readonly)
- **Notifications:** LINE Bot SDK
- **Reports:** openpyxl (Excel export)

## How to Run

```bash
# Backend
pip install -r requirements.txt
cp .env.example .env  # แก้ไข API keys
uvicorn api.main:app --reload --port 8000

# Frontend
cd dashboard && npm install && npm run dev

# Tests
pytest tests/ -v

# Database migration
alembic upgrade head
```

## Project Structure

```
hospital-claim-ai-app/
├── CLAUDE.md              ← คุณอยู่ที่นี่
├── api/                   ← FastAPI endpoints
│   ├── main.py            ← App setup, CORS, middleware
│   ├── routes.py          ← /check, /check/batch, /appeal, /dashboard
│   ├── routes_his.py      ← HIS integration endpoints
│   ├── routes_reports.py  ← Report generation & Excel export
│   └── auth/              ← JWT auth, user management
├── core/                  ← Business logic
│   ├── ai_engine.py       ← Claude API integration
│   ├── claim_checker.py   ← Orchestrator (rules + AI)
│   ├── rule_engine.py     ← 8 deterministic validation checkpoints
│   ├── models.py          ← Pydantic schemas
│   ├── database.py        ← SQLAlchemy ORM models
│   ├── repositories.py    ← Repository pattern for DB
│   ├── report_engine.py   ← Excel report generation
│   └── state_machine.py   ← Claim lifecycle states
├── modules/               ← Pluggable subsystems
│   └── his_connector/     ← HIS adapters (CSV, HOSxP, SSB)
├── knowledge/             ← Clinical decision rules (11 markdown files)
├── references/            ← ความรู้จากภายนอก
│   ├── nhso-rules/        ← หลักเกณฑ์ สปสช. (PDF/สรุป)
│   ├── youtube-extracted/  ← สกัดจาก YouTube สปสช.
│   └── hospital-data/     ← ข้อมูลเฉพาะ รพ.
├── skills/                ← Claude Code skills
│   ├── icd-coding/        ← ช่วย coding ICD-10/ICD-9-CM
│   ├── claim-validator/   ← ตรวจสอบ claim ก่อนส่ง
│   ├── deny-analyzer/     ← วิเคราะห์สาเหตุ deny
│   └── appeal-drafter/    ← ร่างหนังสืออุทธรณ์
├── agents/                ← AI agent definitions
├── dashboard/             ← React frontend
├── tests/                 ← pytest test suite
├── docs/                  ← Implementation plans
├── scripts/               ← Utility scripts
├── alembic/               ← Database migrations
└── .claude/               ← Claude Code config
    └── commands/          ← Custom slash commands
```

## Rule Engine — 8 Checkpoints

1. **Basic Data** — PDx required, procedures recommended for IPD
2. **Dx-Proc Match** — ICD-10 ตรงกับหัตถการ (AI validate)
3. **Device Docs** — Stent/implant lot numbers, GPO VMI match
4. **16-File Completeness** — Date format, LOS, admit < discharge
5. **Timing** — ส่งภายใน 30 วัน, Authen Code สำหรับ UC
6. **CC/MCC Optimization** — หา coding เพิ่ม DRG weight
7. **Department Detection** — Auto-detect จาก Dx + procedures
8. **Score Calculation** — Pass/warning/critical/optimization counts

## Knowledge Base

`knowledge/` มี 11 ไฟล์ — AI engine โหลดตามแผนกที่ detect ได้:
- `core-rules.md` — Thai DRG v6.3.3, FDH 16-File, timing rules
- `cath-lab.md`, `or-surgery.md`, `chemo.md`, `dialysis.md`
- `icu-nicu.md`, `er-ucep.md`, `ods-mis.md`, `opd-ncd.md`
- `rehab-palliative.md`, `deny-fixes.md`

`references/youtube-extracted/` มี transcript สกัดจาก สปสช. YouTube:
- ดู index ที่ `references/youtube-extracted/nhso-video-index.md`

## Key Business Rules (ปีงบ 2569)

- IP Base Rate เป้าหมาย: 8,350 บาท/RW
- ผู้มีสิทธิ์ UC: ~47 ล้านคน
- งบรายหัวรวม: ~4,100 บาท (+12% YoY)
- หน่วยนวัตกรรมเปลี่ยนเป็น Global Budget
- เลิกใช้ C code → เปลี่ยนเป็น Deny พร้อม feedback ทันที
- ใช้ AI/OCR ตรวจสอบ claim
- ประกาศหลักเกณฑ์ครั้งเดียวต่อปี (ไม่เปลี่ยนกลางปี)

## Coding Conventions

- Python: async/await, type hints, Pydantic models
- API: FastAPI with dependency injection
- DB: SQLAlchemy 2.0 async, repository pattern
- Tests: pytest + pytest-asyncio
- Frontend: TypeScript, functional components, TanStack Query
- Naming: snake_case (Python), camelCase (TypeScript)
- ภาษาในโค้ด: English (comments ใช้ Thai ได้สำหรับ domain terms)

## DRG Quick Reference

```
PDx → MDC → OR check → PDC → DC → DRG → PCCL → final RW
```

MDC ที่ deny บ่อย: 05 (Circulatory), 08 (Musculoskeletal), 11 (Kidney), 17 (Myeloproliferative), 04 (Respiratory)

## Common Deny Causes (AI ต้องจับให้ได้)

| สาเหตุ | ตัวอย่าง | Checkpoint |
|--------|---------|-----------|
| ICD-10 ไม่ตรงหัตถการ | J18.9 + Thoracoscopy | #2 Dx-Proc |
| เอกสารไม่ครบ | ไม่แนบใบรับรองแพทย์ | #3 Device, #4 Files |
| DRG ไม่ตรง | Grouper จัดกลุ่มผิด | #6 CC/MCC |
| CID ผิด | เลข 13 หลักผิด | #1 Basic |
| ส่งเลยกำหนด | เกิน 30 วัน | #5 Timing |
