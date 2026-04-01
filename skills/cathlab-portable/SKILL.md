---
name: cathlab-claim-ai
description: "AI ตรวจเคส Cath Lab ครบวงจร: ตรวจ 8 checkpoints ก่อนส่งเบิก สปสช., คำนวณ DRG/RW, วิเคราะห์ Deny, Auto-code ICD จาก clinical notes, ร่างหนังสืออุทธรณ์ — Portable Edition สำหรับ รพ.พญาไทศรีราชา (11855) ใช้ skill นี้เมื่อพูดถึง: Cath Lab, PCI, stent, สวนหัวใจ, AMI, STEMI, NSTEMI, DRG, e-claim, FDH, กองทุน สปสช., deny, อุทธรณ์, appeal, ICD-10, ICD-9, clinical coding, cardiac catheterization"
---

# Cath Lab Claim AI -- Portable Edition

ตรวจสอบเคสห้องสวนหัวใจ (Cardiac Catheterization Lab) ครบวงจร:
ตรวจ claim, วิเคราะห์ deny, auto-code ICD, ร่างอุทธรณ์ -- ทั้งหมดในไฟล์เดียว

---

## วิธีใช้ (4 Tasks)

### Task 1: ตรวจเคสก่อนส่งเบิก (Claim Check)
บอกข้อมูลเคส (Diagnosis, Procedure, อุปกรณ์, เอกสาร) แล้ว AI จะตรวจ 8 Checkpoints
ตัวอย่าง: "ตรวจเคส STEMI anterior wall ทำ PCI ใส่ DES 1 ตัว"

### Task 2: วิเคราะห์ Deny (Deny Analysis)
บอก deny code/reason แล้ว AI จะหาสาเหตุราก + วิธีแก้ + ประเมินโอกาส appeal สำเร็จ
ตัวอย่าง: "เคสนี้ถูก deny เพราะ C-438 สิทธิประโยชน์ไม่ตรง"

### Task 3: Auto-Code ICD (Smart Coder)
ป้อน clinical notes ภาษาไทย/อังกฤษ แล้ว AI จะแปลงเป็น ICD-10-TM + ICD-9-CM + CC/MCC optimization
ตัวอย่าง: "code ให้หน่อย: ชาย 65 ปี chest pain 2 ชม. EKG ST elevation V1-V4 troponin 5.2 ทำ PCI LAD ใส่ DES"

### Task 4: ร่างหนังสืออุทธรณ์ (Appeal Draft)
ให้ข้อมูลเคส + เหตุผล deny แล้ว AI จะร่างหนังสืออุทธรณ์ภาษาราชการไทยพร้อมส่ง สปสช.
ตัวอย่าง: "ร่างอุทธรณ์เคส HN 12345 ที่ถูก deny เพราะ DRG mismatch"

---

## Hospital Info

| Item | Detail |
|------|--------|
| ชื่อ รพ. | โรงพยาบาลพญาไทศรีราชา |
| HOSPCODE | 11855 |
| เขต สปสช. | เขต 6 (ระยอง) |
| HIS System | SSB HIS |
| IP Base Rate (ในเขต) | **8,350 บาท/AdjRW** |
| IP Base Rate (นอกเขต) | **9,600 บาท/AdjRW** |
| ปีงบประมาณ | 2569 (FY69) |
| DRG Version | Thai DRG v6.3.3 |

**Payment Formula:**
```
DRG Payment = AdjRW x Base Rate
ในเขต:  AdjRW x 8,350 บาท
นอกเขต: AdjRW x 9,600 บาท
```

---

## Checkpoint 1: Diagnosis-Procedure Match

**ตรวจว่า PDx ตรงกับ Procedure ที่ทำ**

| Diagnosis | ต้องมี Procedure | ถ้าไม่มีจะเกิดอะไร |
|-----------|-----------------|-------------------|
| I21.0-I21.3 (STEMI) + PCI | 36.06/36.07 + 88.56 + 37.22 | DRG จะไม่ group เป็น Acute MI w/ PCI |
| I21.4 (NSTEMI) + PCI | 36.06/36.07 + 88.56 + 37.22 | เช่นเดียวกัน |
| I20.0 (UA) + Diagnostic cath only | 88.56 + 37.22 | จะได้ DRG กลุ่ม Circ dx w/ cath (RW ต่ำกว่า) |
| I20.0 (UA) + PCI | 36.06/36.07 | จะได้ DRG กลุ่ม PTCA wo CCC (RW ต่ำกว่า AMI+PCI) |
| I25.1 (Chronic IHD) + diagnostic cath | 88.56 + 37.22 | Circ dx except AMI w/ cath |

**Red flags:**
- STEMI/NSTEMI diagnosis แต่ไม่มี procedure code เลย -> สงสัย coding error
- PCI procedure (36.06/36.07) แต่ diagnosis เป็น I25.x (chronic) -> ถามว่ามี acute event จริงไหม
- Unstable angina (I20.0) แต่มี Troponin elevated -> ควร code เป็น NSTEMI (I21.4) แทน เพื่อ DRG weight สูงกว่า

---

## Checkpoint 2: Clinical Documentation

**ตรวจว่าเอกสารทาง clinical ครบ**

| Diagnosis | เอกสารที่ต้องมี | ระดับความสำคัญ |
|-----------|----------------|---------------|
| STEMI (I21.0-I21.3) | Troponin + EKG + D2B time + Cath report | CRITICAL - ขาดอย่างใดอย่างหนึ่งอาจ deny |
| NSTEMI (I21.4) | Troponin trend (rise/fall) + EKG + Risk score + Cath report | CRITICAL |
| Unstable angina (I20.0) | Symptoms documented + EKG + Troponin NORMAL | IMPORTANT - ถ้า troponin elevated ต้อง recode เป็น NSTEMI |
| Diagnostic cath only | Clinical indication + Cath report + Findings | CRITICAL |

**Troponin rules:**
- STEMI/NSTEMI: ต้อง document ค่าที่สูงกว่า 99th percentile URL
- Rise/fall pattern สำหรับ NSTEMI: ค่า 2 ครั้งห่างกัน 3-6 ชม.
- ถ้าใช้ High-sensitivity Troponin (hs-TnI/hs-TnT): ระบุ assay ที่ใช้ + cut-off value ของ lab

---

## Checkpoint 3: Device Documentation (Stent)

**ตรวจข้อมูลอุปกรณ์ -- ต้องครบทุกข้อ:**

- [ ] Stent type: BMS หรือ DES (Drug-Eluting Stent)
- [ ] Manufacturer + brand name
- [ ] Size (diameter x length mm)
- [ ] Lot number / Serial number
- [ ] จำนวนที่ใช้ = จำนวนที่เบิก
- [ ] ตรงกับ GPO VMI/SMI procurement record
- [ ] Code ใน ADP file (TYPE=3-5) ตรงกับชนิดจริง

**Common errors:**
- ใช้ DES แต่ code เป็น BMS -> ค่า reimbursement ต่ำกว่าที่ควร
- จำนวน stent ไม่ตรง procedure note -> deny ค่าอุปกรณ์
- Lot number ไม่ตรง GPO record -> deny

---

## Checkpoint 4: 16-File Completeness (FDH)

**ตรวจว่าข้อมูล 16 แฟ้มครบ -- แฟ้มที่มักมีปัญหากับ Cath Lab:**

