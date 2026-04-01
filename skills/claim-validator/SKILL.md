---
name: claim-validator
description: ตรวจสอบ claim ก่อนส่ง สปสช./FDH — รัน 8 checkpoints, ตรวจ 16-file/43-file, timing, เอกสาร, CC/MCC, แก้ auto ถ้าทำได้
---

# Claim Validator

> ตรวจสอบ claim ครบ 8 checkpoints ก่อนส่ง → จับ error ก่อน deny → แก้อัตโนมัติถ้าทำได้

## Trigger Keywords
ตรวจ claim, validate, check, ส่ง fdh, ก่อนส่ง, 16 แฟ้ม, 43 แฟ้ม, c error, pre-submission

---

## Workflow

### Step 1: รับ Claim Input

```json
{
  "an": "6901234",
  "hn": "001234",
  "cid": "1234567890123",
  "age": 65, "sex": "M",
  "admit_date": "2569-01-15",
  "discharge_date": "2569-01-20",
  "discharge_type": "1",
  "principal_dx": "I21.0",
  "secondary_dx": ["I10", "E11.9", "N18.3"],
  "procedures": ["36.06"],
  "devices": [{"type": 5, "code": "STENT001", "serial": "SN12345", "qty": 1}],
  "drugs": [{"did": "1041959", "name": "abacavir", "amount": 10}],
  "claim_amount": 150000,
  "fund": "UC",
  "authen_code": "PP1007991295",
  "department": "cath-lab"
}
```

### Step 2: Run 8 Checkpoints

#### ✅ Checkpoint 1: Basic Data Validation
ตรวจ:
- [ ] AN ไม่ว่าง
- [ ] HN ไม่ว่าง
- [ ] CID 13 หลัก + checksum ถูกต้อง
- [ ] PDx ไม่ว่าง (DRG Error 1 = No PDx)
- [ ] Procedures มีสำหรับ IPD (แนะนำ)
- [ ] เพศ/อายุ ไม่ conflict กับ PDx (DRG Error 4, 5)
- [ ] วันที่ admit ≤ วันที่ discharge

**Auto-fix:** ❌ (ต้องแก้ด้วยมือ)

#### ✅ Checkpoint 2: Dx-Proc Clinical Match
ตรวจ ICD-10 ↔ ICD-9-CM consistency:

| Check | ตัวอย่าง | ผล |
|-------|---------|-----|
| PDx + Proc match | I21.0 + 36.06 | ✅ STEMI + PCI |
| PDx + Proc mismatch | J18.9 + Thoracoscopy | ⚠️ ขาด Pleural effusion |
| Proc without matching Dx | 99.25 (Chemo) ไม่มี C-code | ❌ ต้องมี cancer PDx |
| Dx without expected Proc | I21.0 ไม่มี 36.06 | ⚠️ ถ้าทำ PCI ต้องใส่ code |

**Auto-fix:** ⚠️ แนะนำ code ที่ขาด แต่ต้อง confirm

#### ✅ Checkpoint 3: Device Documentation
ตรวจ ADP file:
- [ ] TYPE ถูกต้อง (3=วัสดุสิ้นเปลือง, 4=ข้อต่อ, 5=อวัยวะเทียม)
- [ ] CODE ตรงกับ สปสช. catalog
- [ ] QTY ตรงกับ procedure note
- [ ] SERIALNO / Lot number ตรงกับ GPO VMI
- [ ] RATE ไม่เกิน ceiling price

**Auto-fix:** ❌ (ต้องตรวจเอกสารจริง)

#### ✅ Checkpoint 4: 16-File / 43-File Completeness

**สำหรับ e-Claim (16 แฟ้ม):**

| File | Key Fields | Common Error |
|------|-----------|-------------|
| IPD | AN, DATEADM, DATEDSC, DISCHT, WARD | Date format DD/MM/YYYY, D/C < ADM |
| DIA | DIAG (ICD-10), DXTYPE (1=PDx) | Invalid code, ไม่มี PDx |
| OPR | OPCODE (ICD-9-CM), DATEOP | Invalid code, date นอก admit range |
| ADP | TYPE, CODE, QTY, RATE, SERIALNO | Code mismatch |
| DRU | DID (GPUID→TMT), AMOUNT | Drug Catalog mismatch |
| CHA | CHRGITEM, AMOUNT | Missing items |
| INS | INSCL (สิทธิ) | Wrong fund code |

**สำหรับ 43 แฟ้ม (OP/PP):**
อ้างอิง `references/nhso-rules/43-file-spec.md`:
- PERSON ต้องส่งทุกครั้ง
- Key fields: HOSPCODE, PID, CID, SEQ, DATE_SERV
- ตรวจ 3 ขั้นตอน: Validate → Verify → Process

**Auto-fix:** ✅ ตรวจ format, แนะนำแก้ field ที่ผิด

#### ✅ Checkpoint 5: Timing & Authorization
- [ ] ส่งภายใน 30 วัน (IPD) / 15 วัน (OPD) หลัง D/C
- [ ] Authen Code มี + ไม่หมดอายุ (สำหรับ UC)
- [ ] ปีงบ 69: ตรวจ W305 แทน C30

| Timeline | สถานะ | ผล |
|----------|-------|-----|
| ≤24 ชม. | Fast track | สปสช. จ่ายใน 72 ชม. |
| ≤30 วัน (IPD) | ปกติ | จ่ายปกติ |
| ≤15 วัน (OPD) | ปกติ | จ่ายปกติ |
| >30 วัน | ⚠️ Late | ลดอัตราจ่าย / reject |

**Auto-fix:** ✅ คำนวณ deadline + alert

#### ✅ Checkpoint 6: CC/MCC Optimization
อ้างอิง `knowledge/core-rules.md`:

