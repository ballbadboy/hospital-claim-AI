# Cath Lab Claim AI — Knowledge Base Source Guide
## 8 แหล่งข้อมูลหลัก พร้อม URL ดาวน์โหลด

---

## 1. DRG Version Manual (Thai)
**เวอร์ชันปัจจุบัน:** Thai DRG v6.3.3 (ไม่มี v7 อย่างเป็นทางการ — v6.3.x คือเวอร์ชันล่าสุด)

**หน่วยงาน:** สำนักพัฒนากลุ่มโรคร่วมไทย (สรท.) / Thai CaseMix Centre (TCMC)

**URL ดาวน์โหลด:**
- คู่มือ TDRG v6.3.3: https://www.tcmc.or.th/_content_images/download/fileupload/S0091.pdf
- Presentation TDRG v6.3 for NHSO: https://www.sshos.go.th/wp-content/uploads/2024/04/25-4-67-ThaiDRGver634NHSO20240425NK2.pdf
- เว็บหลัก TCMC: https://www.tcmc.or.th/tdrg
- DRG Grouper software (TDS6305.EXE): ขอจาก TCMC โดยตรง (info@tcmc.or.th)

**ข้อมูลที่ต้องดึงมาใช้:**
- เล่ม 1: General description, RW table, LOS adjustment
- เล่ม 2: MDC 05 (Diseases of Circulatory System) — cardiac DRG grouping logic
- Appendix B: Procedure codes (OR/Non-OR classification)
- Appendix F: CC/MCC tables — DCL (Diagnosis Complexity Level) per DC
- RW (Relative Weight) table — ค่าน้ำหนักสัมพัทธ์ทุก DRG

**ติดต่อ TCMC:**
- Line: @thaicasemix
- Facebook: Thaicasmix / Casemix
- Email: info@tcmc.or.th
- Tel: 02-298-0769

---

## 2. ICD-10-TM Cardiac Codes
**เวอร์ชัน:** ICD-10-TM 2024 (Thai Modification)

**หน่วยงาน:** ศูนย์ให้รหัสโรคของประเทศไทย (Thai Health Coding Center - THCC)

**URL อ้างอิง:**
- THCC: http://www.thcc.or.th/
- ICD-10 data (international reference): https://www.icd10data.com/ICD10CM/Codes/I00-I99/I20-I25/

**Cardiac Codes ที่เกี่ยวข้องกับ Cath Lab:**

### Ischemic Heart Diseases (I20-I25)
| Code | Description | Thai Name |
|------|-------------|-----------|
| I20.0 | Unstable angina | กล้ามเนื้อหัวใจขาดเลือดเฉียบพลันชนิดไม่คงที่ |
| I20.1 | Angina pectoris with documented spasm | |
| I20.8 | Other forms of angina | |
| I20.9 | Angina pectoris, unspecified | |
| I21.0 | Acute transmural MI - anterior wall (STEMI) | กล้ามเนื้อหัวใจตายเฉียบพลัน ผนังด้านหน้า |
| I21.1 | Acute transmural MI - inferior wall (STEMI) | กล้ามเนื้อหัวใจตายเฉียบพลัน ผนังด้านล่าง |
| I21.2 | Acute transmural MI - other sites (STEMI) | |
| I21.3 | Acute transmural MI - unspecified site (STEMI) | |
| I21.4 | Acute subendocardial MI (NSTEMI) | กล้ามเนื้อหัวใจตายเฉียบพลันชนิด NSTEMI |
| I21.9 | Acute MI, unspecified | |
| I22.x | Subsequent MI (within 28 days) | กล้ามเนื้อหัวใจตายซ้ำ |
| I24.0 | Acute coronary thrombosis not resulting in MI | |
| I25.1 | Atherosclerotic heart disease | โรคหลอดเลือดหัวใจอุดตัน |
| I25.10 | Chronic IHD without angina | |
| I25.2 | Old myocardial infarction | กล้ามเนื้อหัวใจตายเก่า |
| I25.5 | Ischemic cardiomyopathy | |

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

---

## 3. ICD-9-CM Procedure Codes
**เวอร์ชัน:** ICD-9-CM with Thai Extension codes

**Cardiac Catheterization & PCI Procedures:**

### Diagnostic Catheterization
| Code | Description |
|------|-------------|
| 37.21 | Right heart catheterization |
| 37.22 | Left heart catheterization |
| 37.23 | Combined R+L heart catheterization |

