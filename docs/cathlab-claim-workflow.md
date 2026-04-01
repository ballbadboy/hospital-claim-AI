# Cath Lab Claim Workflow — Semi-Auto Edition

> Hospital: รพ.พญาไทศรีราชา (11855) เขต 6 ชลบุรี
> Version: 1.0 — March 2026
> Mode: Semi-Auto (AI ช่วย + คนตรวจทาน)

---

## ภาพรวม: เส้นทาง Claim ตั้งแต่ผู้ป่วยเข้าจนได้เงิน

```
ผู้ป่วยเข้า Cath Lab
       ↓
[Phase 1] ก่อนทำหัตถการ (Pre-Procedure)
       ↓
[Phase 2] ระหว่างทำหัตถการ (Intra-Procedure)
       ↓
[Phase 3] หลังทำหัตถการ (Post-Procedure)
       ↓
[Phase 4] Discharge + Coding
       ↓
[Phase 5] ตรวจสอบก่อนส่ง (Pre-Submit) ← AI ช่วยตรงนี้
       ↓
[Phase 6] ส่ง e-Claim / FDH
       ↓
[Phase 7] ติดตามผล + แก้ไข ← AI ช่วยตรงนี้
       ↓
💰 ได้เงินคืน
```

---

## Phase 1: ก่อนทำหัตถการ (Pre-Procedure)

### ขั้นตอน

| # | ใครทำ | ทำอะไร | เอกสาร/ระบบ | AI ช่วยได้? |
|---|-------|--------|------------|------------|
| 1.1 | **พยาบาล ER/Ward** | ตรวจสอบสิทธิ์ผู้ป่วย | ระบบ สปสช. / Smart Card | ❌ (ทำใน ER) |
| 1.2 | **พยาบาล ER/Ward** | Authen Code — รูดบัตร/ยืนยันตัวตน | ระบบ Authen สปสช. | ❌ |
| 1.3 | **แพทย์** | ตรวจประเมิน + ส่ง Cath Lab | OPD Card / ER Record | ❌ |
| 1.4 | **เจ้าหน้าที่ Admit** | ลงทะเบียน Admit (สร้าง AN) | HIS (HOSxP) | ❌ |
| 1.5 | **พยาบาล Cath Lab** | เตรียมผู้ป่วย + ตรวจ consent | Cath Lab checklist | ❌ |

### ⚠️ จุดที่มักพลาด
- **ลืมรูด Authen Code** → ติด C30/W305 ภายหลัง
- **สิทธิ์ซ้ำซ้อน** (มีประกันสังคมด้วย) → ติด D02
- **ไม่ verify ตัวตน** กรณีฉุกเฉิน STEMI → ต้องขอย้อนหลัง

### 🤖 AI Recommendation
```
ตั้ง alert ใน HIS:
"ผู้ป่วย Cath Lab ทุกราย ต้องมี Authen Code ก่อน procedure"
ถ้าไม่มี → แจ้งเตือนทันที
```

---

## Phase 2: ระหว่างทำหัตถการ (Intra-Procedure)

### ขั้นตอน

| # | ใครทำ | ทำอะไร | เอกสาร/ระบบ | AI ช่วยได้? |
|---|-------|--------|------------|------------|
| 2.1 | **Cardiologist** | ทำ Diagnostic Cath (37.22 + 88.56) | Cath report | ❌ |
| 2.2 | **Cardiologist** | ตัดสินใจ: PCI หรือ medical | Cath report | ❌ |
| 2.3 | **Cardiologist** | ทำ PCI + ใส่ stent (36.06/36.07) | Cath report | ❌ |
| 2.4 | **พยาบาล Cath Lab** | บันทึก: stent type, brand, size, lot number | Cath Lab record | ❌ |
| 2.5 | **พยาบาล Cath Lab** | บันทึก: ยาที่ใช้ (Heparin, Clopidogrel dose) | MAR (Medication Record) | ❌ |
| 2.6 | **พยาบาล Cath Lab** | บันทึก: D2B time (STEMI) | Cath Lab record | ❌ |