- **IPD file**: admission date, discharge date, LOS ถูกต้อง, discharge type = 1 (Approval)
- **DIA file**: PDx + SDx codes ถูกต้องตาม ICD-10-TM, ลำดับถูก (PDx = เหตุผลหลักที่ admit)
- **OPR file**: procedure codes ครบทุกตัว, extension codes ถูกต้อง
- **ADP file**: device codes (TYPE=3-5), CODE ตรงกับ สปสช. กำหนด
- **DRU file**: drug codes ตรงกับ FDH Drug Catalog
- **CHA file**: charge items ครบ
- **INS file**: สิทธิถูกต้อง (UC/SSS/CSMBS)

---

## Checkpoint 5: Timing & Authorization

- [ ] Authen Code: valid และไม่หมดอายุ
- [ ] ส่งภายใน 30 วันหลัง discharge (ถ้าเกิน -> ถูกปรับลดอัตราจ่าย)
- [ ] ส่งภายใน 24 ชม. หลัง discharge = fast track (สปสช. จ่ายภายใน 72 ชม.)
- [ ] กรณี refer: มี refer form ครบ, สิทธิ verify ต้องรับ

| ประเภท | กำหนด | ผลถ้าเกิน |
|--------|-------|----------|
| Fast track | <=24 ชม. | สปสช. จ่ายใน 72 ชม. |
| IPD ปกติ | <=30 วัน | จ่ายปกติ |
| OPD ปกติ | <=15 วัน | จ่ายปกติ |
| เกินกำหนด | >30 วัน | ลดอัตราจ่าย / reject |

---

## Checkpoint 6: CC/MCC Optimization

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
| Acute kidney injury | N17.9 | MCC | เพิ่ม RW สูงสุด |
| Essential hypertension | I10 | Neither | ไม่มีผลต่อ RW |
| Dyslipidemia | E78.5 | Neither | ไม่มีผลต่อ RW |

**Optimization tips:**
- ถ้ามี DM + CKD + HF ที่ documented แต่ไม่ได้ code -> เสียโอกาส RW สูงขึ้น
- MCC 1 ตัว = DRG weight สูงสุดในกลุ่มแล้ว (ไม่ต้อง stack หลาย MCC)
- ตรวจ medical record ว่ามี comorbidity ที่ยังไม่ได้ code หรือไม่

---

## Checkpoint 7: DRG Group Verification

**ตรวจว่า DRG ที่ได้ถูกต้อง (ดูตาราง RW เต็มด้านล่าง)**

Common DRG groups for Cath Lab:

| Scenario | Expected DRG Group | Approx RW Range |
|----------|-------------------|-----------------|
| STEMI + primary PCI (1 vessel DES) | Acute MI w/ PCI | 8.65-11.48 |
| STEMI + primary PCI + MCC | Acute MI w/ PCI + MCC | 11.48+ |
| NSTEMI + PCI | Acute MI w/ PCI | 8.65-11.48 |
| UA + diagnostic cath only | Circ dx w/ cath | 2.14-5.39 |
| UA + PCI | PTCA w/ stent | 6.88-9.82 |
| Chronic IHD + elective cath | Circ dx except AMI w/ cath | 2.14-5.39 |
| Chronic IHD + elective PCI | PTCA w/ stent | 6.88-9.82 |
| Acute MI multi-vessel PCI | Acute MI w/ multi PTCA | 10.02-12.16 |

---

## Checkpoint 8: Drug Catalog & Lab Catalog Match

- ยาที่ใช้บ่อยใน Cath Lab: Heparin, Clopidogrel, Ticagrelor, Prasugrel, GP IIb/IIIa inhibitors, Aspirin
- ยาทุกตัวต้อง match กับ FDH Drug Catalog (GPUID)
- Lab ที่ต้อง match: Troponin, CBC, BUN, Cr, electrolytes, PT/INR
- ถ้า Drug/Lab code ไม่ match -> ติด C-code error

---

## ICD-10-TM Cardiac Diagnosis Codes

### Unstable Angina & Angina Pectoris (I20)

| Code | Description TH | Description EN |
|------|---------------|---------------|
| I20.0 | กล้ามเนื้อหัวใจขาดเลือดเฉียบพลันชนิดไม่คงที่ | Unstable angina |
| I20.1 | Angina pectoris with documented spasm | Prinzmetal angina |
| I20.8 | Other forms of angina pectoris | |
| I20.9 | Angina pectoris, unspecified | |

### Acute Myocardial Infarction (I21)

| Code | Description | Type | Note |
|------|-------------|------|------|
| I21.0 | Acute transmural MI of anterior wall | STEMI | LAD territory |
| I21.1 | Acute transmural MI of inferior wall | STEMI | RCA territory |
| I21.2 | Acute transmural MI of other sites | STEMI | LCx, posterior |
| I21.3 | Acute transmural MI of unspecified site | STEMI | ใช้เมื่อระบุ territory ไม่ได้ |
| I21.4 | Acute subendocardial MI | NSTEMI | Troponin elevated + symptoms |
| I21.9 | Acute MI, unspecified | Unspecified | หลีกเลี่ยง -- ควรระบุให้ specific |

### Subsequent MI (I22)

| Code | Description | Note |
|------|-------------|------|
| I22.0 | Subsequent MI of anterior wall | ภายใน 28 วันจาก MI ครั้งแรก |
| I22.1 | Subsequent MI of inferior wall | |
| I22.8 | Subsequent MI of other sites | |
| I22.9 | Subsequent MI of unspecified site | |

### Other Acute IHD (I24)

| Code | Description |
|------|-------------|
| I24.0 | Acute coronary thrombosis not resulting in MI |
| I24.1 | Dressler syndrome (post MI syndrome) |
| I24.8 | Other forms of acute IHD |
| I24.9 | Acute IHD, unspecified |

### Chronic Ischemic Heart Disease (I25)

| Code | Description | Note |
|------|-------------|------|
| I25.0 | Atherosclerotic cardiovascular disease | |
| I25.1 | Atherosclerotic heart disease | CAD ทั่วไป |
| I25.10 | Chronic IHD without angina | |
| I25.11 | Chronic IHD with angina | |
| I25.2 | Old myocardial infarction | MI เก่า >28 วัน |
| I25.5 | Ischemic cardiomyopathy | |
| I25.6 | Silent myocardial ischemia | |

---

## ICD-9-CM Procedure Codes for Cardiac Cath/PCI

### Diagnostic Cardiac Catheterization

| Code | Description | Type |
|------|-------------|------|
| 37.21 | Right heart catheterization | Diagnostic |
| 37.22 | Left heart catheterization | Diagnostic |
| 37.23 | Combined R+L heart catheterization | Diagnostic |

### Coronary Angiography

| Code | Description |
|------|-------------|
| 88.55 | Coronary arteriography NOS |
| 88.56 | Coronary arteriography using 2 catheters (Judkins) |
| 88.57 | Other and unspecified coronary arteriography |

### PCI (Percutaneous Coronary Intervention)

| Code | Description | Type |
|------|-------------|------|
| 36.01 | PTCA single vessel without stent | PCI |
| 36.02 | PTCA single vessel with drug-eluting stent | PCI+DES |
| 36.05 | PTCA multiple vessels | Multi-vessel PCI |
| 36.06 | Insertion of non-drug-eluting coronary stent | BMS |
| 36.07 | Insertion of drug-eluting coronary stent | DES |
| 36.09 | Other PTCA | |