### Coronary Angiography
| Code | Description |
|------|-------------|
| 88.55 | Coronary arteriography NOS |
| 88.56 | Coronary arteriography using 2 catheters |
| 88.57 | Other and unspecified coronary arteriography |

### Percutaneous Coronary Intervention (PCI)
| Code | Description |
|------|-------------|
| 36.01 | PTCA single vessel without drug-eluting stent |
| 36.02 | PTCA single vessel with drug-eluting stent |
| 36.05 | PTCA multiple vessels |
| 36.06 | Insertion of non-drug-eluting coronary stent |
| 36.07 | Insertion of drug-eluting coronary stent (DES) |
| 36.09 | Other PTCA |

### Other Cardiac Procedures
| Code | Description |
|------|-------------|
| 36.1x | CABG (bypass graft) |
| 37.61 | IABP implantation |
| 37.34 | Excision/destruction of cardiac tissue (ablation) |
| 39.50 | Angioplasty of non-coronary vessel |

**Extension Code Format:**
- Format: XX.XX + 2 digits (position + count)
- Example: 36.0601 = PTCA 1 vessel, 1 stent at position 1

---

## 4. NHSO Fee Schedule
**หน่วยงาน:** สำนักงานหลักประกันสุขภาพแห่งชาติ (สปสช.)

**URL ดาวน์โหลด:**
- NHSO Downloads: https://www.nhso.go.th/downloads/210
- Fee Schedule Excel: ดาวน์โหลดจากลิงก์ใน NHSO downloads page
- Thai Medical Device Association mirror: https://thaimed.co.th/en/10482

**รายละเอียด:**
- รายการยา Fee Schedule: 2,838 รายการ (GPUID)
- รายการบริการทั่วไป: 587 รายการ (updated)
- อัตราจ่ายอุปกรณ์ cardiac: stent, balloon, guidewire, IABP
- ประกาศ FS เอกสารแนบ 1 + 2

**Cardiac-specific items to extract:**
- Stent (BMS) reimbursement rate
- Stent (DES) reimbursement rate
- Balloon catheter rate
- IABP rate
- Temporary pacemaker rate
- Guidewire/catheter rates

---

## 5. FDH 16-File Structure
**หน่วยงาน:** กองเศรษฐกิจสุขภาพฯ กระทรวงสาธารณสุข

**URL ดาวน์โหลด:**
- FDH Main Portal: https://fdh.moph.go.th
- สาธิตการใช้งาน FDH: https://www.uckkpho.com/wp-content/uploads/2024/03/สาธิตการใช้งาน-FDH.pdf
- แนวทาง FDH to NHSO: https://www.uckkpho.com/wp-content/uploads/2024/03/อภิปราย-2_หลักเกณฑ์และวิธีการ-FDH-to-NHSO-กศภ.pdf
- อบรม "กรณีติด C": https://www.sshos.go.th/financial-data-hub/ (10 เม.ย. 67)
- Drug Catalog + Lab Catalog: https://www.sshos.go.th/financial-data-hub/ (8 มี.ค. 67)

**16 แฟ้มที่เกี่ยวข้องกับ Cath Lab claims:**

| File | Name | Cath Lab Relevance |
|------|------|-------------------|
| IPD | Inpatient data | Admission/discharge dates, ward, LOS |
| DIA | Diagnosis | PDx (I21.x), SDx (comorbidities) |
| OPR | OR Procedure | ICD-9-CM codes (36.06, 37.22, etc.) |
| ADP | Additional Payment | Device codes (stent type, TYPE=3-5) |
| DRU | Drug | Drug catalog codes (must match FDH Drug Catalog) |
| CHA | Charge | Charge items by category |
| LVD | Leave/Discharge | Discharge type, D/C status |
| INS | Insurance | สิทธิ/กองทุน verification |

**C-Code Errors (common for Cath Lab):**
- C-438: สิทธิประโยชน์ไม่ตรง
- Various: Drug Catalog mismatch, Lab Catalog mismatch
- Format errors in ADP file (device codes)
- Authen Code missing/expired

**Reference:** https://www.uckkpho.com/uc/1313/ (รายละเอียด C-codes)

---

## 6. GPO Stent VMI/SMI Data
**หน่วยงาน:** องค์การเภสัชกรรม (GPO)