### ⚠️ จุดที่มักพลาด
- **Lot number stent ไม่ตรง** กับที่บันทึกใน GPO VMI → ติด HC09
- **ไม่บันทึก D2B time** → ขาดหลักฐาน quality indicator
- **ใช้ stent DES แต่บันทึกเป็น BMS** → ค่าชดเชยต่ำกว่าที่ควร

### 🤖 AI Recommendation
```
สร้าง Cath Lab Record Template ที่ capture ข้อมูลครบ:
☐ Stent: Type (BMS/DES), Brand, Size, Lot#, Qty
☐ Balloon: Brand, Size
☐ Guidewire: Brand
☐ ยา: Heparin dose, Loading dose (Clopidogrel/Ticagrelor/Prasugrel)
☐ D2B time (STEMI only)
☐ Contrast volume
```

---

## Phase 3: หลังทำหัตถการ (Post-Procedure)

### ขั้นตอน

| # | ใครทำ | ทำอะไร | เอกสาร/ระบบ | AI ช่วยได้? |
|---|-------|--------|------------|------------|
| 3.1 | **Cardiologist** | เขียน Cath Report + สรุปผล | Cath report | ❌ |
| 3.2 | **Cardiologist** | เขียน Procedure Note | Medical record | ❌ |
| 3.3 | **พยาบาล Ward** | Monitor post-PCI (sheath, groin, vitals) | Nursing record | ❌ |
| 3.4 | **Lab** | ส่ง Troponin follow-up (6-12 ชม. post) | Lab system | ❌ |
| 3.5 | **เภสัชกร** | จ่ายยา DAPT (Clopidogrel/Ticagrelor + ASA) | Pharmacy system | ❌ |

### ⚠️ จุดที่มักพลาด
- **Cath report ไม่ครบ** → ขาดหลักฐานสำหรับ appeal
- **Troponin ไม่ follow** → ขาดหลักฐาน NSTEMI diagnosis
- **ยา DAPT ไม่บันทึกใน DRU file** → Drug Catalog mismatch

---

## Phase 4: Discharge + Medical Coding

### ขั้นตอน

| # | ใครทำ | ทำอะไร | ระบบ | AI ช่วยได้? |
|---|-------|--------|------|------------|
| 4.1 | **แพทย์** | สรุป Discharge Summary | Medical record | ❌ |
| 4.2 | **Medical Coder** | Coding: PDx (ICD-10) | HIS | ⭐ **ใช่!** |
| 4.3 | **Medical Coder** | Coding: SDx — CC/MCC (ICD-10) | HIS | ⭐ **ใช่!** |
| 4.4 | **Medical Coder** | Coding: Procedures (ICD-9-CM) | HIS | ⭐ **ใช่!** |
| 4.5 | **เจ้าหน้าที่ Billing** | บันทึกค่ารักษา (CHA file) | HIS | ❌ |
| 4.6 | **เจ้าหน้าที่ Billing** | บันทึกอุปกรณ์ (ADP file) | HIS | ⚠️ ตรวจได้ |
| 4.7 | **เจ้าหน้าที่ Billing** | บันทึกยา (DRU file) | HIS | ⚠️ ตรวจได้ |
| 4.8 | **เจ้าหน้าที่ Billing** | ปิดสิทธิ์ / Authen verify | ระบบ สปสช. | ❌ |

### 🤖 AI ช่วย Phase 4 (Semi-Auto)

#### 4.2-4.4 ICD Coding Assistant