ตรวจ SDx ทั้งหมด → หา CC/MCC ที่ขาดแต่น่าจะมี:

| สถานการณ์ | แนะนำเพิ่ม | Impact |
|-----------|-----------|--------|
| DM มีแค่ E11.9 | E11.2x-E11.6x (ถ้ามี complication) | +CC |
| HF มีแค่ I50.9 | I50.2x/I50.3x/I50.4x | +CC/MCC |
| Sepsis ไม่มี organ failure | N17.x, J96.0x (ถ้ามี) | +MCC |
| CKD ไม่ระบุ stage | N18.3/N18.4 (ตาม eGFR) | +CC/MCC |

**Auto-fix:** ⚠️ แนะนำ code + เหตุผล แต่ต้อง confirm กับ clinical data

#### ✅ Checkpoint 7: Department Detection
Auto-detect จาก PDx + Procedures:

| PDx Pattern | Proc Pattern | Department |
|------------|-------------|-----------|
| I20-I25 | 36.0x, 37.2x | Cath Lab |
| C-codes | 99.25 | Chemo |
| N18.5 | 39.95 | Dialysis |
| Any | OR codes | OR/Surgery |
| J96.x + ventilator | 96.7x | ICU |
| S/T codes + ER | — | ER/UCEP |

**Auto-fix:** ✅ อัตโนมัติ

#### ✅ Checkpoint 8: Score Calculation

| ระดับ | เงื่อนไข | ความหมาย |
|-------|---------|----------|
| ✅ Pass | ไม่มี error | ส่งได้เลย |
| ⚠️ Warning | มีจุดที่ปรับปรุงได้ | ส่งได้แต่ควรแก้ |
| ❌ Critical | มี error ที่จะถูก deny | **ห้ามส่ง** จนกว่าจะแก้ |
| 💡 Optimization | มี CC/MCC ที่เพิ่มได้ | เงินเพิ่ม |

Score = 100 - (Critical × 20) - (Warning × 5) + (Optimization × 2)

### Step 3: Output

```
══════════════════════════════════════
  CLAIM VALIDATION REPORT
══════════════════════════════════════
AN: 6901234 | Fund: UC | Dept: Cath Lab
Score: 85/100 | Status: ⚠️ WARNING

──────────────────────────────────────
CHECKPOINTS
──────────────────────────────────────
✅ 1. Basic Data          — PASS
✅ 2. Dx-Proc Match       — PASS (I21.0 + 36.06)
⚠️ 3. Device Docs        — WARNING (stent serial ไม่ตรง GPO VMI)
✅ 4. 16-File Complete    — PASS
✅ 5. Timing              — PASS (ส่งภายใน 5 วัน)
💡 6. CC/MCC              — เพิ่ม I50.21 → MCC (+RW 0.8)
✅ 7. Department          — Cath Lab (auto)
⚠️ 8. Score              — 85/100

──────────────────────────────────────
⚠️ ISSUES TO FIX
──────────────────────────────────────
1. [WARNING] Stent serial number ไม่ตรง GPO VMI record
   → ตรวจสอบ lot number กับคลังเวชภัณฑ์

──────────────────────────────────────
💡 OPTIMIZATIONS
──────────────────────────────────────
1. เพิ่ม I50.21 (Acute systolic HF) — EF 35%
   Impact: MCC → DRG 05051 → RW 3.2 → 4.0
   เงินเพิ่ม: ~6,680 บาท

2. เปลี่ยน E11.9 → E11.65 (DM with hyperglycemia)
   Impact: เป็น CC (แต่มี MCC แล้วไม่มีผลเพิ่ม)

──────────────────────────────────────
📊 DRG ESTIMATE
──────────────────────────────────────
Current:  DRG 05052 | RW 3.2 | ~26,720 บาท
Optimized: DRG 05051 | RW 4.0 | ~33,400 บาท
Difference: +6,680 บาท

──────────────────────────────────────
📋 VERDICT
──────────────────────────────────────
⚠️ แก้ device serial ก่อนส่ง
💡 เพิ่ม CC/MCC ได้อีก ~6,680 บาท
══════════════════════════════════════
```

---

## Auto-Fix Capabilities

| ปัญหา | Auto-fix | วิธี |
|-------|---------|------|
| Date format ผิด | ✅ | แปลง format อัตโนมัติ |
| Missing department | ✅ | Auto-detect จาก Dx+Proc |
| CID checksum | ✅ | คำนวณ digit 13 |
| DM unspecified (E11.9) | ⚠️ แนะนำ | แนะนำ specific code + เหตุผล |
| Drug code → TMT | ⚠️ แนะนำ | Lookup Drug Catalog |
| Missing Authen | ❌ | Alert ให้ไปทำใหม่ |
| Stent serial mismatch | ❌ | Alert ตรวจกับคลัง |

---

## Knowledge References

| File | ใช้สำหรับ |
|------|----------|
| `knowledge/core-rules.md` | DRG grouping, 16-file, CC/MCC, timing |
| `knowledge/deny-fixes.md` | C-code prevention |
| `references/nhso-rules/43-file-spec.md` | 43-file validation, key fields |
| `references/nhso-rules/eclaim-system-guide.md` | e-Claim tabs, Drug Catalog, sิทธิ |
| `references/youtube-extracted/zSUuHM9Y2Vk/analysis.md` | ปีงบ 69: Zero C, W305, DRG v6 |
| `knowledge/[department].md` | Department-specific rules |

---

## Integration

- **← icd-coding**: รับ recommended codes → validate
- **→ deny-analyzer**: ถ้า score < 70 → วิเคราะห์ว่าจะถูก deny ตรงไหน
- **→ appeal-drafter**: ถ้าส่งแล้ว deny → ร่างอุทธรณ์