### Other Procedures

| Code | Description |
|------|-------------|
| 36.10-36.19 | CABG (bypass graft) |
| 37.0 | Pericardiocentesis |
| 37.34 | Cardiac ablation |
| 37.61 | IABP implantation |
| 37.68 | IABP removal |
| 39.50 | Angioplasty of non-coronary vessel |
| 99.10 | Injection of thrombolytic agent |
| 99.60 | Cardiopulmonary resuscitation |

### Extension Code Format (Thai)

รูปแบบ: XX.XX + 2 ตำแหน่ง = ตำแหน่ง + จำนวนครั้ง
- ตัวอย่าง: 36.0601 = PTCA 1 vessel, stent 1 ชิ้น, ตำแหน่งที่ 1
- ตัวอย่าง: 36.0702 = DES insertion, 2 stents

### Coding Rules สำคัญ

**Diagnostic Cath + PCI ในวันเดียวกัน:**
- Code ทั้ง diagnostic (37.22 + 88.56) AND therapeutic (36.06/36.07)
- Diagnostic cath ไม่ได้ bundle กับ PCI ใน Thai DRG
- ต้อง document ว่า decision to intervene เกิดหลังจาก diagnostic cath

**Multiple Vessel PCI:**
- ใช้ 36.05 สำหรับ multi-vessel PTCA
- ระบุจำนวน vessel และ stent แต่ละ vessel ใน extension code
- แต่ละ vessel ต้อง document indication แยก

**Staged Procedure (PCI คนละวัน):**
- ถ้า diagnostic cath วันหนึ่ง แล้ว PCI อีกวัน -> 2 admissions แยก
- ห้าม re-bill diagnostic cath ในวันที่ทำ PCI
- ถ้า admit ครั้งเดียว -> code ทั้งหมดในเคสเดียว

---

## Clinical Criteria (STEMI / NSTEMI / UA)

### STEMI Diagnostic Criteria (ต้องครบทุกข้อ)

1. **Symptoms**: Chest pain / ischemic equivalent (dyspnea, diaphoresis)
2. **EKG**: ST elevation >=1mm in 2 contiguous leads (>=2mm in V1-V3 for men)
   - OR new LBBB with clinical suspicion
3. **Troponin**: Elevation above 99th percentile URL (rise and/or fall pattern)
4. **Document**: Time of symptom onset, time of first medical contact, door-to-balloon time

**D2B time target:** <90 minutes for primary PCI (quality indicator -- document เสมอ)

### NSTEMI Diagnostic Criteria

1. **Troponin**: Elevated with rise/fall pattern (ค่า 2 ครั้งห่างกัน 3-6 ชม.)
2. **Symptoms**: Ischemic symptoms (rest angina, new-onset, crescendo)
3. **EKG changes** (อาจไม่มีก็ได้): ST depression, T-wave inversion, transient ST elevation
4. **Risk stratification**: GRACE score or TIMI score documented

**แยก NSTEMI จาก UA:** Troponin elevated = NSTEMI, Troponin normal = UA
ถ้า Troponin elevated ต้อง code I21.4 (NSTEMI) ไม่ใช่ I20.0 (UA)

### Unstable Angina Criteria

1. **Angina at rest** (usually >20 min) OR
2. **New-onset severe angina** (CCS class III) within past 2 months OR
3. **Crescendo angina** (increasing frequency/severity/duration)
4. **Troponin**: NORMAL (ถ้า elevated -> recode เป็น NSTEMI)
5. **EKG**: อาจ normal หรือมี ST-T changes

### Indications for Cardiac Catheterization (ต้อง document)

- ACS (STEMI/NSTEMI/UA) with high-risk features
- Positive stress test
- Recurrent chest pain despite medical therapy
- Heart failure with suspected ischemic etiology
- Pre-operative evaluation (selected cases)
- Post-cardiac arrest with suspected cardiac cause

### Indications for PCI (ต้อง document)

- **Stenosis >=70%** in target vessel (>=50% for left main)
- Correlation with symptoms or functional ischemia
- FFR <0.80 if stenosis 50-70% (borderline)
- Not purely prophylactic in stable asymptomatic patients

### GRACE Score Components

| Variable | Points |
|----------|--------|
| Age | 0-100 |
| Heart rate | 0-46 |
| Systolic BP | 0-58 |
| Creatinine | 0-28 |
| Killip class | 0-64 |
| Cardiac arrest at admission | 0/39 |
| ST deviation | 0/28 |
| Elevated cardiac enzymes | 0/14 |

GRACE >140 = high risk -> early invasive strategy recommended

### TIMI Risk Score (NSTEMI/UA)

| Factor | Points |
|--------|--------|
| Age >=65 | 1 |
| >=3 CAD risk factors | 1 |
| Known CAD (stenosis >=50%) | 1 |
| ASA use in past 7 days | 1 |
| Severe angina (>=2 episodes in 24h) | 1 |
| ST deviation >=0.5mm | 1 |
| Elevated cardiac markers | 1 |

TIMI >=5 = high risk -> early invasive strategy

---

## DRG RW Table -- Thai DRG v6.3.3 (MDC 05 Cardiac)

> Source: Thai DRG and Relative Weight Version 6.3.3, Appendix G
> Published: December 2020 by สำนักพัฒนากลุ่มโรคร่วมไทย (สรท./TCMC)
> Payment Formula: **DRG Payment = AdjRW x Base Rate**
> Base Rate ปีงบ 69: ในเขต **8,350** / นอกเขต **9,600** บาท/AdjRW

### Column Definitions

| Column | Meaning |
|--------|---------|
| DRG | DRG code (5 digits: DDDDX where X=complexity level 0-4,9) |
| RW | Relative Weight (ค่าน้ำหนักสัมพัทธ์) |
| WtLOS | Weighted average Length of Stay (วันนอนเฉลี่ย) |
| OT | Outlier Trim point (จุดตัดวันนอนเกิน) |
| RW0d | RW สำหรับกรณีนอน <=24 ชม. (<=1,440 นาที) |

### PCL Formula (Patient Complexity Level)

```
PCL = sum(Li x r^(i-1))  where r = 0.82
```
- Li = DCL ค่าที่ i (เรียงจากมากไปน้อย)
- PCL 0-9 (ปัดเศษ: <0.5 ปัดทิ้ง, >=0.5 ปัดขึ้น, >9 เป็น 9)

### AdjRW Formula (ปรับค่า RW ตามวันนอน)

- LOS <= OT -> AdjRW = RW (ไม่ปรับ)
- LOS > OT -> AdjRW = RW + per diem (ดู Appendix H)
- LOS <= 24 ชม. -> ใช้ RW0d

---

### Cardiac Surgery & Transplant (Pre-MDC / MDC 05 Surgical)

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05019 | 18.3432 | 24.17 | 73 | 8.0710 | Valve replacement and open valvuloplasty w cath |
| 05020 | 13.2288 | 12.87 | 39 | 8.9956 | Valve replacement and open valvuloplasty wo sig CCC |
| 05021 | 15.9402 | 19.07 | 57 | 8.9956 | Valve replacement and open valvuloplasty w min CCC |
| 05022 | 19.3869 | 24.40 | 73 | 8.9956 | Valve replacement and open valvuloplasty w mod CCC |
| 05039 | 29.3120 | 21.98 | 66 | 12.8973 | Coronary bypass with PTCA |
| 05049 | 23.1477 | 24.44 | 73 | 10.1850 | Coronary bypass with cath |
| 05059 | 18.1845 | 13.75 | 41 | 12.3655 | Coronary bypass |