```
Coder กรอก Clinical Summary:
"ชาย 65 ปี STEMI anterior wall, primary PCI ใส่ DES LAD 1 ตัว
 มี DM, HT, CKD stage 3, EF 35%"

AI แนะนำ:
┌─────────────────────────────────────────┐
│ 📋 ICD CODING RECOMMENDATION           │
│                                         │
│ PDx: I21.0 (STEMI anterior wall)       │
│                                         │
│ SDx:                                    │
│  1. I50.21 — Acute systolic HF  ⭐ MCC │
│     (EF 35% → systolic + acute)        │
│  2. E11.65 — DM w hyperglycemia ⭐ CC  │
│     (ไม่ใช่ E11.9 ซึ่งไม่เป็น CC)     │
│  3. N18.3 — CKD stage 3         ⭐ CC  │
│  4. I10 — HT (ไม่มีผลต่อ RW)          │
│                                         │
│ Proc:                                   │
│  1. 36.07 — DES insertion              │
│  2. 37.22 — Left heart cath            │
│  3. 88.56 — Coronary angiography       │
│                                         │
│ Expected DRG: 05291 (w min CCC)        │
│ Expected RW: 11.4820                   │
│ Expected: ~95,858 บาท                  │
│                                         │
│ 💡 ถ้าไม่ใส่ I50.21:                   │
│    DRG จะเป็น 05290 (wo CCC)          │
│    RW = 8.6544                          │
│    เสียเงิน ~23,630 บาท               │
└─────────────────────────────────────────┘

Coder ตรวจทาน → ✅ ยืนยัน / ✏️ แก้ไข
```

#### 4.6-4.7 ADP/DRU Validation

```
AI ตรวจอัตโนมัติ:
┌─────────────────────────────────────────┐
│ ADP File Check:                         │
│ ⚠️ Stent: TYPE=5 ✅                    │
│ ⚠️ Stent CODE: [ต้องตรง สปสช.]        │
│ ⚠️ Lot#: [ต้องตรง GPO VMI]            │
│ ⚠️ Qty: 1 ตรง Cath report ✅           │
│                                         │
│ DRU File Check:                         │
│ ⚠️ Clopidogrel: TMT [xxxxxx] ✅/❌     │
│ ⚠️ Heparin: TMT [xxxxxx] ✅/❌         │
│ ⚠️ Contrast: TMT [xxxxxx] ✅/❌        │
└─────────────────────────────────────────┘
```

---

## Phase 5: ตรวจสอบก่อนส่ง (Pre-Submit) ← AI หลัก

### ขั้นตอน

| # | ใครทำ | ทำอะไร | ระบบ | AI ช่วยได้? |
|---|-------|--------|------|------------|
| 5.1 | **AI** | รัน 8 Checkpoints อัตโนมัติ | Cath Lab Checker API | ⭐ **อัตโนมัติ** |
| 5.2 | **AI** | ตรวจ Dx-Proc Match | API | ⭐ **อัตโนมัติ** |
| 5.3 | **AI** | ตรวจ CC/MCC Optimization | API | ⭐ **อัตโนมัติ** |
| 5.4 | **AI** | ตรวจ DRG + คำนวณเงิน | API | ⭐ **อัตโนมัติ** |
| 5.5 | **AI** | สรุปผล + Score | API | ⭐ **อัตโนมัติ** |
| 5.6 | **Coder/Billing** | ตรวจทานผล AI | Dashboard/LINE | ⭐ **Semi-Auto** |
| 5.7 | **Coder/Billing** | อนุมัติส่ง | Dashboard/LINE | คนตัดสิน |

### 🤖 AI Output: Claim Check Report

```
══════════════════════════════════════════
  CATH LAB CLAIM CHECK — AN 69-03556
══════════════════════════════════════════
Score: 75/100 | Status: ⚠️ WARNING

✅ CP1: Basic Data — PASS
✅ CP2: Dx-Proc Match — PASS (I21.0 + 36.07 + 37.22)
❌ CP3: Device Docs — CRITICAL (ไม่มี stent serial ใน ADP)
✅ CP4: 16-File — PASS
✅ CP5: Timing — PASS (ส่งภายใน 5 วัน)
💡 CP6: CC/MCC — เพิ่ม I50.21 = +23,630 บาท
✅ CP7: DRG 05290 verified (RW 8.6544)
⚠️ CP8: Drug — Clopidogrel TMT ต้องตรวจ

══════════════════════════════════════════
⚠️ ต้องแก้ก่อนส่ง:
1. เพิ่ม stent serial/lot ใน ADP file
2. ตรวจ Clopidogrel TMT code

💡 เพิ่มเงินได้:
1. เพิ่ม I50.21 (MCC) → DRG 05291 = +23,630 บาท

💰 ถ้าส่งตอนนี้: ~72,264 บาท
💰 ถ้าแก้ตาม AI: ~95,858 บาท
══════════════════════════════════════════
```

