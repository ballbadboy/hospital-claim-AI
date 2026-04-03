# Cath Lab Claim Validation Rules

## 8 Checkpoints ตรวจทุกเคส

### Checkpoint 1: Diagnosis-Procedure Match
**ตรวจว่า PDx ตรงกับ Procedure ที่ทำ**

| Diagnosis | ต้องมี Procedure | ถ้าไม่มีจะเกิดอะไร |
|-----------|-----------------|-------------------|
| I21.0-I21.3 (STEMI) + PCI | 36.06/36.07 + 88.56 + 37.22 | DRG จะไม่ group เป็น Acute MI w/ PCI |
| I21.4 (NSTEMI) + PCI | 36.06/36.07 + 88.56 + 37.22 | เช่นเดียวกัน |
| I20.0 (UA) + Diagnostic cath only | 88.56 + 37.22 | จะได้ DRG กลุ่ม Circ dx w/ cath (RW ต่ำกว่า) |
| I20.0 (UA) + PCI | 36.06/36.07 | จะได้ DRG กลุ่ม PTCA wo sig CCC (RW ต่ำกว่า AMI+PCI) |
| I25.1 (Chronic IHD) + diagnostic cath | 88.56 + 37.22 | Circ dx except AMI w/ cath |

**Red flags:**
- STEMI/NSTEMI diagnosis แต่ไม่มี procedure code เลย → สงสัย coding error
- PCI procedure (36.06/36.07) แต่ diagnosis เป็น I25.x (chronic) → ถามว่ามี acute event จริงไหม
- Unstable angina (I20.0) แต่มี Troponin elevated → ควร code เป็น NSTEMI (I21.4) แทน เพื่อ DRG weight สูงกว่า

### Checkpoint 2: Clinical Documentation
**ตรวจว่าเอกสารทางคลินิกครบ**

| Diagnosis | เอกสารที่ต้องมี | ระดับความสำคัญ |
|-----------|----------------|---------------|
| STEMI (I21.0-I21.3) | Troponin ✓ EKG ✓ D2B time ✓ Cath report ✓ | CRITICAL - ขาดอย่างใดอย่างหนึ่งอาจ deny |
| NSTEMI (I21.4) | Troponin trend (rise/fall) ✓ EKG ✓ Risk score ✓ Cath report ✓ | CRITICAL |
| Unstable angina (I20.0) | Symptoms documented ✓ EKG ✓ Troponin NORMAL ✓ | IMPORTANT - ถ้า troponin elevated ต้อง recode เป็น NSTEMI |
| Diagnostic cath only | Clinical indication ✓ Cath report ✓ Findings ✓ | CRITICAL |

**Troponin rules:**
- STEMI/NSTEMI: ต้อง document ค่าที่สูงกว่า 99th percentile URL
- Rise/fall pattern สำหรับ NSTEMI: ค่า 2 ครั้งห่างกัน 3-6 ชม.
- ถ้าใช้ High-sensitivity Troponin (hs-TnI/hs-TnT): ระบุ assay ที่ใช้ + cut-off value ของ lab

### Checkpoint 3: Device Documentation (Stent)
**ตรวจข้อมูลอุปกรณ์**

ต้องครบทุกข้อ:
- [ ] Stent type: BMS หรือ DES (Drug-Eluting Stent)
- [ ] Manufacturer + brand name
- [ ] Size (diameter x length mm)
- [ ] Lot number / Serial number
- [ ] จำนวนที่ใช้ = จำนวนที่เบิก
- [ ] ตรงกับ GPO VMI/SMI procurement record
- [ ] Code ใน ADP file (TYPE=3-5) ตรงกับชนิดจริง
- [ ] **[ปีงบ69 ใหม่]** ส่ง Sticker/QR Code/Barcode/Serial ผ่าน Standard API (บังคับตั้งแต่ 1 เม.ย. 2569)
- [ ] **[ปีงบ69 ใหม่]** จำนวนอุปกรณ์ไม่เกินเพดานต่อครั้ง (ดูตาราง INST Limit ด้านล่าง)

**Common errors:**
- ใช้ DES แต่ code เป็น BMS → ค่า reimbursement ต่ำกว่าที่ควร
- จำนวน stent ไม่ตรง procedure note → deny ค่าอุปกรณ์
- Lot number ไม่ตรง GPO record → deny
- **[ปีงบ69 ใหม่]** จำนวนอุปกรณ์เกินเพดาน → deny ส่วนที่เกิน
- **[ปีงบ69 ใหม่]** ไม่ส่ง Serial/Barcode ผ่าน API → HC09 deny

#### ตาราง INST Limit — เพดานอุปกรณ์ต่อครั้งต่อหัตถการ (ร่างประกาศ สปสช. ปีงบ 69)