### PCI -- Acute MI with PCI

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| **05259** | **32.5414** | **22.89** | **69** | **14.3182** | **Acute MI w CAB or VSD repair w PTCA** |
| **05269** | **22.2634** | **21.59** | **65** | **9.7959** | **Acute MI w CAB or VSD repair wo PTCA** |
| **05270** | **10.0192** | **4.31** | **13** | **9.1175** | **Acute MI w multiple vessel PTCA wo sig CCC** |
| **05271** | **12.1597** | **8.90** | **27** | **10.2141** | **Acute MI w multiple vessel PTCA w min CCC** |
| **05290** | **8.6544** | **3.57** | **11** | **7.8755** | **Acute MI w single vessel PTCA wo sig CCC** |
| **05291** | **11.4820** | **6.54** | **20** | **9.6449** | **Acute MI w single vessel PTCA w min CCC** |

### PCI -- Cardiac Cath/Angiography

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05210 | 2.7603 | 3.87 | 12 | 2.5119 | Cardiac cath/angiography for complex Dx wo sig CCC |
| 05211 | 5.5237 | 8.85 | 27 | 4.6399 | Cardiac cath/angiography for complex Dx w min CCC |
| 05212 | 9.1898 | 13.12 | 39 | 6.2491 | Cardiac cath/angiography for complex Dx w mod CCC |
| 05220 | 2.1360 | 2.16 | 6 | 2.1360 | Cardiac cath/angiography wo sig CCC |
| 05221 | 3.0615 | 3.73 | 11 | 2.7860 | Cardiac cath/angiography w min CCC |
| 05222 | 5.3864 | 10.58 | 32 | 4.0937 | Cardiac cath/angiography w mod CCC |

### PCI -- Percutaneous Cardiovascular Procedures (Non-Acute)

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05230 | 6.8786 | 2.14 | 6 | 6.8786 | Percut cardiovas proc w stent insertion wo sig CCC |
| 05231 | 8.0392 | 2.56 | 8 | 8.0392 | Percut cardiovas proc w stent insertion w min CCC |
| 05232 | 9.8158 | 5.19 | 16 | 8.9324 | Percut cardiovas proc w stent insertion w mod CCC |
| 05240 | 6.5804 | 2.18 | 7 | 6.5804 | Percut cardiovas proc wo sig CCC |
| 05241 | 7.7565 | 2.76 | 8 | 7.7565 | Percut cardiovas proc w min CCC |
| 05242 | 9.2851 | 5.75 | 17 | 8.4494 | Percut cardiovas proc w mod CCC |

### Other Cardiac Procedures

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05060 | 9.7878 | 5.53 | 17 | 8.9069 | Other cardiothoracic proc wo sig CCC |
| 05061 | 12.2013 | 13.69 | 41 | 9.0047 | Other cardiothoracic proc w min CCC |
| 05079 | 22.4312 | 17.70 | 53 | 13.4588 | Thoracoabdominal proc combination |
| 05080 | 8.4539 | 7.10 | 21 | 7.1013 | Major cardiovascular proc wo sig CCC |
| 05081 | 12.0728 | 15.46 | 46 | 7.2436 | Major cardiovascular proc w min CCC |
| 05090 | 4.5621 | 14.57 | 44 | 3.1022 | Major amputation for CVS disorders wo sig CCC |
| 05091 | 8.0812 | 23.82 | 71 | 3.5557 | Major amputation for CVS disorders w min CCC |
| 05109 | 9.5307 | 12.57 | 38 | 6.4809 | Perm pacemaker proc comb for AMI, HF, Shock |
| 05110 | 3.2787 | 4.50 | 14 | 2.9836 | Perm pacemaker proc comb wo sig CCC |
| 05111 | 4.8684 | 6.98 | 21 | 4.0895 | Perm pacemaker proc comb w min CCC |
| 05112 | 7.6522 | 13.53 | 41 | 5.2035 | Perm pacemaker proc comb w mod CCC |
| 05120 | 4.9904 | 3.94 | 12 | 4.5413 | Automat cardioverter proc wo sig CCC |
| 05121 | 7.3820 | 7.09 | 21 | 6.2008 | Automat cardioverter proc w min CCC |
| 05122 | 9.9119 | 15.57 | 47 | 6.2008 | Automat cardioverter proc w mod CCC |
| 05130 | 8.7454 | 9.00 | 27 | 7.3461 | Simple cardiothoracic proc wo sig CCC |
| 05131 | 11.8708 | 12.03 | 36 | 8.0722 | Simple cardiothoracic proc w min CCC |
| 05149 | 5.7297 | 3.22 | 10 | 5.2140 | Cardiac electrophysiologic proc |
| 05150 | 3.3140 | 3.56 | 11 | 3.0157 | Other vascular proc wo sig CCC |
| 05151 | 6.0702 | 8.57 | 26 | 5.0990 | Other vascular proc w min CCC |
| 05152 | 8.9979 | 18.51 | 56 | 5.0990 | Other vascular proc w mod CCC |

### Peripheral Stent / Amputation

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05310 | 3.9910 | 2.42 | 7 | 3.9910 | Peripheral stent insertion wo sig CCC |
| 05311 | 7.5004 | 10.10 | 30 | 5.7003 | Peripheral stent insertion w min CCC |
| 05160 | 1.6835 | 6.64 | 20 | 1.4141 | Minor amputation wo sig CCC |
| 05161 | 4.0676 | 12.92 | 39 | 2.7659 | Minor amputation w min CCC |

### Medical Cardiac DRGs (No OR Procedure)

#### Acute MI (Medical Management)

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05500 | 2.4222 | 3.56 | 11 | 2.2042 | Acute MI w major comp w thrombol inj wo sig CCC |
| 05501 | 6.0220 | 10.06 | 30 | 4.5767 | Acute MI w major comp w thrombol inj w min CCC |
| 05510 | 2.1349 | 3.59 | 11 | 1.9428 | Acute MI w thrombol inj wo sig CCC |
| 05511 | 2.6876 | 5.20 | 16 | 2.4457 | Acute MI w thrombol inj w min CCC |
| 05520 | 1.5851 | 4.86 | 15 | 1.4424 | Acute MI w major comp, not transferred wo sig CCC |
| 05521 | 2.9432 | 7.45 | 22 | 2.4723 | Acute MI w major comp, not transferred w min CCC |
| 05522 | 4.0802 | 9.40 | 28 | 3.1009 | Acute MI w major comp, not transferred w mod CCC |
| 05523 | 6.7633 | 13.91 | 42 | 4.5990 | Acute MI w major comp, not transferred w maj CCC |
| 05530 | 1.0396 | 4.00 | 12 | 0.9460 | Acute MI, not transferred wo sig CCC |
| 05531 | 1.3637 | 4.94 | 15 | 1.2410 | Acute MI, not transferred w min CCC |
| 05532 | 2.0671 | 6.88 | 21 | 1.7363 | Acute MI, not transferred w mod CCC |
| 05533 | 3.2701 | 9.33 | 28 | 2.4853 | Acute MI, not transferred w maj CCC |