### Workflow Semi-Auto

```
AI รัน 8 checkpoints อัตโนมัติ
       ↓
Score ≥ 85, ไม่มี critical
  → ✅ แจ้ง LINE: "พร้อมส่ง"
  → คนกด [อนุมัติ] ใน LINE

Score 60-84, มี warning
  → ⚠️ แจ้ง LINE: "มี issues ต้องแก้"
  → แนบรายการที่ต้องแก้
  → คนแก้ → AI ตรวจใหม่ → อนุมัติ

Score < 60, มี critical
  → ❌ แจ้ง LINE: "ห้ามส่ง!"
  → แนบรายละเอียด
  → ต้องแก้ทุก critical ก่อน
```

---

## Phase 6: ส่ง e-Claim / FDH

### ขั้นตอน

| # | ใครทำ | ทำอะไร | ระบบ | AI ช่วยได้? |
|---|-------|--------|------|------------|
| 6.1 | **เจ้าหน้าที่ Billing** | Generate 16-file จาก HIS | HIS → e-Claim | ❌ (ต้องทำใน HIS) |
| 6.2 | **เจ้าหน้าที่ Billing** | Upload .ecd file เข้า e-Claim | eclaim.nhso.go.th | ❌ |
| 6.3 | **ระบบ e-Claim** | Validate + ประมวลผล (จ-พ-ศ) | e-Claim สปสช. | ❌ |
| 6.4 | **ระบบ e-Claim** | แจ้งผล: A (ผ่าน) / C (error) / D (deny) | REP file | ⭐ AI อ่านผล |

### ⚠️ จุดที่มักพลาด
- **Upload ผิด version** → ไฟล์ถูก reject
- **Upload ซ้ำ** → ติด D05 (Duplicate)
- **ลืม upload** → เกิน 30 วัน → ติด D06

---

## Phase 7: ติดตามผล + แก้ไข ← AI ช่วย

### 7A: ถ้าผ่าน (Status A)

| # | ใครทำ | ทำอะไร | AI ช่วยได้? |
|---|-------|--------|------------|
| 7A.1 | **ระบบ** | ออก Statement (กลางเดือน/สิ้นเดือน) | ❌ |
| 7A.2 | **การเงิน** | ตรวจยอดโอนเงิน | ⚠️ ตรวจ expected vs actual |
| 7A.3 | **AI** | เปรียบเทียบ DRG ที่คาด vs จริง | ⭐ **Feedback loop** |

### 7B: ถ้าติด C-Error

| # | ใครทำ | ทำอะไร | AI ช่วยได้? |
|---|-------|--------|------------|
| 7B.1 | **AI** | อ่าน REP file → วิเคราะห์ C-code | ⭐ **อัตโนมัติ** |
| 7B.2 | **AI** | แนะนำวิธีแก้เฉพาะ C-code | ⭐ **อัตโนมัติ** |
| 7B.3 | **Coder/Billing** | แก้ไขตาม AI แนะนำ | **Semi-Auto** |
| 7B.4 | **AI** | ตรวจซ้ำหลังแก้ (8 checkpoints) | ⭐ **อัตโนมัติ** |
| 7B.5 | **เจ้าหน้าที่** | ส่งใหม่ | ❌ |

### 7C: ถ้าถูก Deny

| # | ใครทำ | ทำอะไร | AI ช่วยได้? |
|---|-------|--------|------------|
| 7C.1 | **AI** | วิเคราะห์ Root Cause | ⭐ **Deny Analyzer** |
| 7C.2 | **AI** | ประเมิน Recovery Chance | ⭐ **อัตโนมัติ** |
| 7C.3 | **AI** | แนะนำ: auto_fix / appeal / escalate / write_off | ⭐ **อัตโนมัติ** |
| 7C.4 | **AI** | ร่าง Appeal Letter (ถ้าควรอุทธรณ์) | ⭐ **Appeal Drafter** |
| 7C.5 | **แพทย์/Coder** | ตรวจทาน Appeal Letter | **Semi-Auto** |
| 7C.6 | **ผอ.รพ.** | ลงนาม | ❌ |
| 7C.7 | **เจ้าหน้าที่** | ส่ง Appeal + เอกสารแนบ | ❌ |