**URL:**
- VMI Stent Portal: https://scm.gpo.or.th/vmi_next/nhso/stent
- แบบฟอร์มใบนำส่งขดลวดค้ำยัน: ดาวน์โหลดจาก portal

**ข้อมูลที่ต้องใช้:**
- Approved stent catalog (BMS vs DES)
- Stent specifications (size range, length)
- Lot/serial number tracking format
- Procurement code ที่ใช้ใน ADP file
- VMI delivery records matching to individual cases

**สิ่งที่ต้องตรวจสอบ:**
- Stent type ใน procedure note = Stent type ใน ADP file = Stent type ใน GPO VMI
- Quantity used = Quantity claimed
- Lot number traceable

---

## 7. Hospital Historical Data
**แหล่งข้อมูล:** FDH Dashboard ของโรงพยาบาล

**URL:** https://fdh.moph.go.th/hospital/nhso/dashboard

**วิธี Export:**
1. Login FDH Dashboard
2. ไปที่ กองทุนสปสช. → Dashboard
3. Filter: Primary Diagnosis contains "I20" OR "I21" OR "I25"
4. Filter: Procedure code contains "36" OR "37.2" OR "88.5"
5. Export เป็น CSV/Excel

**ข้อมูลที่ต้อง export:**
- วันที่จำหน่าย (Discharge date)
- Primary Diagnosis + code
- Procedure codes
- Project code (กองทุน)
- จำนวนเงินขอเบิก
- DRG Version ที่ได้
- DRG assigned
- Status (อนุมัติ / อยู่ระหว่างปรับปรุง / Deny)
- Deny reason (ถ้ามี)

**จากภาพ FDH Dashboard ที่ถ่ายมา:** มี 181 records ต้อง export ทั้งหมด

---

## 8. Clinical Guidelines
**แหล่งข้อมูลหลัก:**

### Thai Heart Association (สมาคมโรคหัวใจแห่งประเทศไทย)
- PCI Guideline: http://www.thaiheart.org/images/column_1291454908/PCIGuideline.pdf
- Website: http://www.thaiheart.org

### ACC/AHA Guidelines (International Reference)
- 2021 ACC/AHA/SCAI Guideline for Coronary Artery Revascularization
- URL: https://www.ahajournals.org/doi/10.1161/CIR.0000000000001038

### Key Clinical Criteria for Claims:

**STEMI Diagnosis requires ALL of:**
1. Chest pain / ischemic symptoms
2. ST elevation on EKG (or new LBBB)
3. Troponin elevation (above 99th percentile URL)
4. Door-to-Balloon time documented (target <90 min for primary PCI)

**NSTEMI Diagnosis requires:**
1. Troponin elevation with rise/fall pattern
2. Clinical symptoms of ischemia
3. EKG changes (ST depression, T-wave inversion) — OR — imaging evidence
4. Risk stratification: GRACE score or TIMI score

**Unstable Angina:**
1. Anginal symptoms at rest or crescendo pattern
2. Normal or minimally elevated Troponin
3. EKG changes possible but not required
4. Risk stratification for cath timing

**PCI Indication (must be documented):**
- Significant stenosis (>70% diameter) in target vessel
- Correlation with clinical symptoms or functional ischemia
- Not purely prophylactic in asymptomatic patients
- FFR <0.80 if stenosis is borderline (50-70%)

---

## Action Items สำหรับทีม Noi

### ผมหาให้ได้แล้ว (Online Sources):
✅ Thai DRG v6.3.3 manual PDF
✅ ICD-10-TM cardiac code tables
✅ ICD-9-CM procedure code tables  
✅ NHSO Fee Schedule download links
✅ FDH 16-file documentation links
✅ GPO VMI portal link
✅ Clinical guidelines (Thai + ACC/AHA)

### Noi ต้องจัดหา (Hospital-Specific):
❑ FDH Dashboard export CSV (181 records — filter Cath Lab)
❑ Cath lab case log (procedure + stent details)
❑ Drug Catalog mapping file (HIS → FDH)
❑ Lab Catalog mapping file (HIS → FDH)
❑ Sample of successfully paid claims (for comparison)
❑ Sample of denied claims with deny reasons
❑ ADP file template currently used for cardiac devices

---

*Compiled: March 2026 | AI Hospital Hub | For Cath Lab Claim Optimization Project*