#### Heart Failure

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05550 | 0.6831 | 3.36 | 10 | 0.6216 | Heart failure and shock wo sig CCC |
| 05551 | 1.3294 | 5.24 | 16 | 1.2098 | Heart failure and shock w min CCC |
| 05552 | 2.9495 | 8.57 | 26 | 2.4776 | Heart failure and shock w mod CCC |
| 05553 | 5.5413 | 12.72 | 38 | 3.7681 | Heart failure and shock w maj CCC |
| 05554 | 7.3352 | 18.81 | 56 | 3.8143 | Heart failure and shock w ext CCC |

#### Coronary Atherosclerosis & Unstable Angina

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05590 | 0.5561 | 2.31 | 7 | 0.5561 | Coronary atherosclerosis and unstable angina wo sig CCC |
| 05591 | 0.8915 | 3.55 | 11 | 0.8113 | Coronary atherosclerosis and unstable angina w min CCC |
| 05592 | 1.6921 | 5.75 | 17 | 1.5398 | Coronary atherosclerosis and unstable angina w mod CCC |
| 05593 | 2.9651 | 8.20 | 25 | 2.4907 | Coronary atherosclerosis and unstable angina w maj CCC |
| 05594 | 6.3327 | 12.71 | 38 | 4.3062 | Coronary atherosclerosis and unstable angina w ext CCC |

#### Arrhythmia

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05630 | 0.8116 | 2.13 | 6 | 0.8116 | Major arrhythmia and cardiac arrest wo sig CCC |
| 05631 | 1.9084 | 3.87 | 12 | 1.7366 | Major arrhythmia and cardiac arrest w min CCC |
| 05632 | 3.6236 | 6.68 | 20 | 3.0438 | Major arrhythmia and cardiac arrest w mod CCC |
| 05633 | 7.4736 | 12.38 | 37 | 5.0820 | Major arrhythmia and cardiac arrest w maj CCC |

#### Hypertension

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05600 | 0.3341 | 1.91 | 6 | 0.3341 | Hypertension wo sig CCC |
| 05601 | 0.8421 | 3.45 | 10 | 0.7663 | Hypertension w min CCC |
| 05602 | 2.0261 | 6.29 | 19 | 1.7019 | Hypertension w mod CCC |
| 05603 | 3.7381 | 9.10 | 27 | 2.8409 | Hypertension w maj CCC |

#### Chest Pain, Syncope

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05660 | 0.3602 | 1.63 | 5 | 0.3602 | Chest pain, syncope and collapse wo sig CCC |
| 05661 | 0.6192 | 2.48 | 7 | 0.6192 | Chest pain, syncope and collapse w min CCC |
| 05662 | 1.2428 | 4.29 | 13 | 1.1309 | Chest pain, syncope and collapse w mod CCC |
| 05663 | 1.9439 | 5.93 | 18 | 1.7689 | Chest pain, syncope and collapse w maj CCC |

#### Acute MI, Transferred

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05690 | 0.6719 | 1.81 | 5 | 0.6719 | Acute MI, transferred wo sig CCC |
| 05691 | 1.6614 | 3.90 | 12 | 1.5119 | Acute MI, transferred w min CCC |
| 05692 | 3.0483 | 6.32 | 19 | 2.5606 | Acute MI, transferred w mod CCC |
| 05693 | 5.3159 | 10.78 | 32 | 4.0401 | Acute MI, transferred w maj CCC |

---

## Payment Calculation Examples (Base Rate 8,350)

### Example 1: STEMI + Primary PCI (Single vessel)
- DRG 05290 (Acute MI w single vessel PTCA wo sig CCC)
- RW = 8.6544, AdjRW = 8.65
- **Payment = 8.65 x 8,350 = 72,228 บาท**

### Example 2: STEMI + PCI + CC/MCC (HF + CKD4)
- DRG 05291 (Acute MI w single vessel PTCA w min CCC)
- RW = 11.4820, AdjRW = 11.48
- **Payment = 11.48 x 8,350 = 95,858 บาท**
- Difference from wo CCC: **+23,630 บาท** (ผลจาก CC/MCC)

### Example 3: Diagnostic Cath only (Chronic IHD)
- DRG 05220 (Cardiac cath/angiography wo sig CCC)
- RW = 2.1360, AdjRW = 2.14
- **Payment = 2.14 x 8,350 = 17,869 บาท**

### Example 4: Elective PCI with stent (non-acute)
- DRG 05230 (Percut cardiovas proc w stent insertion wo sig CCC)
- RW = 6.8786, AdjRW = 6.88
- **Payment = 6.88 x 8,350 = 57,448 บาท**

### Example 5: Acute MI medical (no PCI, not transferred)
- DRG 05530 (Acute MI, not transferred wo sig CCC)
- RW = 1.0396
- **Payment = 1.04 x 8,350 = 8,684 บาท**
- vs PCI DRG 05290 RW 8.65 = 72,228 บาท
- **ผลต่าง: ~63,544 บาท** -- นี่คือสาเหตุที่ Dx-Proc match สำคัญมาก

### Example 6: Acute MI multi-vessel PCI
- DRG 05270 (Acute MI w multiple vessel PTCA wo sig CCC)
- RW = 10.0192
- **Payment = 10.02 x 8,350 = 83,667 บาท**

---

## Key Insights for Claim Optimization

1. **Acute MI + PCI (05290) vs Medical MI (05530):** RW ต่างกัน 8.3x -> ถ้าทำ PCI แต่ไม่ code procedure = เสียเงิน ~63,000 บาท
2. **CC/MCC impact (05290 vs 05291):** เพิ่ม CC/MCC = +23,630 บาท
3. **Cath only (05220) vs PCI (05230):** RW ต่างกัน 3.2x -> ถ้าทำ PCI แต่ code แค่ cath = เสียเงิน ~40,000 บาท
4. **LOS > OT:** ถ้านอนเกิน OT จะได้ per diem เพิ่ม (ดู Appendix H)
5. **LOS <= 24 ชม.:** ใช้ RW0d ซึ่งต่ำกว่า RW ปกติ (~70-90%)
6. **Multi-vessel (05270) vs Single-vessel (05290):** Multi-vessel RW สูงกว่า ~1.36 -> ต้อง code 36.05 ถ้าทำหลาย vessel

---

## DRG Grouping Logic

### Grouping Flow

1. PDx determines MDC (I20-I25 -> MDC 05: Diseases of Circulatory System)
2. Check OR Procedure list -> Surgical or Medical DRG
3. Cardiac cath (37.21-37.23) = Non-OR procedure affecting DRG
4. PCI (36.01-36.09) = OR Procedure -> Surgical DRG
5. Check CC/MCC (PCCL level) -> final DRG assignment

### Surgical DRGs (มี OR Procedure)

| Scenario | DRG Pattern |
|----------|-------------|
| PCI with DES/BMS + Acute MI | Acute MI w/ PCI (สูงสุด) |
| PCI + non-acute diagnosis | PTCA/Percut cardiovas proc (ต่ำกว่า) |
| CABG | Cardiac valve/major cardiothoracic |
| Pacemaker/ICD implant | Perm pacemaker implant |

### Medical DRGs (ไม่มี OR Procedure)

| Scenario | DRG Pattern |
|----------|-------------|
| Acute MI (medical, no PCI) | AMI discharged alive |
| Circ dx with cardiac cath | Circ disorders w/ cath |
| Heart failure | Heart failure and shock |
| Chest pain | Chest pain, syncope |

### CC/MCC Impact on DRG Weight (PCCL)