| รหัส | อุปกรณ์ | จำนวน/ครั้ง |
|------|---------|------------|
| 4301 | Coronary Guiding Catheter | 2 ชุด |
| 4302 | PTCA Guide Wire | 3 ชุด |
| 4303 | PTCA Balloon | 5 ชุด |
| 4304 | Coronary Stent (BMS) | 3 ชุด |
| 4305A | DES อัลลอยด์ | 3 ชุด |
| 4305B | DES สแตนเลส | 1 ชุด |
| 4305C | DES อัลลอยด์ พอลิเมอร์ย่อยสลาย | 3 ชุด |
| 4305D | DES ไม่มีพอลิเมอร์ | 1 ชุด |
| 4306 | Coronary Stent Graft | 2 ชุด |
| 4307 | Rotational Atherectomy Burr | 2 ชุด |
| 4308 | Rota Burr Advancer | 1 ชุด |
| 4309 | Cutting/Scoring Balloon | 2 ชุด |
| 4310 | Thrombectomy Catheter | 1 ชุด |
| 4313 | IVUS Catheter | 1 ชุด |
| 4314 | FFR Pressure Wire | 1 ชุด |
| 4319 | CTO PTCA Guide Wire | 3 ชุด |
| 4401 | Diagnostic Catheter | 3 ชุด |
| 4407 | Diagnostic Angiography Catheter | 3 ชุด |
| 4701 | Introducer Sheath | 3 ชุด |
| 4702 | Vascular Closure Device | 4 ชุด |

> อ้างอิง: ร่างประกาศ สปสช. เรื่องการแก้ไขหลักเกณฑ์จ่ายค่าอุปกรณ์ ปีงบ 69 (ข้อ 5.2.1)
> ดูรายละเอียดเต็มที่ `references/nhso-rules/inst-payment-reform-fy69.md`

#### ICD-9-CM 17.55 — Transluminal Coronary Atherectomy (รหัสใหม่ DRG v6)

**ข้อกำหนดสำคัญจาก สปสช. (แจ้ง มี.ค. 2569):**
- **Device 4310 (Thrombectomy Catheter) ต้องมีรหัส 17.55** ถึงจะเบิกได้
- **ข้อมูลที่ส่งก่อน 17/3/2569 ต้องส่งใหม่** — ติดการเบิก Thrombuster
- ใช้กับ DRG v6 เป็นต้นไป

**ICD-9-CM 17.55 ครอบคลุม:**
- Rotational atherectomy [ROTA, RA]
- Cutting balloon angioplasty [CBA]
- Laser coronary angioplasty [LCA]
- Excimer laser angioplasty [ELCA]
- Directional coronary atherectomy [DCA]
- Rheolytic thrombectomy

**Code also any:**
- injection or infusion of thrombolytic agent (99.10)
- insertion of coronary artery stent (36.06-36.07)
- intracoronary artery thrombolytic infusion (36.04)
- number of vascular stents inserted (00.45-00.48)
- number of vessels treated (00.40-00.43)
- procedure on vessel bifurcation (00.44)
- Super Saturated oxygen therapy (00.49)
- transluminal coronary angioplasty (00.66)

**Device-Procedure Matching (ต้อง match ถึงจะเบิกได้):**

| รหัสอุปกรณ์ | ชื่อ | ราคา(บาท) | ต้องมี ICD-9-CM | หมายเหตุ |
|-------------|------|-----------|----------------|---------|
| 4306 | Coronary Stent Graft | 75,000 | 36.06-36.07 | — |
| 4307 | Rotational Atherectomy Burr | 28,000 | **17.55** | — |
| 4308 | Rota Burr Advancer | 29,000 | **17.55** | ใช้คู่กับ 4307 + 00.66 PTCA |
| 4309 | Cutting/Scoring Balloon | 22,000 | **17.55** | Renal artery ก็ใช้ได้ |
| 4310 | **Thrombectomy Catheter** | **12,000** | **17.55** | **ถ้าไม่มี 17.55 → deny** |
| 4320 | Rotablator Guide Wire | 9,000 | **17.55** | ใช้คู่กับ 4307+4308 |
| 4321 | CTO PTCA Balloon | 8,000 | 00.66 | เส้นผ่าศูนย์กลาง ≤1.25mm |

> **CRITICAL:** ถ้าใช้ device 4307/4308/4309/4310/4320 แล้วไม่ code 17.55 → **ถูก deny แน่นอน**
> สปสช. ตรวจ auto matching ระหว่าง ADP file กับ OPR file

### Checkpoint 4: 16-File Completeness (FDH)
**ตรวจว่าข้อมูล 16 แฟ้มครบ**