### 🤖 AI Deny Analysis (ตัวอย่างเคสจริง)

```
══════════════════════════════════════════
  DENY ANALYSIS — AN 69-03556
══════════════════════════════════════════
Category: device_documentation
Severity: HIGH (71,322 บาท)

🔍 Root Cause:
HC09 = อุปกรณ์/อวัยวะเทียม documentation ไม่ครบ
- INST (31,490 บาท) ถูกปฏิเสธ
- Clopidogrel drug catalog mismatch

🔧 Fix Steps:
1. ตรวจ ADP file: TYPE/CODE ตรง สปสช.
2. ตรวจ stent serial ตรง GPO VMI
3. ตรวจ Clopidogrel TMT code
4. แก้แล้วส่งใหม่

📊 Recovery Chance: 85%
💰 Estimated Recovery: 71,322 บาท
🎯 Action: AUTO_FIX (แก้ข้อมูลแล้วส่งใหม่)
══════════════════════════════════════════
```

---

## Timeline: เส้นเวลาทั้ง Workflow

```
Day 0: ผู้ป่วยเข้า Cath Lab
       ├── Authen Code ✓
       ├── ทำ PCI + ใส่ stent
       └── บันทึก Cath report

Day 1-2: Post-PCI Ward
       ├── Troponin follow-up
       ├── DAPT prescribed
       └── Discharge planning

Day 2-3: Discharge
       ├── Discharge Summary
       ├── Medical Coding (AI ช่วย)
       ├── Billing (AI ตรวจ)
       └── 🤖 AI Pre-Submit Check

Day 3-5: ส่ง e-Claim ← เป้าหมาย fast track
       └── Upload .ecd file

Day 5-10: รอผล
       ├── จ-พ-ศ: ระบบประมวลผล
       └── 🤖 AI อ่าน REP file

Day 10-15: ผลออก
       ├── A = ✅ ผ่าน → รอ Statement
       ├── C = ⚠️ แก้ไข → 🤖 AI แนะนำ fix
       └── D = ❌ Deny → 🤖 AI วิเคราะห์ + Appeal

Day 15-22: Statement ออก
       └── 💰 เงินโอนเข้า

Day 22-30: (ถ้าถูก deny)
       ├── 🤖 AI draft Appeal
       ├── คนตรวจ + ส่ง
       └── รอผล Appeal (15 วันทำการ)
```

---

## สรุป: AI ช่วยตรงไหนบ้าง

| Phase | งาน | คนทำ | AI ช่วย | ประหยัดเวลา |
|-------|-----|------|---------|------------|
| **4** | ICD Coding | Coder | ⭐ แนะนำ codes + CC/MCC | ~30 นาที/เคส |
| **4** | ADP/DRU check | Billing | ⭐ ตรวจอัตโนมัติ | ~15 นาที/เคส |
| **5** | Pre-submit check | Billing | ⭐ 8 checkpoints auto | ~45 นาที/เคส |
| **5** | DRG verify | Billing | ⭐ คำนวณ RW + เงิน | ~10 นาที/เคส |
| **7B** | C-Error fix | Billing | ⭐ วิเคราะห์ + แนะนำ | ~30 นาที/เคส |
| **7C** | Deny analysis | Coder | ⭐ Root cause + fix | ~60 นาที/เคส |
| **7C** | Appeal letter | แพทย์ | ⭐ Draft อัตโนมัติ | ~120 นาที/เคส |

**รวมประหยัดต่อเคส: ~5 ชั่วโมง** (จาก ~6-8 ชม. เหลือ ~1-3 ชม.)

---

## ข้อแนะนำ: ทำอะไรต่อ

### Sprint 1 (สัปดาห์นี้) — Quick Win