- PCCL 0: ไม่มี CC -> base RW (suffix 0)
- PCCL 1-2: มี CC -> RW สูงขึ้นเล็กน้อย (suffix 1)
- PCCL 3-4: มี MCC -> RW สูงขึ้นมาก (suffix 2-3)

**DCL (Diagnosis Complexity Level):**
แต่ละ SDx มีค่า DCL ต่างกันในแต่ละ DC
- DCL 0 = ไม่เป็น CC ใน DC นี้
- DCL 1-4 = CC ระดับต่ำ-สูง

**CC Exclusion:** บาง SDx จะถูกตัดออกจาก CC ถ้าเกี่ยวข้องกับ PDx
ตัวอย่าง: I50 (HF) อาจไม่นับเป็น CC ถ้า PDx เป็น I21 (MI) ใน DC บางตัว -> ตรวจ CC Exclusion List เสมอ

### LOS Adjustment

- LOS < Trim Low -> ลด RW (outlier สั้น)
- LOS ปกติ -> RW ตามกลุ่ม
- LOS > Trim High (OT) -> เพิ่ม RW (outlier ยาว -- per diem)

สำหรับ Cath Lab:
- PCI ปกติ: LOS 2-5 วัน
- Acute MI + PCI: LOS 3-7 วัน
- Complicated: LOS 7-14+ วัน

---

## FDH 16-File Structure

### Overview
Financial Data Hub (FDH) รับข้อมูล 16 แฟ้มจาก HIS ของโรงพยาบาล ส่งเข้า สปสช. เพื่อประมวลผล e-Claim

### IPD -- Inpatient Data

| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| AN | Admission number | ต้องไม่ว่าง |
| DATEADM | วันที่ admit | ต้องก่อน D/C date |
| DATEDSC | วันที่ discharge | ใช้คำนวณ LOS |
| DISCHT | Discharge type | 1=Approval, 2=Against advice |
| WARD | Ward code | ต้อง map กับ ward ที่ขึ้นทะเบียน |

### DIA -- Diagnosis

| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| DIAG | ICD-10 code | ต้อง valid ใน ICD-10-TM library |
| DXTYPE | 1=PDx, 2=SDx, 3=External cause | PDx ต้องมี 1 ตัว SDx ได้หลายตัว |
| PROVIDER | รหัสแพทย์ | ต้องมี |

**Critical rules:**
- PDx (DXTYPE=1) ต้องมีเพียง 1 รหัส = เหตุผลหลักที่ admit
- SDx ทุกตัวต้องเป็น comorbidity ที่มีอยู่จริง ไม่ใช่ duplicate
- SDx ที่เป็น CC/MCC ต้อง code ครบเพื่อ optimize DRG weight

### OPR -- Operation/Procedure

| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| ESSION | Episode/session | ตรง AN |
| OPTYPE | OR type | 1=major OR, 2=minor OR, 3=non-OR |
| OPCODE | ICD-9-CM code | ต้อง valid + extension code ถ้ามี |
| DATEOP | วันที่ทำ | ต้องอยู่ระหว่าง admit-discharge |
| PROVIDER | รหัสแพทย์ผ่าตัด | ต้องมี |

**Cath Lab procedure coding:**
- PCI (36.0x) = OPTYPE 1 (major OR) ใน Thai DRG
- Diagnostic cath (37.22) = OPTYPE 3 (non-OR) แต่มีผลต่อ DRG grouping
- ต้อง code ทุก procedure ที่ทำ ไม่ใช่แค่ main procedure

### ADP -- Additional Payment (อุปกรณ์)

| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| TYPE | 3=วัสดุ, 4=ข้อต่อ, 5=อวัยวะเทียม | Stent = TYPE 5 |
| CODE | รหัสอุปกรณ์ สปสช. | ต้องตรงกับ Fee Schedule |
| QTY | จำนวน | ต้องตรง procedure note |
| RATE | ราคาต่อหน่วย | ต้องไม่เกิน ceiling ที่ สปสช. กำหนด |
| TOTAL | ราคารวม | QTY x RATE |
| SERIALNO | Lot/Serial number | ต้องตรง GPO VMI |

**Stent coding ใน ADP:**
- DES (Drug-Eluting Stent): ใช้ CODE ตามที่ สปสช. กำหนดสำหรับ DES
- BMS (Bare Metal Stent): CODE ต่างจาก DES
- Balloon catheter, guidewire: แยก CODE
- IABP: CODE เฉพาะ

### DRU -- Drug

| Field | Description | Check |
|-------|-------------|-------|
| DID | Drug ID (GPUID) | ต้องตรง FDH Drug Catalog |
| AMOUNT | จำนวน | ต้องสมเหตุสมผล |
| TOTAL | ราคารวม | |

### CHA -- Charge

| Field | Description |
|-------|-------------|
| CHRGITEM | Charge item code |
| AMOUNT | จำนวนเงิน |
| DATE | วันที่ |

### Common FDH Submission Errors

**Format Errors:**
- Date format ผิด (ต้องเป็น YYYYMMDD)
- Code มี leading/trailing spaces
- Numeric field มีตัวอักษร
- Required field เป็น null/empty

**Logic Errors:**
- D/C date ก่อน Admit date
- Procedure date นอกช่วง Admit-D/C
- PDx ไม่ valid สำหรับ age/sex ของผู้ป่วย
- SDx duplicate กับ PDx
- ADP quantity > reasonable limit

---

## Deny Codes & Fixes

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
| C-438 | สิทธิประโยชน์ไม่ตรง | ตรวจสิทธิ -> เลือกให้ตรง |
| C30/W305 | ไม่พบการปิดสิทธิ | ตรวจ Authen Code |
| C555 | OP REFER error | ตรวจรหัส refer |
| Drug mismatch | รหัสยาไม่ตรง | Map Hosp Drug Code -> TMT/GPUID |
| Lab mismatch | รหัส Lab ไม่ตรง | Map กับ FDH standard |
| ADP error | รหัสอุปกรณ์ผิด | TYPE 3/4/5, lot number ตรง GPO VMI |

### C-438: สิทธิประโยชน์ไม่ตรง (รายละเอียด)

**สาเหตุ:** เลือกเงื่อนไขสิทธิประโยชน์ไม่ตรงกับสิทธิที่พึงเบิกได้
**วิธีแก้:**
1. ตรวจสอบสิทธิผู้ป่วย (UC/SSS/CSMBS)
2. เลือกสิทธิประโยชน์ในการเบิกชดเชยให้ตรงกับสิทธิ
3. กรณีเบิกชดเชยไม่ตรงกับสิทธิหลัก -> ตรวจสอบรหัสโครงการพิเศษ
4. บันทึกข้อมูลให้ถูกต้องตามเงื่อนไข แล้วส่งใหม่

### Drug Catalog Mismatch

**วิธีแก้:**
1. ดาวน์โหลด Drug Catalog ล่าสุดจาก FDH
2. Map รหัสยาใน HIS กับ GPUID ที่ FDH กำหนด
3. ยาที่ใช้บ่อยใน Cath Lab ต้อง map ก่อน: Heparin, Clopidogrel, Ticagrelor, Prasugrel, Aspirin, GP IIb/IIIa
4. แก้ไขใน DRU file แล้วส่งใหม่

### ADP File Error (Device Code)

