# คู่มือการใช้ AI ช่วยทำ Claim ห้อง Cath Lab

> Hospital: รพ.พญาไทศรีราชา (11855)
> AI System: Claude + Cath Lab Claim Checker
> Version: 1.0 — March 2026
> ผู้จัดทำ: Dr.Kasemson Kasemwong

---

## สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [เตรียมเอกสารก่อนเริ่มงาน](#2-เตรียมเอกสารก่อนเริ่มงาน)
3. [ขั้นตอนที่ 1: Coding — AI แนะนำ ICD](#3-ขั้นตอนที่-1-coding)
4. [ขั้นตอนที่ 2: Pre-Submit Check — AI ตรวจ 8 จุด](#4-ขั้นตอนที่-2-pre-submit-check)
5. [ขั้นตอนที่ 3: Deny Analysis — AI วิเคราะห์](#5-ขั้นตอนที่-3-deny-analysis)
6. [ขั้นตอนที่ 4: Appeal — AI ร่างหนังสือ](#6-ขั้นตอนที่-4-appeal)
7. [Batch Mode — ตรวจทีเดียวหลายเคส](#7-batch-mode)
8. [Checklist สำหรับแต่ละบทบาท](#8-checklist)
9. [FAQ & Troubleshooting](#9-faq)

---

## 1. ภาพรวมระบบ

### AI ช่วย 4 งานหลัก

```
📋 Coding        → AI อ่าน clinical data → แนะนำ ICD-10 + ICD-9-CM
🔍 Pre-Submit    → AI ตรวจ 8 checkpoints → บอก score + สิ่งที่ต้องแก้
🔬 Deny Analysis → AI อ่าน deny code → บอกสาเหตุ + วิธีแก้
📝 Appeal        → AI ร่างหนังสืออุทธรณ์ → คนแค่ตรวจ + เซ็น
```

### ใครใช้ตอนไหน

| บทบาท | ใช้ AI ตอนไหน | ขั้นตอนที่ |
|-------|-------------|----------|
| **Medical Coder** | หลัง discharge ก่อน coding | ขั้นตอนที่ 1 |
| **เจ้าหน้าที่ Billing** | หลัง coding ก่อนส่ง e-Claim | ขั้นตอนที่ 2 |
| **Medical Coder** | เมื่อได้ REP file กลับมาติด C/Deny | ขั้นตอนที่ 3 |
| **แพทย์/ผอ.รพ.** | เมื่อต้องอุทธรณ์ | ขั้นตอนที่ 4 |

---

## 2. เตรียมเอกสารก่อนเริ่มงาน

### 2.1 เอกสารที่ต้องเตรียม (ทุกเคส)

```
📁 เอกสารจากห้อง Cath Lab
├── 📄 Cath Report (รายงานผลการสวนหัวใจ)
│   ├── Findings: กี่เส้น ตีบ % (เช่น LAD 95% stenosis)
│   ├── Intervention: ทำอะไร (PCI, stent ชนิดไหน)
│   ├── Stent info: Brand, Size, Lot number
│   └── D2B time (STEMI เท่านั้น)
│
├── 📄 Procedure Note (บันทึกหัตถการ)
│   ├── แพทย์ผู้ทำ
│   ├── วิธีทำ (access site, technique)
│   └── Complications (ถ้ามี)
│
├── 📄 EKG (12-lead)
│   ├── ก่อนทำ: ST elevation/depression ไหม
│   └── หลังทำ: ST resolution ไหม
│
├── 📄 Lab Results
│   ├── Troponin I/T: ค่าเท่าไหร่ (+ เวลา)
│   ├── Troponin follow-up (6-12 ชม.)
│   ├── CBC, BUN, Cr, eGFR
│   ├── Electrolytes (Na, K)
│   ├── PT/INR, aPTT
│   ├── HbA1c (ถ้ามี DM)
│   └── Lipid profile
│
├── 📄 Echo Report (ถ้ามี)
│   ├── EF% → สำคัญมาก (ใช้ code HF)
│   ├── Wall motion abnormality
│   └── Valve function
│
└── 📄 Discharge Summary
    ├── Final diagnosis
    ├── Procedures done
    ├── Discharge medications
    └── Follow-up plan

📁 เอกสารจาก Billing
├── 📄 ค่ารักษาพยาบาล (CHA)
├── 📄 รายการอุปกรณ์ (ADP) — stent, balloon, wire
├── 📄 รายการยา (DRU) — Clopidogrel, Heparin ฯลฯ
└── 📄 สิทธิ์ผู้ป่วย (INS) — UCS/SSS/CSMBS

📁 เอกสารจากระบบ
├── 📄 Authen Code status
└── 📄 สิทธิ์ตรวจสอบ (ณ วันที่รับบริการ)
```

### 2.2 ไฟล์ที่ต้อง Load ให้ Claude

**สิ่งที่ต้อง copy/paste หรือ upload ให้ AI ทุกครั้ง:**

```
=== ข้อมูลผู้ป่วย ===
HN: [เลข HN]
AN: [เลข AN]
CID: [เลข 13 หลัก]
เพศ: [ชาย/หญิง]
อายุ: [ปี]
สิทธิ์: [UC/SSS/CSMBS]
วันที่ Admit: [DD/MM/YYYY HH:MM]
วันที่ Discharge: [DD/MM/YYYY HH:MM]
Authen Code: [รหัส หรือ ไม่มี]

=== Clinical Data ===
Diagnosis (แพทย์สรุป): [เขียนสั้นๆ เช่น STEMI anterior wall]
EKG: [ST elevation V1-V4 / normal / ST depression]
Troponin: [ค่า + หน่วย เช่น 15.2 ng/ml]
Echo EF: [เช่น 35% หรือ ไม่ได้ทำ]
eGFR/Cr: [เช่น eGFR 45, Cr 1.8]
Blood sugar: [ถ้ามี DM]
ประวัติโรคร่วม: [DM, HT, CKD, COPD, AF ฯลฯ]

=== Procedure Data ===
Procedure ที่ทำ: [เช่น Primary PCI + DES LAD 1 ตัว]
Stent: [Type=DES/BMS, Brand=..., Size=...mm, Lot#=...]
จำนวน Stent: [กี่ตัว]
D2B time: [นาที — STEMI เท่านั้น]
Cath Findings: [เช่น LAD 95%, LCx 40%, RCA normal]
ยาที่ใช้: [Heparin dose, Clopidogrel loading, Contrast volume]

=== ถ้าถูก Deny (ขั้นตอนที่ 3-4 เท่านั้น) ===
Deny Codes: [เช่น HC09, IP01, HC13]
Deny Reason: [ข้อความจาก REP file]
DRG ที่ได้: [เช่น 05290]
RW: [เช่น 8.6544]
ยอดเรียกเก็บ: [บาท]
ยอดที่ถูก deny: [บาท]
รายการที่ถูก deny: [เช่น INST 31,490, CLOPIDOGREL_DRUG]
```

---

## 3. ขั้นตอนที่ 1: Coding — AI แนะนำ ICD

### เมื่อไหร่ใช้
หลังผู้ป่วย discharge แล้ว ก่อน code ICD ลง HIS

### ใครใช้
Medical Coder

### วิธีใช้

**Step 1:** เตรียมข้อมูล Clinical ตามหัวข้อ 2.2

**Step 2:** เปิด Claude แล้วพิมพ์:

```
ช่วย coding ICD สำหรับเคส Cath Lab:

=== ข้อมูลผู้ป่วย ===
HN: 69-09349
AN: 69-03556
เพศ: หญิง อายุ: 65 ปี
สิทธิ์: UC
Admit: 27/02/2569  Discharge: 01/03/2569

=== Clinical Data ===
Diagnosis: STEMI anterior wall
EKG: ST elevation V1-V4
Troponin: 15.2 ng/ml (สูง)
Echo EF: 35%
eGFR: 45 (Cr 1.8)
ประวัติ: DM type 2 (HbA1c 8.2), HT, CKD

=== Procedure ===
Primary PCI: DES LAD 1 ตัว (Xience 3.0x28mm, Lot#AB123)
Cath: LAD 95% proximal, LCx 40%, RCA normal
D2B time: 78 นาที
ยา: Heparin 7500U, Clopidogrel 600mg loading
```

**Step 3:** AI จะตอบ:

```
📋 ICD CODING RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PDx: I21.0 — Acute transmural MI of anterior wall
เหตุผล: ST elevation V1-V4 + Troponin 15.2 + LAD 95%

SDx:
1. I50.21 — Acute systolic HF           ⭐ MCC (+23,630 บาท)
   เหตุผล: EF 35% (<40%) + acute event

2. E11.65 — DM type 2 w hyperglycemia   ⭐ CC
   เหตุผล: HbA1c 8.2 (ไม่ใช่ E11.9 ซึ่งไม่เป็น CC)
   ⚠️ ถ้าใช้ E11.9 จะเสียโอกาส CC

3. N18.3 — CKD stage 3a                 ⭐ CC
   เหตุผล: eGFR 45 (stage 3a = 45-59)

4. I10 — Essential HT                   ไม่มีผลต่อ RW

Procedures:
1. 36.07 — Insertion of drug-eluting coronary stent
2. 37.22 — Left heart catheterization
3. 88.56 — Coronary arteriography (Judkins)

Expected DRG: 05291 (Acute MI w single vessel PTCA w min CCC)
Expected RW: 11.4820
Expected Payment: ~95,858 บาท (base rate 8,350)

💡 ถ้าไม่ใส่ I50.21 (MCC):
   DRG: 05290 → RW: 8.6544 → ~72,264 บาท
   เสียเงิน: 23,594 บาท
```

**Step 4:** Coder ตรวจทาน

```
✅ ตรวจสอบ checklist:
☐ PDx ตรงกับ clinical จริงไหม?
  → I21.0 ตรง: ST elevation V1-V4 + Troponin สูง ✓

☐ SDx มี documentation สนับสนุนไหม?
  → I50.21: Echo EF 35% มีในเวชระเบียน ✓
  → E11.65: HbA1c 8.2 มีผล lab ✓
  → N18.3: eGFR 45 มีผล lab ✓

☐ Procedures ตรงกับ Cath report ไหม?
  → 36.07 (DES): ตรง Xience stent ✓
  → 37.22 + 88.56: ตรง diagnostic cath ✓

☐ ไม่มี upcode? (code ตรง clinical reality)
  → ✓ ทุก code มี documentation

✅ ยืนยัน → บันทึกลง HIS
```

### ⚠️ สิ่งที่ต้องระวัง

| สถานการณ์ | อย่าทำ | ให้ทำ |
|-----------|--------|------|
| Troponin สูงนิดเดียว | Code เป็น STEMI | ตรวจว่า EKG มี ST elevation จริงไหม ถ้าไม่มี → NSTEMI (I21.4) |
| EF ไม่ได้ทำ Echo | เดา EF แล้ว code I50.21 | ไม่ code HF ถ้าไม่มี Echo report |
| DM ไม่มี complication | Code E11.65 เพื่อได้ CC | ต้องมี blood sugar >250 documented |
| AI แนะนำ code ที่ไม่แน่ใจ | ใส่ตามโดยไม่ตรวจ | ถาม AI ว่าต้องมี documentation อะไร |

---

## 4. ขั้นตอนที่ 2: Pre-Submit Check — AI ตรวจ 8 จุด

### เมื่อไหร่ใช้
หลัง coding + billing เสร็จ ก่อน upload e-Claim

### ใครใช้
เจ้าหน้าที่ Billing / หัวหน้า Billing

### วิธีใช้

**Step 1:** เตรียมข้อมูล claim ครบ (ตามหัวข้อ 2.2 + ICD codes ที่ code แล้ว)

**Step 2:** พิมพ์ใน Claude:

```
ตรวจ claim ก่อนส่ง e-Claim:

HN: 69-09349 | AN: 69-03556
CID: 2411300021503
หญิง 65 ปี | สิทธิ์ UC | Authen: PP1007991295
Admit: 27/02/2569 11:44 | D/C: 01/03/2569 13:00

PDx: I21.0
SDx: I50.21, E11.65, N18.3, I10
Proc: 36.07, 37.22, 88.56

Stent: DES Xience 3.0x28mm, Lot#AB123, จำนวน 1, TYPE=5
ยา: Clopidogrel (HospCode=CLO075, TMT=xxxxxx)
ค่ารักษา: 31,517 บาท
ค่าอุปกรณ์ INST: 31,490 บาท

DRG ที่คาดหวัง: 05291
```

**Step 3:** AI ตรวจ 8 Checkpoints แล้วตอบ:

```
═══════════════════════════════════════
  CATH LAB PRE-SUBMIT CHECK
  AN: 69-03556 | Score: 90/100
═══════════════════════════════════════

✅ CP1 Basic Data
   AN, HN, CID ✓ | เพศ/อายุ match PDx ✓
   Admit < D/C ✓ | LOS = 2 วัน ✓

✅ CP2 Dx-Proc Match
   I21.0 (STEMI) + 36.07 (DES) + 37.22 (Cath) ✓
   Dx-Proc สอดคล้อง

⚠️ CP3 Device Docs
   Stent TYPE=5 ✓ | Qty=1 ✓
   ⚠️ ตรวจ Lot#AB123 ตรง GPO VMI หรือไม่
   → ให้ Billing ตรวจกับคลังเวชภัณฑ์

✅ CP4 16-File Completeness
   DIA ✓ | OPR ✓ | ADP ✓ | DRU ✓ | CHA ✓ | INS ✓

✅ CP5 Timing
   LOS=2 วัน | ส่งภายใน 30 วัน ✓
   Authen Code PP1007991295 ✓

✅ CP6 CC/MCC
   I50.21 (MCC) ✓ | E11.65 (CC) ✓ | N18.3 (CC) ✓
   CC/MCC ครบถ้วน ไม่มี optimization เพิ่ม

✅ CP7 DRG Verification
   DRG 05291: Acute MI w single vessel PTCA w min CCC
   RW = 11.4820 | Payment ~95,858 บาท ✓

⚠️ CP8 Drug/Lab Catalog
   Clopidogrel TMT=xxxxxx
   → ตรวจว่า TMT ตรง Drug Catalogue ของ รพ.

═══════════════════════════════════════
📊 สรุป: 6 PASS / 2 WARNING / 0 CRITICAL
🎯 Score: 90/100 — พร้อมส่ง (หลังแก้ warning)

⚠️ ก่อนส่ง ให้ตรวจ 2 จุด:
1. Lot# stent ตรง GPO VMI ✓/✗
2. Clopidogrel TMT ตรง Drug Catalogue ✓/✗

💰 Expected: 95,858 บาท
═══════════════════════════════════════
```

**Step 4:** Billing ตรวจ 2 จุดที่ AI flag แล้วกด approve

```
☐ ตรวจ GPO VMI: Lot#AB123 = ✅ ตรง
☐ ตรวจ Drug Catalogue: Clopidogrel TMT = ✅ ตรง
→ ✅ พร้อมส่ง e-Claim
```

---

## 5. ขั้นตอนที่ 3: Deny Analysis — AI วิเคราะห์

### เมื่อไหร่ใช้
เมื่อได้ REP file กลับมาแล้วเคสติด C-error หรือ Deny

### ใครใช้
Medical Coder / เจ้าหน้าที่ Billing

### วิธีใช้

**Step 1:** เปิด REP file จาก e-Claim → หาเคสที่ติด C/Deny

**Step 2:** เตรียมข้อมูลจาก REP file:

```
จาก REP file:
- AN: 69-03556
- Status: DENY
- Error Codes: HC09, IP01, HC13
- Items ที่ถูก deny: CLOPIDOGREL_DRUG, INST, IPINRGR
- DRG: 05290
- RW: 8.6544
- ยอดเรียกเก็บ: 71,322 บาท
- ค่า INST ที่ถูก deny: 31,490 บาท
```

**Step 3:** พิมพ์ใน Claude:

```
เคส Cath Lab ถูก deny ช่วยวิเคราะห์:

AN: 69-03556
HN: 69-09349
Admit: 27/02/2569 | D/C: 01/03/2569
PDx: I21.0 | Proc: 36.06, 37.22, 88.56
DRG: 05290 | RW: 8.6544
สิทธิ์: UC

Deny Codes: HC09, IP01, HC13
Items ถูก deny: CLOPIDOGREL_DRUG, INST (31,490 บาท), IPINRGR
ยอดที่ควรได้: 71,322 บาท
ยอดที่ได้จริง: 0 บาท
```

**Step 4:** AI วิเคราะห์แล้วตอบ:

```
═══════════════════════════════════════
  DENY ANALYSIS — AN 69-03556
═══════════════════════════════════════
❌ เงินหาย: 71,322 บาท
📊 Recovery Chance: 85%

🔍 สาเหตุแต่ละ Deny Code:
━━━━━━━━━━━━━━━━━━━━━━━━━━━

HC09: อุปกรณ์/อวัยวะเทียมในการทำหัตถการ
  → Stent documentation มีปัญหา
  → สาเหตุที่เป็นไปได้:
    1. ADP file: CODE ไม่ตรงกับ สปสช. กำหนด
    2. Serial/Lot number ไม่ตรง GPO VMI
    3. TYPE ใน ADP ไม่ถูกต้อง
  → แก้: ตรวจ ADP file ทุก field

IP01: IP ในเขต
  → การจ่าย IP ตามปกติ
  → ไม่ใช่ปัญหาหลัก (ถูก deny พ่วงกับ HC09)

HC13: เงื่อนไข HC เพิ่มเติม
  → เอกสาร device ไม่ครบ
  → แก้: ส่งเอกสารเพิ่มเติม

CLOPIDOGREL_DRUG ถูก deny:
  → TMT code ไม่ตรง Drug Catalogue
  → แก้: ตรวจ HospDrugCode → TMT mapping

🔧 วิธีแก้ (เรียงตามลำดับ):
━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. เปิด ADP file ของเคสนี้
   ตรวจ: TYPE=5 ?, CODE=ตรง สปสช.?,
   Lot#=ตรง GPO VMI?, Qty=ตรง Cath report?

2. เปิด DRU file
   ตรวจ Clopidogrel: HospDrugCode → TMT
   ถ้า TMT ไม่ตรง → ไป Drug Catalogue แก้ mapping

3. แก้ไขข้อมูลใน HIS

4. Generate 16-file ใหม่

5. ส่งใหม่ผ่าน e-Claim (ไม่ต้อง appeal)

🎯 Action: AUTO_FIX (แก้ข้อมูลแล้วส่งใหม่)
⏰ Deadline: ส่งภายใน [วันที่] (30 วันหลัง D/C)
═══════════════════════════════════════
```

**Step 5:** ทำตาม AI แนะนำ

```
☐ 1. ตรวจ ADP file:
     TYPE = 5 ✅
     CODE = [ตรวจกับ fee schedule สปสช.]
     Lot# = [ตรวจกับ GPO VMI record]
     Qty = 1 ตรง Cath report ✅

☐ 2. ตรวจ DRU file:
     Clopidogrel HospDrugCode = CLO075
     TMT ที่ map = [ตรวจใน Drug Catalogue]
     ถ้าไม่ตรง → แก้ใน Drug Catalogue program

☐ 3. แก้ใน HIS แล้ว

☐ 4. Generate 16-file ใหม่

☐ 5. ส่ง e-Claim → รอผล
```

---

## 6. ขั้นตอนที่ 4: Appeal — AI ร่างหนังสือ

### เมื่อไหร่ใช้
เมื่อ deny แล้วแก้ข้อมูลไม่ได้ ต้องอุทธรณ์เป็นทางการ

### ใครใช้
Medical Coder → แพทย์ตรวจ → ผอ.รพ. เซ็น

### วิธีใช้

**Step 1:** พิมพ์ใน Claude:

```
ช่วยร่างหนังสืออุทธรณ์สำหรับเคสนี้:

AN: 69-03556
ผู้ป่วย: นาง ลังกา เทยณี
Admit: 27/02/2569 | D/C: 01/03/2569
PDx: I21.0 (STEMI anterior wall)
Proc: 36.07 (DES insertion), 37.22, 88.56
DRG: 05290 | RW: 8.6544

Deny: HC09 — อุปกรณ์/อวัยวะเทียม
ยอด: 71,322 บาท
สาเหตุ: Stent documentation — ได้ตรวจแล้วข้อมูลถูกต้อง
หลักฐาน: Cath report + GPO VMI record + ADP file ที่แก้แล้ว

ส่งถึง: สปสช. เขต 6
```

**Step 2:** AI จะร่างหนังสือให้:

```
═══════════════════════════════════════
  APPEAL LETTER (DRAFT)
═══════════════════════════════════════

ที่ พศ.11855/____
                    โรงพยาบาลพญาไทศรีราชา
                    วันที่ ____ มีนาคม 2569

เรื่อง ขอทบทวนผลการตรวจสอบการขอรับค่าใช้จ่าย
      เพื่อบริการสาธารณสุข

เรียน ผู้อำนวยการสำนักงานหลักประกันสุขภาพ
     แห่งชาติ เขต 6 ระยอง

   ตามที่โรงพยาบาลพญาไทศรีราชา รหัส 11855
ได้ส่งข้อมูลการขอรับค่าใช้จ่ายเพื่อบริการ
สาธารณสุข สำหรับผู้ป่วย

   AN: 69-03556
   วันที่รับเข้า: 27 กุมภาพันธ์ 2569
   วันที่จำหน่าย: 1 มีนาคม 2569
   การวินิจฉัย: I21.0 Acute transmural
   myocardial infarction of anterior wall
   หัตถการ: 36.07 Insertion of drug-eluting
   coronary artery stent

   ทางโรงพยาบาลได้รับแจ้งว่าข้อมูลดังกล่าว
ไม่ผ่านการตรวจสอบ เนื่องจาก HC09 (อุปกรณ์
และอวัยวะเทียมในการทำหัตถการ)

   ข้อชี้แจง:
   1. ผู้ป่วยรายนี้เข้ารับการรักษาด้วยอาการ
เจ็บหน้าอกรุนแรง ตรวจ EKG พบ ST elevation
V1-V4 ร่วมกับ Troponin I สูง 15.2 ng/ml
วินิจฉัยเป็น STEMI anterior wall จึงได้ทำ
Primary PCI ใส่ Drug-eluting stent ที่ LAD
ตามแนวทางเวชปฏิบัติ

   2. อุปกรณ์ที่ใช้ได้บันทึกข้อมูลครบถ้วน
ตาม ADP file โดย TYPE=5 (อวัยวะเทียม)
Serial number ตรงกับ GPO VMI record

   3. ทางโรงพยาบาลได้ตรวจสอบและแก้ไข
ข้อมูลเรียบร้อยแล้ว ดังเอกสารแนบ

เอกสารแนบ:
1. สำเนาเวชระเบียน
2. Cath Report
3. ADP file ที่แก้ไขแล้ว
4. GPO VMI record (Lot# confirmation)
5. ผลตรวจ Troponin + EKG

   จึงเรียนมาเพื่อโปรดพิจารณาทบทวน

   ขอแสดงความนับถือ

   (ลงนาม)
   ผู้อำนวยการโรงพยาบาลพญาไทศรีราชา
═══════════════════════════════════════
```

**Step 3:** แพทย์ตรวจทาน → ผอ. เซ็น → ส่งพร้อมเอกสารแนบ

```
☐ แพทย์ตรวจทานเนื้อหา clinical ✓
☐ ผอ.รพ. ลงนาม ✓
☐ แนบเอกสาร:
  ☐ สำเนาเวชระเบียน
  ☐ Cath Report
  ☐ ADP file (แก้แล้ว)
  ☐ GPO VMI record
  ☐ ผล Lab (Troponin, EKG)
☐ ส่ง สปสช. เขต 6
☐ บันทึกวันที่ส่ง: ____
☐ รอผล: 15 วันทำการ
```

---

## 7. Batch Mode — ตรวจทีเดียวหลายเคส

### เมื่อไหร่ใช้
ตรวจเคสทั้งเดือน / ตรวจ REP file ที่มีหลายเคส

### วิธีใช้

**Step 1:** Export e-Claim CSV file

**Step 2:** Upload ผ่าน API:
```
POST /api/v1/cathlab/parse-eclaim
Body: [upload CSV file]
```

**Step 3:** หรือพิมพ์ใน Claude:

```
ตรวจ deny cases ทั้งหมดจาก REP file เดือนนี้:

เคส 1: AN 69-03556, DRG 05290, Deny HC09+IP01, INST 31,490
เคส 2: AN 69-03602, DRG 05220, Deny C210, ยอด 17,869
เคส 3: AN 69-03618, DRG 05291, Deny D06, ส่งเกิน 35 วัน
เคส 4: AN 69-03625, DRG 05530, Deny D10, PDx I25.1 + PCI
...
```

**Step 4:** AI จะสรุป:

```
═══════════════════════════════════════
  BATCH ANALYSIS — 4 CASES
═══════════════════════════════════════

PRIORITY (แก้ก่อน — เงินมาก):
🔴 AN 69-03556: 71,322 บาท | HC09 | AUTO_FIX (85%)
🔴 AN 69-03625: 72,264 บาท | D10 | AUTO_FIX (90%)
   → PDx I25.1 ควรเปลี่ยนเป็น I21.x ถ้าเป็น acute

MEDIUM:
🟡 AN 69-03602: 17,869 บาท | C210 | AUTO_FIX (80%)
   → DRG group ไม่ได้ ตรวจ ICD codes

LOW:
🔵 AN 69-03618: 95,858 บาท | D06 | APPEAL (30%)
   → ส่งเกิน 30 วัน โอกาสน้อย

TOTAL:
  เงินที่หาย: 257,313 บาท
  คาดว่ากู้คืนได้: ~161,455 บาท (63%)
═══════════════════════════════════════
```

---

## 8. Checklist สำหรับแต่ละบทบาท

### Medical Coder — Daily Checklist

```
เช้า:
☐ เปิด HIS ดูเคส Cath Lab ที่ D/C เมื่อวาน
☐ เตรียม clinical data ตามหัวข้อ 2.2
☐ ใช้ AI ช่วย coding (ขั้นตอนที่ 1)
☐ ตรวจทาน AI recommendation
☐ บันทึก ICD codes ลง HIS

บ่าย:
☐ เปิด REP file ที่ได้รับ
☐ แยกเคสที่ติด C / Deny
☐ ใช้ AI วิเคราะห์ deny (ขั้นตอนที่ 3)
☐ แก้ไขตาม AI แนะนำ
☐ ส่งใหม่ / ส่ง appeal
```

### Billing — Daily Checklist

```
เช้า:
☐ ตรวจเคสที่ code แล้วรอส่ง
☐ ใช้ AI pre-submit check (ขั้นตอนที่ 2)
☐ แก้ตาม AI flag (ADP, DRU, timing)
☐ Upload e-Claim
☐ บันทึกเลขที่ส่ง

บ่าย:
☐ ตรวจ Statement / ยอดโอน
☐ เทียบ expected vs actual
☐ Report ให้หัวหน้า
```

### แพทย์ — Weekly

```
☐ ตรวจ Appeal draft ที่ AI ร่าง
☐ แก้ไข clinical justification (ถ้าจำเป็น)
☐ ส่ง ผอ. ลงนาม
```

---

## 9. FAQ & Troubleshooting

### Q: AI แนะนำ code ที่ไม่แน่ใจ ทำยังไง?

**A:** ถาม AI ต่อ:
```
code I50.21 ต้องมี documentation อะไรบ้างถึงจะ code ได้?
```
AI จะตอบ:
```
I50.21 (Acute systolic HF) ต้องมี:
1. Echo report ที่ระบุ EF <40%
2. อาการ acute (dyspnea, orthopnea, edema)
3. Documentation ว่าเป็น acute event (ไม่ใช่ chronic)
ถ้ามีแค่ EF ต่ำแต่ไม่มีอาการ acute → ใช้ I50.22 (Chronic systolic HF) แทน
```

### Q: AI วิเคราะห์ deny ไม่ตรง ทำยังไง?

**A:** ให้ข้อมูลเพิ่ม:
```
AI วิเคราะห์ว่า HC09 เป็น stent issue แต่จริงๆ ปัญหาคือ
contrast media ที่ใช้ไม่อยู่ใน fee schedule ช่วยวิเคราะห์ใหม่
โดยเน้นที่ contrast media
```

### Q: เคสไม่ใช่ Cath Lab ใช้ได้ไหม?

**A:** ได้ แต่บอก AI ว่าเป็นแผนกอะไร:
```
ตรวจ claim แผนก OR (ไม่ใช่ Cath Lab):
PDx: M17.1 (OA knee)
Proc: 81.54 (Total knee replacement)
...
```

### Q: Drug Catalogue ของ รพ. ยังไม่ได้ export มา

**A:** AI จะเตือนว่า:
```
⚠️ ไม่สามารถตรวจ TMT code ได้ละเอียด
เนื่องจากยังไม่มี Drug Catalogue ของ รพ.
→ แนะนำ: ตรวจ TMT ด้วยมือที่ drug.nhso.go.th/DrugCode/
→ หรือ export Drug Catalogue มาให้ AI ตรวจอัตโนมัติ
```

### Q: REP file เป็น format แปลก อ่านไม่ออก

**A:** Copy ข้อมูลเฉพาะที่ต้องการมาให้ AI:
```
ข้อมูลจาก REP file (copy มา):
690300013,1,761883134,69-09349,69-03556,...,DENY,HC09,IP01,...
```
AI จะ parse ให้ได้

---

## สรุป: Quick Reference Card

```
┌─────────────────────────────────────────┐
│     CATH LAB AI CLAIM — QUICK GUIDE    │
├─────────────────────────────────────────┤
│                                         │
│ 📋 CODING (หลัง D/C):                  │
│    ให้ AI: clinical data               │
│    ได้: ICD-10 + CC/MCC + DRG + เงิน   │
│                                         │
│ 🔍 CHECK (ก่อนส่ง):                     │
│    ให้ AI: claim data ครบ              │
│    ได้: score + warnings + approval    │
│                                         │
│ 🔬 DENY (หลังถูก deny):                │
│    ให้ AI: deny codes + REP data       │
│    ได้: root cause + fix steps         │
│                                         │
│ 📝 APPEAL (ต้องอุทธรณ์):               │
│    ให้ AI: deny info + clinical        │
│    ได้: หนังสือพร้อมส่ง                 │
│                                         │
│ ⚠️ จำไว้:                              │
│ • AI แนะนำ คนตรวจทาน                   │
│ • ทุก code ต้องมี documentation         │
│ • ไม่ upcode — code ตรง clinical       │
│ • ไม่แน่ใจ = ถาม AI เพิ่ม             │
└─────────────────────────────────────────┘
```