แฟ้มที่มักมีปัญหากับ Cath Lab:
- **IPD file**: admission date, discharge date, LOS ถูกต้อง, discharge type = 1 (Approval)
- **DIA file**: PDx + SDx codes ถูกต้องตาม ICD-10-TM, ลำดับถูก (PDx = เหตุผลหลักที่ admit)
- **OPR file**: procedure codes ครบทุกตัว, extension codes ถูกต้อง
- **ADP file**: device codes (TYPE=3-5), CODE ตรงกับ สปสช. กำหนด
- **DRU file**: drug codes ตรงกับ FDH Drug Catalog
- **CHA file**: charge items ครบ
- **INS file**: สิทธิถูกต้อง (UC/SSS/CSMBS)

### Checkpoint 5: Timing & Authorization
**ตรวจว่าส่งทันเวลาและมี authen code**

- [ ] Authen Code: valid และไม่หมดอายุ
- [ ] ส่งภายใน 30 วันหลัง discharge (ถ้าเกิน → ถูกปรับลดอัตราจ่าย)
- [ ] ส่งภายใน 24 ชม. หลัง discharge = fast track (สปสช. จ่ายภายใน 72 ชม.)
- [ ] กรณี refer: มี refer form ครบ, สิทธิ verify ก่อนรับ
- [ ] **[ปีงบ69 ใหม่]** กรณี CCS (Chronic Coronary Syndromes / I25.x): ต้องมี Pre Authorized ก่อนให้บริการทุกราย
- [ ] **[ปีงบ69 ใหม่]** ห้ามแบ่ง Episode ในการนอนต่อเนื่อง ≤270 วัน

### Checkpoint 6: CC/MCC Optimization
**ตรวจว่า comorbidities ได้ code ครบ**

| Comorbidity | ICD-10 Code | CC or MCC | ผลต่อ DRG |
|-------------|-------------|-----------|-----------|
| DM type 2 | E11.x | CC | เพิ่ม RW ระดับกลาง |
| DM with hyperglycemia | E11.65 | CC | เพิ่ม RW |
| CKD Stage 3 | N18.3 | CC | เพิ่ม RW |
| CKD Stage 4 | N18.4 | MCC | เพิ่ม RW สูงสุด |
| Acute systolic HF | I50.21 | MCC | เพิ่ม RW สูงสุด |
| Acute diastolic HF | I50.31 | MCC | เพิ่ม RW สูงสุด |
| Atrial fibrillation | I48.x | CC | เพิ่ม RW |
| COPD acute exacerbation | J44.1 | MCC | เพิ่ม RW สูงสุด |
| Essential hypertension | I10 | Neither | ไม่มีผลต่อ RW |
| Dyslipidemia | E78.5 | Neither | ไม่มีผลต่อ RW |

**Optimization tips:**
- ถ้ามี DM + CKD + HF ที่ documented แต่ไม่ได้ code → เสียโอกาส RW สูงขึ้น
- MCC 1 ตัว = DRG weight สูงสุดในกลุ่มแล้ว (ไม่ต้อง stack หลาย MCC)
- ตรวจ medical record ว่ามี comorbidity ที่ยังไม่ได้ code หรือไม่

### Checkpoint 7: DRG Group Verification
**ตรวจว่า DRG ที่ได้ถูกต้อง**

ดู reference file `references/drg-cardiac.md` สำหรับตาราง DRG mapping เต็ม

Common DRG groups for Cath Lab:
- Acute MI w/ single vessel PTCA wo sig CCC
- Acute MI w/ single vessel PTCA w CC
- Acute MI w/ single vessel PTCA w MCC
- Circulatory disorders except AMI w/ cardiac cath
- PTCA wo CCC (non-acute)

### Checkpoint 8: Drug Catalog & Lab Catalog Match
**ตรวจว่ายาและ lab ตรง catalog FDH**

- ยาที่ใช้บ่อยใน Cath Lab: Heparin, Clopidogrel, Ticagrelor, Prasugrel, GP IIb/IIIa inhibitors
- ยาทุกตัวต้อง match กับ FDH Drug Catalog (GPUID)
- Lab ที่ต้อง match: Troponin, CBC, BUN, Cr, electrolytes, PT/INR
- ถ้า Drug/Lab code ไม่ match → ติด C-code error

## DRG Quick Reference: Cath Lab Cases

| Scenario | Expected DRG Group | Approx RW Range |
|----------|-------------------|-----------------|
| STEMI + primary PCI (1 vessel DES) | Acute MI w/ PCI | 2.5-4.0 |
| STEMI + primary PCI + MCC | Acute MI w/ PCI + MCC | 3.5-5.0+ |
| NSTEMI + PCI | Acute MI w/ PCI | 2.0-3.5 |
| UA + diagnostic cath only | Circ dx w/ cath | 1.0-2.0 |
| UA + PCI | PTCA wo CCC | 1.5-2.5 |
| Chronic IHD + elective cath | Circ dx except AMI w/ cath | 0.8-1.5 |
| Chronic IHD + elective PCI | PTCA wo CCC | 1.5-2.5 |

*RW ranges are approximate for Thai DRG v6.3 — verify with actual RW table*