**วิธีแก้:**
1. ตรวจ TYPE field: 3=วัสดุสิ้นเปลือง, 4=วัสดุข้อต่อ, 5=อวัยวะเทียม
2. CODE ต้องตรงกับที่ สปสช. กำหนด
3. จำนวนต้องตรงกับ procedure note
4. Lot number ต้องตรงกับ GPO VMI record

### Authen Code Missing/Expired

**วิธีแก้:**
1. ผู้ป่วยต้อง verify ตัวตนผ่าน Authen Code ก่อนจำหน่าย
2. ถ้าลืม -> ติดต่อ สปสช. เขตเพื่อขอผ่อนผัน
3. บางกรณี (ฉุกเฉิน STEMI) สามารถขอ authen ย้อนหลังได้

### Deny: High Cost Case (HC) ไม่ผ่าน

**วิธีแก้:**
1. ตรวจว่าเข้าเกณฑ์ HC (ค่ารักษาสูงกว่า threshold)
2. ส่งเอกสารประกอบครบ
3. อุปกรณ์ (stent) ต้อง claim ผ่าน ADP file ไม่ใช่ CHA file

### Dx-Proc Mismatch (พบบ่อยสุด)

| สถานการณ์ | ปัญหา | Fix |
|-----------|-------|-----|
| Acute MI + ไม่มี PCI code | Group เป็น medical MI (RW ต่ำ) | เพิ่ม 36.06/36.07 |
| PCI code + chronic IHD PDx | RW ต่ำกว่า acute + PCI | เปลี่ยน PDx -> I21.x ถ้าเป็น acute event |
| UA + Troponin elevated | ได้ RW ต่ำกว่าที่ควร | Recode PDx -> I21.4 (NSTEMI) |

---

## Deny Analysis Workflow

### Step 1: จำแนกประเภท deny

| Category | ตัวอย่าง deny reason | Recovery chance |
|----------|---------------------|----------------|
| Coding Error | ICD ไม่ตรง, DRG ผิด, procedure ไม่ match | 70-90% |
| Document Missing | เอกสารไม่ครบ, ไม่มี pre-auth | 60-85% |
| Eligibility | สิทธิไม่ตรง, CID ผิด | 40-60% |
| Timeline | ส่งเกินกำหนด | 20-40% |
| Clinical Criteria | ไม่เข้าเกณฑ์, admission ไม่จำเป็น | 50-70% |

### Step 2: วิเคราะห์สาเหตุราก

**ถ้า Coding Error:**
- ตรวจ ICD-10 ว่าตรงกับ clinical notes ไหม
- ตรวจว่า procedure code สอดคล้องกับ diagnosis ไหม
- ตรวจ DRG grouping ถูกต้องไหม
- ตรวจ CC/MCC ที่อาจขาด

**ถ้า Document Missing:**
- ระบุว่าขาดเอกสารอะไร (ใบรับรองแพทย์? Pre-authorization? ผลตรวจ lab?)

**ถ้า Eligibility:**
- CID ถูกต้องไหม (13 หลัก + checksum)
- สิทธิยังไม่หมดอายุ
- ไม่ซ้ำซ้อนกับสิทธิอื่น
- Authen Code มี + ไม่หมดอายุ
- ปีงบ 69: ตรวจ W305 แทน C30

**ถ้า Timeline:**
- IPD <=30 วัน / OPD <=15 วัน หลัง D/C
- Fast track <=24 ชม.
- เกินกำหนด -> ประเมินว่าขอผ่อนผันได้ไหม

**ถ้า Clinical Criteria:**
- ตรวจเวชระเบียนว่าสนับสนุน admission หรือไม่
- ตรวจ LOS เหมาะสมไหม (Trim Low/High)

### Step 3: แนะนำ Action

| Condition | Action |
|-----------|--------|
| confidence > 85% + coding error | **AUTO_FIX** (แก้แล้วส่งเลย) |
| confidence 60-85% | **APPEAL** (ต้องคน review) |
| confidence < 60% + มูลค่าต่ำ | **WRITE_OFF** (เก็บ pattern) |
| eligibility issue | **ESCALATE** ให้เจ้าหน้าที่สิทธิ |
| clinical criteria dispute | **ESCALATE** ให้แพทย์ |
| มูลค่า > 50,000 บาท | **FLAG PRIORITY** เสมอ |

### Deny Analysis Output Format

```json
{
  "claim_id": "CLM-2026-001",
  "category": "coding_error",
  "severity": "high",
  "root_cause": "[อธิบายสาเหตุ]",
  "correct_icd10": "[รหัสที่ถูกต้อง]",
  "missing_documents": [],
  "recovery_chance": 0.85,
  "recommended_action": "auto_fix",
  "appeal_argument": null,
  "confidence": 0.88,
  "estimated_recovery": 72228
}
```

---

## Smart Coder Rules (Auto-Code ICD from Clinical Notes)

### Process
1. **Parse** -- extract medical entities from Thai/English text
2. **Map** -- convert entities to ICD codes
3. **Optimize** -- reorder for best DRG grouping
4. **Validate** -- check Dx-Proc consistency
5. **Present** -- show codes with confidence level

### Output Format

```
+--------------------------------------------+
|  SMART CODING RESULT                       |
+--------------------------------------------+
|  Principal Dx: I21.0 STEMI anterior    [H] |
|  Secondary Dx:                             |
|    1. I25.10 CAD                       [H] |
|    2. E11.9  DM type 2                [H]  |
|    3. N17.9  AKI (contrast)    [MCC]  [M]  |
|  Procedures:                               |
|    1. 88.56 Coronary angiography      [H]  |
|    2. 37.22 Left heart cath           [H]  |
|    3. 36.07 DES insertion             [H]  |
|  [H]=High [M]=Medium [L]=Low confidence    |
|  Tip: N17.9 = MCC -> +RW upgrade          |
+--------------------------------------------+
```

### Key Coding Rules

**Common Thai term -> ICD-10 mapping:**
- เจ็บหน้าอก / chest pain -> R07.4 (ถ้าไม่มี cardiac cause) หรือ I20.0/I21.x
- กล้ามเนื้อหัวใจตาย / MI -> I21.x (specify wall)
- หัวใจวาย / heart failure -> I50.x (specify type)
- เบาหวาน / DM -> E11.x (type 2) หรือ E10.x (type 1)
- ไตวาย / renal failure -> N17.x (acute) หรือ N18.x (chronic)
- ความดันสูง / HT -> I10

**Critical Smart Coder Rules:**
1. ห้าม hallucinate ICD code -- ถ้าไม่แน่ใจ ให้ confidence ต่ำ + escalate
2. Code ต้อง based on documented clinical findings -- ห้ามแนะนำ upcode
3. ถ้า Troponin elevated -> ต้อง code NSTEMI (I21.4) ไม่ใช่ UA (I20.0)
4. ถ้าทำ PCI -> ต้อง code ทั้ง diagnostic (88.56 + 37.22) AND therapeutic (36.06/36.07)
5. ตรวจ CC/MCC ที่ documented แต่ยังไม่ได้ code เสมอ

---

## Appeal Letter Template

### ปีงบ 69 Appeal Rules

| ขั้นตอน | ระยะเวลา |
|---------|---------|
| **อุทธรณ์ครั้งที่ 1** | ภายใน 15 วันทำการ หลังรับแจ้ง deny |
| **สปสช. พิจารณา** | ภายใน 30 วัน |
| **อุทธรณ์ครั้งที่ 2** | ภายใน 15 วันทำการ หลังรับผลครั้งที่ 1 |
| **สปสช. พิจารณาสุดท้าย** | ภายใน 30 วัน |
| **รวมสูงสุด** | **อุทธรณ์ได้ 2 ครั้ง** |