| # | ทำอะไร | ผลลัพธ์ | ความยาก |
|---|--------|---------|--------|
| 1 | **ทดสอบ API กับเคสจริง** — รัน FastAPI server แล้วยิง POST /cathlab/check ด้วย AN 69-03556 | พิสูจน์ว่า AI วิเคราะห์ถูก | ง่าย |
| 2 | **ขอ 181 deny cases จากทีม Noi** — FDH export CSV ทั้งเดือน | ได้ test data จริง + วัด accuracy | รอคน |
| 3 | **ขอ Drug Catalogue export** จากระบบ drug.nhso.go.th ของ รพ. | ตรวจ TMT code ได้จริง | รอคน |

### Sprint 2 (สัปดาห์หน้า) — Semi-Auto Pipeline

| # | ทำอะไร | ผลลัพธ์ | ความยาก |
|---|--------|---------|--------|
| 4 | **สร้าง LINE Notify** — แจ้งผลตรวจ + ขออนุมัติผ่าน LINE | ทีม billing เห็นผลทันที | กลาง |
| 5 | **สร้าง CSV batch upload** — upload e-Claim CSV → AI ตรวจทุกเคส | ตรวจทีเดียวหลายเคส | ง่าย |
| 6 | **วัดผล: AI accuracy** — เทียบ AI recommendation vs ผลจริง | รู้ว่า AI เก่งแค่ไหน | กลาง |

### Sprint 3 (2 สัปดาห์) — Optimize

| # | ทำอะไร | ผลลัพธ์ | ความยาก |
|---|--------|---------|--------|
| 7 | **เชื่อม Claude API** — ให้ AI วิเคราะห์ clinical context ลึกขึ้น | วิเคราะห์ที่ rule engine ทำไม่ได้ | กลาง |
| 8 | **Dashboard Cath Lab** — หน้าเว็บแสดง KPI + cases + pipeline | ผู้บริหารเห็นภาพ | ยาก |
| 9 | **Feedback loop** — เก็บผล approved/denied → ปรับ model | AI เก่งขึ้นเรื่อยๆ | กลาง |

### Sprint 4 (1 เดือน) — Scale

| # | ทำอะไร | ผลลัพธ์ | ความยาก |
|---|--------|---------|--------|
| 10 | **เพิ่มแผนก OR** — ใช้ pattern เดียวกับ Cath Lab | ครอบคลุม 2 แผนก | กลาง |
| 11 | **เชื่อม HOSxP** — ดึง case อัตโนมัติจาก HIS | ไม่ต้อง upload CSV | ยาก |
| 12 | **Full Auto** — scan ทุกเช้า → ตรวจ → ส่ง → ติดตาม | Zero manual work | ยาก |

### 🎯 เป้าหมายวัดผล

| KPI | ก่อน AI | หลัง Semi-Auto (เป้า 1 เดือน) | หลัง Full Auto (เป้า 3 เดือน) |
|-----|---------|-------------------------------|-------------------------------|
| Deny rate Cath Lab | ~10% | **<5%** | **<3%** |
| เวลาต่อเคส | 6-8 ชม. | **1-3 ชม.** | **<30 นาที** |
| CC/MCC capture rate | ~60% | **>80%** | **>90%** |
| Revenue uplift/เดือน | 0 | **+100K** | **+300K** |
| Appeal success rate | ~50% | **>70%** | **>80%** |

---

## Action Item ตอนนี้

```
┌─────────────────────────────────────────────────┐
│  ✅ ทำได้เลยโดยไม่ต้องรอใคร:                   │
│                                                  │
│  1. รัน: uvicorn api.main:app --reload          │
│  2. เปิด: http://localhost:8000/docs            │
│  3. ยิง POST /api/v1/cathlab/check              │
│     ด้วยเคสจริง AN 69-03556                     │
│  4. ยิง POST /api/v1/cathlab/analyze-deny       │
│     ด้วย deny codes HC09, IP01, HC13            │
│  5. ดูผล → ถ้าถูก = พร้อมใช้งานจริง            │
│                                                  │
│  📞 ขอจากทีม Noi:                               │
│  1. FDH export CSV (181 deny cases)             │
│  2. Drug Catalogue export ของ รพ.               │
│  3. Cath Lab case log (procedure + outcome)     │
└─────────────────────────────────────────────────┘
```
