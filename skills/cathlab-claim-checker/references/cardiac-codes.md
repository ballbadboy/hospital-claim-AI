# Cardiac ICD Codes for Cath Lab

## ICD-10-TM Diagnosis Codes (Ischemic Heart Disease I20-I25)

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
| I21.9 | Acute MI, unspecified | Unspecified | หลีกเลี่ยง — ควรระบุให้ specific |

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

## Coding Rules สำคัญ

### Diagnostic Cath + PCI ในวันเดียวกัน
- Code ทั้ง diagnostic (37.22 + 88.56) AND therapeutic (36.06/36.07)
- Diagnostic cath ไม่ได้ bundle กับ PCI ใน Thai DRG
- ต้อง document ว่า decision to intervene เกิดหลังจาก diagnostic cath

### Multiple Vessel PCI
- ใช้ 36.05 สำหรับ multi-vessel PTCA
- ระบุจำนวน vessel และ stent แต่ละ vessel ใน extension code
- แต่ละ vessel ต้อง document indication แยก

### Staged Procedure (PCI คนละวัน)
- ถ้า diagnostic cath วันหนึ่ง แล้ว PCI อีกวัน → 2 admissions แยก
- ห้าม re-bill diagnostic cath ในวันที่ทำ PCI
- ถ้าเป็นถ้า admit ครั้งเดียว → code ทั้งหมดในเคสเดียว

### Common CC/MCC Comorbidities
| Code | Description | CC/MCC |
|------|-------------|--------|
| E11.x | Type 2 DM | CC |
| N18.3 | CKD Stage 3 | CC |
| N18.4 | CKD Stage 4 | MCC |
| I50.2x | Systolic heart failure (acute) | MCC |
| I50.3x | Diastolic heart failure (acute) | MCC |
| I48.x | Atrial fibrillation | CC |
| J44.1 | COPD with acute exacerbation | MCC |
| I10 | Essential hypertension | Neither |
| E78.5 | Dyslipidemia | Neither |