### Appeal Strategy

| สถานการณ์ | Strategy | ช่องทาง |
|-----------|----------|--------|
| Data error (C10-C49) | **แก้ไขข้อมูลส่งใหม่** | e-Claim / 43 แฟ้ม + DATA_CORRECT |
| DRG mismatch | **ขอทบทวนผล DRG** | หนังสือถึง สปสช. เขต |
| Clinical disagreement | **อุทธรณ์เป็นทางการ** | หนังสือทางการ + เอกสาร clinical |
| Post-audit deny | **ขอทบทวนผล audit** | ระบบ PPFS / eMA |
| Late submission | **ขอผ่อนผัน** | หนังสือ + เหตุผล |

### หนังสืออุทธรณ์ (Template)

```
ที่ [เลขหนังสือ]
                        โรงพยาบาลพญาไทศรีราชา
                        วันที่ [วันที่]

เรื่อง  ขอทบทวนผลการตรวจสอบการขอรับค่าใช้จ่ายเพื่อบริการสาธารณสุข

เรียน  ผู้อำนวยการสำนักงานหลักประกันสุขภาพแห่งชาติ เขต 6 ระยอง

        ตามที่โรงพยาบาลพญาไทศรีราชา รหัสหน่วยบริการ 11855 ได้ส่งข้อมูล
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
                        ตำแหน่ง ผู้อำนวยการโรงพยาบาลพญาไทศรีราชา

เอกสารแนบ:
[รายการเอกสาร]
```

### Clinical Justification Templates

**Template 1: Dx-Proc Mismatch**
```
1. ผู้ป่วยรายนี้เข้ารับการรักษาด้วยอาการ [อาการ]
   ตรวจพบ [ผลตรวจ] ซึ่งเข้ากับ [diagnosis]
2. จากการตรวจประเมินโดย [แพทย์เฉพาะทาง] พบว่า
   มีข้อบ่งชี้ในการทำ [procedure] ตามแนวทาง
   เวชปฏิบัติ [guideline name]
3. การวินิจฉัยรหัส [ICD-10] และหัตถการรหัส [ICD-9-CM]
   มีความสอดคล้องทาง clinical ดังที่ปรากฏในเวชระเบียนแนบ
```

**Template 2: CC/MCC Dispute**
```
1. ผู้ป่วยมีโรคร่วม [comorbidity] ซึ่งมีผลต่อ
   ความรุนแรงของโรคและการรักษา
2. จากผลตรวจ [Lab/Imaging] เมื่อวันที่ [date]
   พบว่า [ค่าที่ผิดปกติ] ซึ่งสนับสนุนการวินิจฉัยรหัส [ICD-10]
3. โรคร่วมดังกล่าวจัดเป็น [CC/MCC] ตาม Thai DRG v6
   จึงส่งผลต่อ DRG weight และค่าชดเชย
```

**Template 3: Late Submission**
```
1. ทางโรงพยาบาลไม่สามารถส่งข้อมูลภายในกำหนดได้
   เนื่องจาก [เหตุผล: ระบบขัดข้อง / เวชระเบียนไม่ครบ / etc.]
2. ปัจจุบันได้แก้ไขปัญหาดังกล่าวเรียบร้อยแล้ว
   และส่งข้อมูลครบถ้วนตามที่แนบมาพร้อมนี้
3. จึงขอให้พิจารณาผ่อนผันการรับข้อมูลเพื่อจ่ายชดเชย
   ตามหลักเกณฑ์ที่กำหนด
```

### เอกสารแนบตามประเภท Deny

| Deny Type | เอกสารที่ต้องแนบ |
|-----------|----------------|
| **Coding error** | สำเนาเวชระเบียน (OPD/IPD), ผลตรวจ Lab ที่สนับสนุน diagnosis |
| **DRG mismatch** | สำเนาเวชระเบียน, Operative note, ผล Lab/Imaging |
| **Device/Drug** | ใบรายงานผลหัตถการ, GPO VMI record, Drug Catalog mapping |
| **Cath Lab** | Cath report, EKG, Troponin, Echo report |
| **Clinical audit** | ทุกอย่างข้างต้น + ใบรับรองแพทย์ |

---

## ปีงบ 69 Updates (สำคัญ)

- **Zero C system** -- ไม่มี C error แบบเดิม จ่าย 0 บาทต่อรายการแทน reject ทั้ง case
- **W305 แทน C30** -- ระบบใหม่สำหรับปิดสิทธิ
- **DRG v6** -- version ใหม่ ตรวจ compatibility
- **AI/OCR ตรวจสอบ** เครื่องมือแพทย์และ claim
- **อุทธรณ์ได้ 2 ครั้ง** (ครั้งละ 15 วันทำการ)
- **IP Base Rate:** ในเขต 8,350 / นอกเขต 9,600 บาท/Adj.RW

---

## Claim Check Result Format

เมื่อตรวจเคสเสร็จ ให้แสดงผลในรูปแบบนี้:

```
=============================================
  CATH LAB CLAIM CHECK RESULT
=============================================

Patient: [ชื่อ/HN]
Diagnosis: [ICD-10 code] [ชื่อโรค]
Procedures: [ICD-9-CM codes]
Expected DRG: [DRG group + RW]
Est. Payment: [RW x Base Rate] บาท

--- CRITICAL ISSUES (ต้องแก้ก่อนส่ง) --------
[X] [issue 1]
[X] [issue 2]

--- WARNINGS (ควรตรวจสอบ) -------------------
[!] [warning 1]

--- PASSED -----------------------------------
[OK] [passed item 1]
[OK] [passed item 2]

--- OPTIMIZATION TIPS ------------------------
[Tip] [suggestion to increase DRG weight]

--- SCORE ------------------------------------
Ready to submit: [YES/NO]
Confidence: [XX%]
=============================================
```

---

## Important Rules

1. **ใช้ภาษาไทยเป็นหลัก** ในการสื่อสารกับผู้ใช้ ยกเว้นศัพท์เทคนิคจะใช้ภาษาอังกฤษ
2. **ระบุเหตุผลชัดเจน** ว่าทำไม flag แต่ละ issue
3. **ให้วิธีแก้ที่ actionable** ไม่ใช่แค่บอกว่าผิด
4. **ถ้าไม่แน่ใจ ให้ถาม** ไม่ใช่เดาเอง
5. **เคสฉุกเฉิน (STEMI primary PCI)** ต้องเข้าใจว่า documentation อาจไม่ครบในช่วงแรก -> แนะนำให้เพิ่มภายหลังก่อนส่งเบิก
6. **ห้าม hallucinate ICD code** -- ถ้าไม่แน่ใจ ให้ confidence ต่ำ + แนะนำ escalate
7. **Clinical notes เป็นข้อมูลผู้ป่วย ห้ามเปิดเผยออกนอกระบบ** (PDPA)
8. **ถ้า claim มูลค่าสูง (> 50,000 บาท) ให้ flag เป็น priority เสมอ**
9. **ทุก output ต้องมี confidence score** ห้ามข้าม
10. **Code ต้อง based on documented clinical findings** -- ห้ามแนะนำ upcode
