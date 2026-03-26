# Deny Test Cases for AI Claim Validator

> Compiled from: NHSO official rules, e-Claim system documentation, NHSO YouTube series (สปสช. channel),
> fiscal year 2569 policy briefings, and published Thai DRG audit patterns.
>
> Last updated: 2026-03-25
> Total test cases: 30
> Purpose: Validate the Hospital Claim AI agent against realistic deny scenarios

---

## Table of Contents

1. [Test Cases by Category](#test-cases-by-category)
2. [Statistical Reference Data](#statistical-reference-data)
3. [C-Code / Deny Code Reference](#c-code--deny-code-reference)
4. [DRG Error Code Reference](#drg-error-code-reference)
5. [Sources & Methodology](#sources--methodology)

---

## Test Cases by Category

### Category A: Diagnosis-Procedure Mismatch (5 cases)

#### TC-01: STEMI without PCI procedure code

| Field | Value |
|-------|-------|
| **Case ID** | TC-01 |
| **Department** | Cath Lab |
| **Patient** | Male, 62 years |
| **PDx** | I21.0 (Acute transmural MI of anterior wall) |
| **SDx** | I10, E11.9, E78.5 |
| **Procedure codes** | None recorded |
| **Expected deny reason** | Diagnosis-Procedure mismatch: STEMI diagnosis without any PCI/catheterization procedure code. DRG groups as medical MI only (low RW) |
| **DRG impact** | Groups to MDC 05 medical instead of surgical. RW drops from ~4.5 to ~1.2 |
| **Deny code** | DRG Error (ungroupable or low RW mismatch) |
| **What was wrong** | Cath lab performed PCI with stent but coder forgot to enter ICD-9-CM codes 36.06 (coronary artery angioplasty), 88.56 (coronary arteriography), 37.22 (left heart catheterization) in OPR file |
| **How to fix** | Add procedure codes 36.06/36.07 + 88.56 + 37.22 to OPR file. Verify procedure date matches admission window |
| **Estimated amount lost** | ~27,000 THB (difference between surgical vs medical DRG at 8,350 THB/RW) |
| **AI checkpoint** | #2 Dx-Proc Match |

---

#### TC-02: Chronic IHD coded as PDx with PCI performed

| Field | Value |
|-------|-------|
| **Case ID** | TC-02 |
| **Department** | Cath Lab |
| **Patient** | Male, 55 years |
| **PDx** | I25.1 (Atherosclerotic heart disease) |
| **SDx** | I10, E78.5, E11.9 |
| **Procedure codes** | 36.07, 88.56, 37.22 |
| **Expected deny reason** | PDx is chronic IHD but PCI was performed. If patient had acute event (elevated troponin), PDx should be I21.x (Acute MI). Groups as "PTCA w/o significant CCC" instead of "Acute MI w/ PCI" |
| **DRG impact** | RW ~2.8 instead of ~4.5 (loss of ~1.7 RW) |
| **Deny code** | Not denied outright but significant underpayment |
| **What was wrong** | Patient presented with NSTEMI (troponin elevated) but coder used chronic IHD code instead of I21.4 |
| **How to fix** | Change PDx to I21.4 (NSTEMI). Verify troponin documentation supports acute MI diagnosis |
| **Estimated amount lost** | ~14,200 THB underpayment |
| **AI checkpoint** | #2 Dx-Proc Match, #6 CC/MCC Optimization |

---

#### TC-03: Unstable angina with elevated troponin

| Field | Value |
|-------|-------|
| **Case ID** | TC-03 |
| **Department** | Cath Lab |
| **Patient** | Female, 68 years |
| **PDx** | I20.0 (Unstable angina) |
| **SDx** | I10, N18.3, E11.65 |
| **Procedure codes** | 36.06, 88.56, 37.22 |
| **Expected deny reason** | Unstable angina diagnosis but troponin was elevated per medical record. Should be NSTEMI (I21.4). UA requires troponin NORMAL |
| **DRG impact** | Difference of ~1.5 RW between UA+PCI and AMI+PCI |
| **Deny code** | Coding audit finding (potential clawback) |
| **What was wrong** | Coder did not check troponin result. UA should only be coded when troponin is within normal range |
| **How to fix** | Recode PDx to I21.4 (NSTEMI). Document troponin trend (rise/fall pattern) |
| **Estimated amount lost** | ~12,500 THB underpayment |
| **AI checkpoint** | #2 Dx-Proc Match |

---

#### TC-04: Pneumonia with thoracoscopy - mismatch

| Field | Value |
|-------|-------|
| **Case ID** | TC-04 |
| **Department** | Surgery |
| **Patient** | Male, 45 years |
| **PDx** | J18.9 (Pneumonia, unspecified organism) |
| **SDx** | J90 (Pleural effusion) |
| **Procedure codes** | 34.21 (Thoracoscopy) |
| **Expected deny reason** | J18.9 is nonspecific pneumonia. Thoracoscopy suggests empyema or complicated pleural effusion. PDx should be J86.9 (Empyema) or J90 (Pleural effusion) if that was the reason for surgery |
| **DRG impact** | Surgical DRG for empyema/pleural drainage has higher RW than medical pneumonia |
| **Deny code** | Potential audit finding for Dx-Proc inconsistency |
| **What was wrong** | PDx does not justify the surgical intervention. The condition requiring surgery should be the PDx |
| **How to fix** | Change PDx to J86.9 or appropriate specific diagnosis that justified thoracoscopy. Move J18.9 to SDx |
| **Estimated amount lost** | ~8,000-15,000 THB depending on DRG group change |
| **AI checkpoint** | #2 Dx-Proc Match |

---

#### TC-05: Dialysis claim with AKI coded wrong

| Field | Value |
|-------|-------|
| **Case ID** | TC-05 |
| **Department** | Nephrology |
| **Patient** | Female, 72 years |
| **PDx** | N18.5 (CKD Stage 5) |
| **SDx** | N17.9 (Acute kidney injury, unspecified) |
| **Procedure codes** | 39.95 (Hemodialysis) |
| **Expected deny reason** | Patient had AKI on CKD. When AKI is the acute event requiring emergent dialysis, N17.x should be PDx and N18.5 should be SDx. Affects DRG grouping |
| **DRG impact** | AKI as PDx with dialysis groups differently (potentially higher RW with MCC) than CKD Stage 5 maintenance dialysis |
| **Deny code** | Underpayment / audit finding |
| **What was wrong** | Coder put chronic condition as PDx instead of the acute event that triggered admission |
| **How to fix** | Swap PDx to N17.9, move N18.5 to SDx. Document acute deterioration requiring emergent HD |
| **Estimated amount lost** | ~5,000-10,000 THB |
| **AI checkpoint** | #2 Dx-Proc Match |

---

### Category B: Missing/Invalid Authen Code (3 cases)

#### TC-06: No Authen Code for UC patient (C30/W305)

| Field | Value |
|-------|-------|
| **Case ID** | TC-06 |
| **Department** | Internal Medicine |
| **Patient** | Male, 58 years, UC right |
| **PDx** | I50.9 (Heart failure, unspecified) |
| **SDx** | I10, E11.9, N18.3 |
| **Procedure codes** | None (medical case) |
| **Authen Code** | Missing |
| **Expected deny reason** | W305 (formerly C30) -- no verification of identity/right at end of service. Entire claim denied |
| **Deny code** | W305 (replaces C30 from FY2569 onwards) |
| **What was wrong** | Patient discharged without identity verification. No Authen Code generated |
| **How to fix** | Appeal via SMCS system within 10 days. Upload supporting documents. Hospital administrator must approve via Thai ID login. If appeal window missed, payment = 0 THB |
| **Estimated amount** | Full claim denied: ~25,000-40,000 THB |
| **AI checkpoint** | #5 Timing & Authorization |

---

#### TC-07: Expired Authen Code

| Field | Value |
|-------|-------|
| **Case ID** | TC-07 |
| **Department** | Surgery (Ortho) |
| **Patient** | Female, 70 years, UC right |
| **PDx** | M17.1 (Primary gonarthrosis, bilateral) |
| **SDx** | I10, E11.9 |
| **Procedure codes** | 81.54 (Total knee replacement) |
| **Authen Code** | PP1007991295 (expired -- generated >24 hrs before discharge) |
| **Expected deny reason** | Authen Code expired. Code was generated at admission but patient stayed 5 days; code must be re-verified before discharge |
| **Deny code** | W305 / Authen validation failure |
| **What was wrong** | Authen Code has time limit. Long-stay patients need re-verification before discharge |
| **How to fix** | Re-verify patient identity before discharge using Face Recognition or LINE. For retroactive cases, appeal within 10 days via SMCS |
| **Estimated amount** | Full TKA claim: ~80,000-120,000 THB at risk |
| **AI checkpoint** | #5 Timing & Authorization |

---

#### TC-08: STEMI emergency - Authen obtained retroactively

| Field | Value |
|-------|-------|
| **Case ID** | TC-08 |
| **Department** | Cath Lab / ER |
| **Patient** | Male, 50 years, UC right |
| **PDx** | I21.0 (Anterior STEMI) |
| **SDx** | I10 |
| **Procedure codes** | 36.06, 88.56, 37.22 |
| **Authen Code** | Retroactive request filed |
| **Expected deny reason** | Emergency STEMI -- patient unconscious at presentation. Cannot verify identity via Face Recognition. Authen obtained retroactively |
| **Deny code** | Initially W305, but should be approved on appeal for emergency cases |
| **What was wrong** | Emergency case -- verification was impossible at time of service. Retroactive Authen request is allowed per NHSO policy for true emergencies |
| **How to fix** | File retroactive Authen request to NHSO regional office with supporting ER documentation, triage records, and clinical justification |
| **Estimated amount** | PCI claim: ~100,000-150,000 THB |
| **AI checkpoint** | #5 Timing & Authorization (emergency exception) |

---

### Category C: Late Submission / Timing Errors (3 cases)

#### TC-09: Claim submitted 45 days after discharge

| Field | Value |
|-------|-------|
| **Case ID** | TC-09 |
| **Department** | Surgery |
| **Patient** | Female, 55 years |
| **PDx** | K80.1 (Calculus of gallbladder with cholecystitis) |
| **SDx** | E11.9 |
| **Procedure codes** | 51.23 (Laparoscopic cholecystectomy) |
| **Discharge date** | 2026-01-15 |
| **Submission date** | 2026-03-01 (45 days after D/C) |
| **Expected deny reason** | Late submission -- beyond 30-day window. Payment rate reduced |
| **Deny code** | Late submission penalty |
| **What was wrong** | Hospital billing team missed the 30-day submission deadline. No alert system in place |
| **How to fix** | Submit immediately. Accept reduced payment rate. Implement automated alert system to flag claims approaching 30-day deadline |
| **Estimated amount lost** | 10-30% reduction on claim of ~30,000 THB = ~3,000-9,000 THB penalty |
| **AI checkpoint** | #5 Timing |

---

#### TC-10: Service date outside eligible period

| Field | Value |
|-------|-------|
| **Case ID** | TC-10 |
| **Department** | General Medicine |
| **Patient** | Male, 65 years |
| **PDx** | J44.1 (COPD with acute exacerbation) |
| **SDx** | J96.00, I10, E11.9 |
| **Procedure codes** | 96.71 (Mechanical ventilation <96 hrs) |
| **Service date** | 2025-09-14 (before FY2569 eligible start date of 2025-09-16) |
| **Expected deny reason** | Service date falls outside the eligible fiscal year period. FY2569 covers 16 Sep 2568 to 15 Sep 2569 |
| **Deny code** | Data validation error |
| **What was wrong** | Admission date is 2 days before the fiscal year start date for the claim period |
| **How to fix** | Submit under the previous fiscal year (FY2568) if deadline not passed. Otherwise, appeal to NHSO regional office |
| **Estimated amount** | Full claim at risk: ~40,000-60,000 THB |
| **AI checkpoint** | #5 Timing |

---

#### TC-11: IPD admission less than 2 hours

| Field | Value |
|-------|-------|
| **Case ID** | TC-11 |
| **Department** | Day Surgery |
| **Patient** | Male, 40 years |
| **PDx** | K40.9 (Inguinal hernia without obstruction or gangrene) |
| **SDx** | None |
| **Procedure codes** | 53.00 (Unilateral repair inguinal hernia) |
| **Admission time** | 08:00 |
| **Discharge time** | 09:30 (1.5 hours) |
| **Expected deny reason** | Stay < 2 hours counts as OPD, not IPD per NHSO rules. Except if patient dies, is referred, or leaves against advice |
| **Deny code** | IPD claim rejected -- reclassified as OPD |
| **What was wrong** | Claimed as IPD but LOS < 2 hours. Should have been claimed as ODS (One Day Surgery) or OPD |
| **How to fix** | Reclassify as OPD claim with appropriate Free Schedule items. If qualifies for ODS (2-24 hrs), document accordingly |
| **Estimated amount impact** | IPD claim ~20,000 THB vs OPD claim ~5,000-8,000 THB |
| **AI checkpoint** | #4 16-File Completeness (LOS check) |

---

### Category D: Device/Equipment Documentation Errors (3 cases)

#### TC-12: Stent lot number mismatch with GPO record

| Field | Value |
|-------|-------|
| **Case ID** | TC-12 |
| **Department** | Cath Lab |
| **Patient** | Male, 60 years |
| **PDx** | I21.1 (Acute transmural MI of inferior wall) |
| **SDx** | I10, E11.9 |
| **Procedure codes** | 36.07, 88.56, 37.22 |
| **ADP file** | TYPE=5, CODE=DES stent code, QTY=2, SERIALNO=ABC123456 |
| **Expected deny reason** | Lot number in ADP file does not match GPO VMI procurement record. QTY=2 but procedure note mentions only 1 stent placed |
| **Deny code** | ADP Error -- device code/qty mismatch |
| **What was wrong** | (1) Serial/lot number transcription error. (2) Quantity discrepancy between ADP file and procedure note |
| **How to fix** | Correct lot number to match GPO VMI record. Reconcile quantity with operative note. If 2 stents were truly used, update procedure note. If only 1, correct ADP to QTY=1 |
| **Estimated amount** | Device cost at risk: ~40,000-80,000 THB per stent |
| **AI checkpoint** | #3 Device Documentation |

---

#### TC-13: DES stent coded as BMS in ADP

| Field | Value |
|-------|-------|
| **Case ID** | TC-13 |
| **Department** | Cath Lab |
| **Patient** | Female, 65 years |
| **PDx** | I21.4 (NSTEMI) |
| **SDx** | I10, E11.9, N18.3 |
| **Procedure codes** | 36.06, 88.56, 37.22 |
| **ADP file** | TYPE=5, CODE=BMS code (but DES actually used) |
| **Expected deny reason** | ADP device code is for BMS but procedure note and implant sticker indicate DES was used. Reimbursement for BMS is significantly lower than DES |
| **Deny code** | ADP Error / underpayment |
| **What was wrong** | Coder selected wrong device code in ADP file. DES and BMS have different NHSO reimbursement codes |
| **How to fix** | Update ADP CODE to correct DES device code matching the NHSO fee schedule. Ensure lot number matches implant sticker |
| **Estimated amount lost** | DES ~45,000-60,000 THB vs BMS ~15,000-20,000 THB. Loss: ~30,000-40,000 THB |
| **AI checkpoint** | #3 Device Documentation |

---

#### TC-14: Ortho implant not in NHSO approved list

| Field | Value |
|-------|-------|
| **Case ID** | TC-14 |
| **Department** | Orthopedics |
| **Patient** | Male, 35 years |
| **PDx** | S72.0 (Fracture of neck of femur) |
| **SDx** | None |
| **Procedure codes** | 79.35 (Open reduction internal fixation, femur) |
| **ADP file** | TYPE=4, CODE=unlisted implant code, QTY=1 plate + 6 screws |
| **Expected deny reason** | Implant code not found in NHSO approved device catalog. Device exists but code mapping is incorrect |
| **Deny code** | ADP Error -- invalid device code |
| **What was wrong** | Hospital used a new implant brand. The HIS device code was not mapped to the NHSO standard code |
| **How to fix** | Map hospital's internal device code to the correct NHSO ADP code. Update ADP file with valid code |
| **Estimated amount at risk** | Implant cost: ~50,000-100,000 THB |
| **AI checkpoint** | #3 Device Documentation |

---

### Category E: Drug & Lab Catalog Mismatch (3 cases)

#### TC-15: Drug GPUID not in FDH Drug Catalog

| Field | Value |
|-------|-------|
| **Case ID** | TC-15 |
| **Department** | Cardiology |
| **Patient** | Male, 58 years |
| **PDx** | I21.4 (NSTEMI) |
| **SDx** | I10, E11.9 |
| **DRU file** | Ticagrelor 90mg -- hospital drug code = TIC90, but GPUID not mapped to FDH catalog |
| **Expected deny reason** | Drug code in DRU file does not match FDH Drug Catalog. GPUID mismatch |
| **Deny code** | Drug Catalog Mismatch |
| **What was wrong** | Hospital's internal drug code was not properly mapped to the national GPUID/TMT standard in FDH Drug Catalog |
| **How to fix** | Download latest FDH Drug Catalog. Map hospital drug code TIC90 to correct GPUID for Ticagrelor 90mg. Update DRU file and resubmit |
| **Estimated amount** | Drug cost portion denied: ~2,000-5,000 THB |
| **AI checkpoint** | #4 16-File Completeness |

---

#### TC-16: Lab code not mapped to FDH Lab Catalog

| Field | Value |
|-------|-------|
| **Case ID** | TC-16 |
| **Department** | Internal Medicine |
| **Patient** | Female, 60 years |
| **PDx** | E11.2 (DM Type 2 with renal complications) |
| **SDx** | N18.3, I10 |
| **Lab file** | HbA1C test -- hospital lab code not mapped to TMLT standard |
| **Expected deny reason** | Lab code mismatch with FDH Lab Catalog |
| **Deny code** | Lab Catalog Mismatch |
| **What was wrong** | Hospital's internal lab code for HbA1C was not mapped to the national TMLT standard code |
| **How to fix** | Map hospital lab code to TMLT standard. Ensure lab result data format matches FDH requirements |
| **Estimated amount** | Lab portion denied: ~150-500 THB per test |
| **AI checkpoint** | #4 16-File Completeness |

---

#### TC-17: Chemo drug not in Fee Schedule

| Field | Value |
|-------|-------|
| **Case ID** | TC-17 |
| **Department** | Oncology |
| **Patient** | Female, 52 years |
| **PDx** | C50.9 (Malignant neoplasm of breast, unspecified) |
| **SDx** | None |
| **Procedure codes** | 99.25 (Injection of cancer chemotherapeutic substance) |
| **Drug** | Pertuzumab (not in NHSO Fee Schedule for this indication) |
| **Expected deny reason** | Chemotherapy drug not in NHSO approved Fee Schedule. Drug billed but not reimbursable |
| **Deny code** | Drug not in Fee Schedule |
| **What was wrong** | Hospital administered Pertuzumab but this drug is not covered under NHSO Fee Schedule for UC patients in this indication/protocol |
| **How to fix** | Verify drug is in NHSO Fee Schedule before administration. If not covered, inform patient about out-of-pocket cost. For covered alternatives, use approved protocol (e.g., Herceptin monotherapy if HER2+) |
| **Estimated amount** | Drug cost not reimbursed: ~50,000-100,000 THB per cycle |
| **AI checkpoint** | #2 Dx-Proc Match (protocol check) |

---

### Category F: DRG Grouper Errors (3 cases)

#### TC-18: No Principal Diagnosis (DRG Error 1)

| Field | Value |
|-------|-------|
| **Case ID** | TC-18 |
| **Department** | Internal Medicine |
| **Patient** | Male, 70 years |
| **PDx** | Empty (no PDx in DIA file) |
| **SDx** | I10, E11.9, J44.1 |
| **Procedure codes** | None |
| **Expected deny reason** | DRG Error Code 1: No Principal Diagnosis. Cannot group DRG without PDx |
| **Deny code** | DRG Error 1 |
| **What was wrong** | DIA file has secondary diagnoses but DXTYPE=1 (PDx) is missing. Likely data entry error |
| **How to fix** | Add PDx to DIA file with DXTYPE=1. The principal diagnosis should be the main condition that prompted admission |
| **Estimated amount** | Entire claim ungroupable: full amount at risk |
| **AI checkpoint** | #1 Basic Data |

---

#### TC-19: PDx invalid for patient sex (DRG Error 5)

| Field | Value |
|-------|-------|
| **Case ID** | TC-19 |
| **Department** | OB/GYN |
| **Patient** | Sex recorded as Male in system (data entry error -- actual female) |
| **PDx** | O80 (Single spontaneous delivery) |
| **SDx** | None |
| **Procedure codes** | 73.59 (Assisted spontaneous delivery) |
| **Expected deny reason** | DRG Error 5: PDx not valid for sex. Obstetric diagnosis O80 cannot be assigned to male patient |
| **Deny code** | DRG Error 5 |
| **What was wrong** | Patient sex recorded incorrectly as Male in IPD file. Sex/diagnosis conflict |
| **How to fix** | Correct sex field in IPD file to Female. Resubmit all 16 files |
| **Estimated amount** | Full delivery claim ungroupable until fixed: ~15,000-25,000 THB |
| **AI checkpoint** | #1 Basic Data, #4 16-File Completeness |

---

#### TC-20: PDx invalid for age (DRG Error 4)

| Field | Value |
|-------|-------|
| **Case ID** | TC-20 |
| **Department** | Pediatrics |
| **Patient** | Age recorded as 45 years (data entry error -- actual 4.5 years) |
| **PDx** | P07.3 (Other preterm infants) |
| **SDx** | P22.0 (Respiratory distress syndrome of newborn) |
| **Procedure codes** | 96.71 (Mechanical ventilation <96 hrs) |
| **Expected deny reason** | DRG Error 4: PDx not valid for age. Neonatal diagnosis P07.3 cannot be assigned to 45-year-old patient |
| **Deny code** | DRG Error 4 |
| **What was wrong** | Date of birth entered incorrectly causing age calculation error. P-codes are only valid for neonatal period |
| **How to fix** | Correct date of birth in patient demographics. Verify age matches neonatal diagnosis codes |
| **Estimated amount** | Full NICU claim ungroupable: ~50,000-200,000 THB depending on LOS and RW |
| **AI checkpoint** | #1 Basic Data |

---

### Category G: CC/MCC Under-coding (3 cases)

#### TC-21: Sepsis not coded as MCC

| Field | Value |
|-------|-------|
| **Case ID** | TC-21 |
| **Department** | ICU |
| **Patient** | Male, 75 years |
| **PDx** | J18.9 (Pneumonia, unspecified) |
| **SDx** | I10, E11.9 (only these two coded) |
| **Procedure codes** | 96.72 (Mechanical ventilation >=96 hrs) |
| **Medical record shows** | Blood culture positive for E. coli, lactate >4, vasopressor use, acute kidney injury |
| **Expected deny reason** | Not denied, but severely underpaid. Missing MCC codes: A41.51 (Sepsis due to E. coli), R65.21 (Severe sepsis with septic shock), N17.9 (AKI), J96.00 (Acute respiratory failure) |
| **DRG impact** | With MCC: RW ~8-12. Without MCC: RW ~3-4. Difference of ~5-8 RW |
| **What was wrong** | Coder only coded the primary condition and basic comorbidities. Failed to capture sepsis, septic shock, AKI, and respiratory failure documented in medical record |
| **How to fix** | Add SDx: A41.51, R65.21, N17.9, J96.00. One MCC is enough to reach highest DRG tier |
| **Estimated amount lost** | ~42,000-67,000 THB (difference of 5-8 RW at 8,350 THB/RW) |
| **AI checkpoint** | #6 CC/MCC Optimization |

---

#### TC-22: Acute heart failure not coded

| Field | Value |
|-------|-------|
| **Case ID** | TC-22 |
| **Department** | Cardiology |
| **Patient** | Female, 72 years |
| **PDx** | I21.4 (NSTEMI) |
| **SDx** | I10, E11.9, E78.5 (only these coded) |
| **Procedure codes** | 36.06, 88.56, 37.22 |
| **Medical record shows** | BNP elevated, pulmonary edema on CXR, required IV furosemide, documented "acute decompensated HF" |
| **Expected deny reason** | Underpayment. Acute systolic HF (I50.21) is an MCC that increases DRG weight |
| **DRG impact** | With MCC: highest tier AMI+PCI DRG. Without: base tier |
| **What was wrong** | Coder missed acute heart failure documented in progress notes and nursing assessment |
| **How to fix** | Add I50.21 (Acute systolic HF) or I50.31 (Acute diastolic HF) as SDx based on documentation |
| **Estimated amount lost** | ~8,000-15,000 THB |
| **AI checkpoint** | #6 CC/MCC Optimization |

---

#### TC-23: CKD Stage 4 not coded (missed MCC)

| Field | Value |
|-------|-------|
| **Case ID** | TC-23 |
| **Department** | Internal Medicine |
| **Patient** | Male, 68 years |
| **PDx** | J44.1 (COPD with acute exacerbation) |
| **SDx** | I10, E11.9 |
| **Procedure codes** | 96.71 (Mechanical ventilation <96 hrs) |
| **Medical record shows** | Creatinine 3.8, eGFR 22, documented "CKD Stage 4" in problem list |
| **Expected deny reason** | Underpayment. N18.4 (CKD Stage 4) is an MCC. Currently only CC-level comorbidities coded |
| **DRG impact** | MCC pushes to higher DRG tier. ~1-2 RW difference |
| **What was wrong** | CKD Stage 4 was in the medical record but not coded as SDx |
| **How to fix** | Add N18.4 as SDx |
| **Estimated amount lost** | ~8,350-16,700 THB |
| **AI checkpoint** | #6 CC/MCC Optimization |

---

### Category H: 16-File / Data Format Errors (3 cases)

#### TC-24: Discharge date before admission date

| Field | Value |
|-------|-------|
| **Case ID** | TC-24 |
| **Department** | Surgery |
| **Patient** | Female, 50 years |
| **PDx** | K35.8 (Acute appendicitis, other and unspecified) |
| **Procedure codes** | 47.09 (Appendectomy) |
| **IPD file** | DATEADM=2026-03-15, DATEDSC=2026-03-12 |
| **Expected deny reason** | Data validation error: discharge date is before admission date. LOS calculation impossible |
| **Deny code** | DRG Error 9 (LOS error) / 16-file validation failure |
| **What was wrong** | Date entry error -- month/day transposed or wrong date entered in IPD file |
| **How to fix** | Correct DATEDSC to actual discharge date (e.g., 2026-03-18). Verify all date fields across 16 files are consistent |
| **Estimated amount** | Full claim rejected until corrected |
| **AI checkpoint** | #4 16-File Completeness |

---

#### TC-25: Wrong fund/insurance type in INS file (C-438)

| Field | Value |
|-------|-------|
| **Case ID** | TC-25 |
| **Department** | Internal Medicine |
| **Patient** | Male, 45 years, SSS (Social Security) right |
| **PDx** | I10 (Essential hypertension) |
| **SDx** | E11.9 |
| **INS file** | INSCL=UCS (should be SSS) |
| **Expected deny reason** | C-438: Insurance type mismatch. Patient's actual right is SSS but claim submitted under UCS fund |
| **Deny code** | C-438 (สิทธิประโยชน์ไม่ตรง) |
| **What was wrong** | Registration staff selected wrong fund type. Patient's current right is Social Security but was coded as UC |
| **How to fix** | Verify patient's current insurance status via NHSO verification system. Update INS file INSCL to correct fund (SSS). Resubmit. For SSS patients, some services must be billed to Social Security Office instead |
| **Estimated amount** | Full claim rejected: ~3,000-5,000 THB |
| **AI checkpoint** | #1 Basic Data, #5 Timing & Authorization |

---

#### TC-26: Incomplete CHA file (missing charge items)

| Field | Value |
|-------|-------|
| **Case ID** | TC-26 |
| **Department** | Surgery |
| **Patient** | Female, 60 years |
| **PDx** | M16.1 (Primary coxarthrosis) |
| **Procedure codes** | 81.51 (Total hip replacement) |
| **CHA file** | Missing Room & Board (category 1), OR fee (category 5), Anesthesia (category 3) |
| **Expected deny reason** | CHA file incomplete. Multiple charge categories missing. DRG may still group but actual cost data is inaccurate |
| **Deny code** | 16-file validation warning / potential audit flag |
| **What was wrong** | HIS export did not capture all charge categories. Incomplete CHA affects cost analysis and may trigger audit |
| **How to fix** | Ensure CHA file has all charge categories: Room & Board, Lab, Radiology, OR fee, Anesthesia, Blood, Supplies, Drugs, etc. Re-export from HIS |
| **Estimated amount** | Not directly denied but audit risk. Hip replacement claim: ~80,000-150,000 THB |
| **AI checkpoint** | #4 16-File Completeness |

---

### Category I: Specialty-Specific Deny Cases (4 cases)

#### TC-27: ODS claim with LOS > 24 hours

| Field | Value |
|-------|-------|
| **Case ID** | TC-27 |
| **Department** | Day Surgery |
| **Patient** | Male, 55 years |
| **PDx** | K80.2 (Calculus of gallbladder without cholecystitis) |
| **Procedure codes** | 51.23 (Laparoscopic cholecystectomy) |
| **Claim type** | ODS (One Day Surgery) |
| **Admission** | 2026-02-10 08:00 |
| **Discharge** | 2026-02-11 14:00 (LOS = 30 hours) |
| **Expected deny reason** | ODS requires LOS 2-24 hours. This case exceeds 24 hours. Must be claimed as regular IPD |
| **Deny code** | ODS eligibility failure |
| **What was wrong** | Patient had post-op complication (nausea/vomiting) requiring extended observation beyond 24 hrs. Should have been reclassified from ODS to regular IPD |
| **How to fix** | Reclassify claim as regular IPD. Document complication as SDx if applicable (e.g., T81.x post-procedural complication) |
| **Estimated amount impact** | ODS payment formula differs from regular IPD DRG. May result in higher or lower payment depending on case |
| **AI checkpoint** | #4 16-File Completeness (LOS check) |

---

#### TC-28: Dialysis session exceeds monthly limit

| Field | Value |
|-------|-------|
| **Case ID** | TC-28 |
| **Department** | Nephrology (HD unit) |
| **Patient** | Male, 65 years |
| **PDx** | N18.5 (CKD Stage 5/ESRD) |
| **Procedure codes** | 39.95 (Hemodialysis) x 15 sessions in one month |
| **Expected deny reason** | Temporary HD limited to max 3 sessions/week. 15 sessions in one month exceeds the standard. Sessions 14-15 denied |
| **Deny code** | Session limit exceeded |
| **What was wrong** | Hospital scheduled 15 HD sessions in the month but standard is max 13 sessions/month (3/week). Two extra sessions need clinical justification |
| **How to fix** | For sessions exceeding limit, provide clinical justification (e.g., fluid overload, hyperkalemia). Document medical necessity. Some extra sessions may be approved on appeal |
| **Estimated amount** | 2 sessions denied: ~3,000-4,000 THB (1,500 THB/session x 2) |
| **AI checkpoint** | #2 Dx-Proc Match (session limit check) |

---

#### TC-29: Cancer chemo -- protocol mismatch

| Field | Value |
|-------|-------|
| **Case ID** | TC-29 |
| **Department** | Oncology |
| **Patient** | Male, 60 years |
| **PDx** | C18.0 (Malignant neoplasm of cecum) |
| **SDx** | None additional |
| **Procedure codes** | 99.25 (Injection of cancer chemotherapeutic substance) |
| **Regimen** | FOLFOX but cycle number not documented, cumulative dose missing |
| **Expected deny reason** | Protocol compliance issue: (1) No cycle tracking documentation (2) Regimen code not recorded in e-Claim (3) Cumulative dose not tracked (4) Diagnosis C18.0 needs TNM staging documented |
| **Deny code** | Protocol mismatch / documentation incomplete |
| **What was wrong** | (1) Coder did not record NHSO chemo protocol/regimen code (2) Cycle number absent (3) TNM staging not in structured data (4) Cumulative dose tracking missing |
| **How to fix** | Add regimen code per NHSO 20-protocol list. Record cycle number (e.g., FOLFOX cycle 3 of 12). Document TNM staging. Track and record cumulative dose |
| **Estimated amount** | Chemo claim: ~30,000-80,000 THB per cycle at risk |
| **AI checkpoint** | #2 Dx-Proc Match, #3 Device Documentation (chemo drugs) |

---

#### TC-30: ER case - wrong project code (UC instead of UCEP)

| Field | Value |
|-------|-------|
| **Case ID** | TC-30 |
| **Department** | Emergency |
| **Patient** | Female, 48 years, UC right but registered at different hospital |
| **PDx** | I63.9 (Cerebral infarction, unspecified) |
| **SDx** | I10, E11.9 |
| **Procedure codes** | 99.10 (Thrombolytic therapy) |
| **Project code** | UC (should be UCEP) |
| **Expected deny reason** | Patient is UC but not registered at this hospital. Presented as emergency stroke. Should use UCEP project code for emergency patients treated at non-registered facility |
| **Deny code** | C-438 or equivalent -- wrong project/fund code |
| **What was wrong** | Registration used standard UC project code instead of UCEP (Universal Coverage Emergency Patients). UCEP allows emergency treatment at any facility for first 72 hours |
| **How to fix** | Change project code to UCEP. Ensure triage documentation supports emergency classification. Stroke with thrombolytic therapy qualifies as emergency |
| **Estimated amount** | Full stroke claim: ~49,000-80,000 THB |
| **AI checkpoint** | #1 Basic Data, #5 Timing & Authorization |

---

## Statistical Reference Data

### Top Deny Reasons by Frequency (Estimated from NHSO patterns)

| Rank | Deny Reason | Estimated % of All Denials | Typical Departments |
|------|------------|---------------------------|---------------------|
| 1 | W305/C30: No identity verification (ไม่ปิดสิทธิ์) | 25-30% | All departments |
| 2 | Drug/Lab Catalog Mismatch | 15-20% | Pharmacy, Lab-heavy departments |
| 3 | ADP Device Code Mismatch | 10-15% | Cath Lab, OR, Ortho |
| 4 | Late Submission (>30 days) | 8-12% | All departments |
| 5 | C-438: Wrong fund/right type | 8-10% | All departments (registration error) |
| 6 | DRG Grouper Error (Error 1-9) | 5-8% | All IPD |
| 7 | Dx-Procedure Mismatch | 5-7% | Cath Lab, OR, Chemo |
| 8 | CC/MCC Under-coding (underpayment) | 5-7% | ICU, Cath Lab, Complex medical |
| 9 | Protocol/Documentation Incomplete | 3-5% | Chemo, Dialysis, Special procedures |
| 10 | Session/Visit Limit Exceeded | 2-3% | Dialysis, Rehab, Innovation units |

### Deny Rates by Department (Estimated)

| Department | Estimated Deny Rate | Primary Deny Causes |
|-----------|-------------------|-------------------|
| Cath Lab | 8-15% | Dx-Proc mismatch, ADP errors, documentation |
| Orthopedics | 6-12% | Implant code mismatch, PA not obtained for TKA <55 |
| Oncology (Chemo) | 5-10% | Protocol mismatch, drug not in Fee Schedule |
| Nephrology (Dialysis) | 4-8% | Session limits, Authen per session, duplicate claims |
| ICU/NICU | 3-7% | CC/MCC under-coding, ventilator day mismatch |
| ER/UCEP | 5-10% | Wrong project code, triage documentation, 72-hr window |
| General Surgery | 3-6% | Late submission, 16-file errors, implant documentation |
| Internal Medicine | 2-5% | CC/MCC under-coding, Authen code issues |
| ODS/MIS | 3-7% | LOS violations, not in approved procedure list |
| Innovation Units | 10-20% | Quota exceeded, Face Recognition failures, C error from cap limits |

### Average Amounts Denied (Estimated by Category)

| Deny Category | Average Amount per Case (THB) | Range (THB) |
|--------------|------------------------------|-------------|
| Full claim deny (W305/C30) | 35,000 | 5,000 - 200,000 |
| Dx-Proc mismatch (underpayment) | 15,000 | 5,000 - 50,000 |
| Device/implant deny | 50,000 | 10,000 - 200,000 |
| Drug catalog mismatch | 3,000 | 500 - 100,000 |
| CC/MCC under-coding (revenue loss) | 12,000 | 5,000 - 70,000 |
| Late submission penalty | 5,000 | 1,000 - 30,000 |
| DRG grouper error (full deny) | 30,000 | 5,000 - 200,000 |

### Appeal Success Rates (Estimated)

| Deny Type | Appeal Success Rate | Notes |
|-----------|-------------------|-------|
| W305 (identity verification) | 60-70% | If filed within 10 days with documentation |
| ADP device mismatch | 70-80% | If corrected data + sticker/barcode provided |
| Drug catalog mismatch | 80-90% | Usually remapping issue, easily corrected |
| DRG grouper error (data fix) | 85-95% | Fix data and resubmit |
| Dx-Proc mismatch | 50-60% | Requires medical record review |
| Late submission | 10-20% | Strict deadline, rarely waived |
| Protocol mismatch (chemo) | 40-50% | Requires protocol justification |

---

## C-Code / Deny Code Reference

### Legacy C-Codes (being phased out for UC in FY2569)

| C-Code | Description (Thai) | Description (English) | Severity |
|--------|-------------------|----------------------|----------|
| C-438 | สิทธิประโยชน์ไม่ตรง | Benefit/fund type mismatch | Full deny |
| C-474 | ไม่มีเลข PA หรือ PA ไม่ตรง | No PA number or PA mismatch | Item deny |
| C-555 | OP REFER ข้อมูลไม่ตรง | OP Refer data mismatch | Full deny |
| C-825 | เบิกอุปกรณ์เกินจำนวน | Device claim exceeds quantity | Item deny (0 THB) |
| C30 | ไม่ปิดสิทธิ์ | No identity verification | Full deny |

### New FY2569 Codes (Zero C system)

| Code | Description | Action |
|------|------------|--------|
| W305 | ไม่พบการปิดสิทธิ์ (replaces C30) | Appeal within 10 days via SMCS |
| G47 | ไม่พบ CAG/PCI Data Form | Submit Data Form before claim |
| V993 | Data Form ไม่ผ่านข้อบ่งชี้ | Hold payment pending review |
| Deny 305 | W305 ไม่ได้อุทธรณ์ในเวลา | Payment = 0 THB (final) |
| W74/W75 | Auditor review required (กทม.) | Additional audit step after W305 appeal |

### DRG Error Codes

| Error | Meaning | Fix |
|-------|---------|-----|
| 1 | No Principal Diagnosis | Add PDx to DIA file (DXTYPE=1) |
| 2 | Invalid PDx code | Check ICD-10-TM validity |
| 3 | Unacceptable PDx | Some codes not allowed as PDx |
| 4 | PDx invalid for age | Verify patient age / DOB |
| 5 | PDx invalid for sex | Verify patient sex |
| 7 | Ungroupable (sex error) | Fix sex data |
| 8 | Ungroupable (discharge type) | Fix discharge type code |
| 9 | LOS error | Fix admission/discharge dates |

---

## DRG Error Code Reference

### Error Code Decision Tree

```
Claim submitted
    ├── PDx present?
    │   ├── No → Error 1 (No PDx)
    │   └── Yes → Valid ICD-10?
    │       ├── No → Error 2 (Invalid PDx)
    │       └── Yes → Acceptable as PDx?
    │           ├── No → Error 3 (Unacceptable PDx)
    │           └── Yes → Age compatible?
    │               ├── No → Error 4 (Age invalid)
    │               └── Yes → Sex compatible?
    │                   ├── No → Error 5 (Sex invalid)
    │                   └── Yes → D/C type valid?
    │                       ├── No → Error 8 (D/C type)
    │                       └── Yes → LOS valid?
    │                           ├── No → Error 9 (LOS)
    │                           └── Yes → ✅ Groups to DRG
```

---

## Sources & Methodology

### Primary Sources

1. **NHSO Official Rules (nhso-rules/)** -- Core rules, deny-fixes, department-specific validation rules extracted from NHSO publications
2. **NHSO YouTube Channel (@nhsothailand)** -- 96+ videos indexed, 5 fully analyzed:
   - `zSUuHM9Y2Vk` -- FY2569 policy changes (6.5 hrs) -- Zero C, W305, new services
   - `v9ZPwJhBqoc` -- Innovation unit billing changes (3.8 hrs) -- Global Budget, Face Recognition
   - `jKE0lh9BMak` -- Fund management FY2569 morning session (2.6 hrs) -- Budget, Base Rate
   - `4tVbQzkux7Y` -- Fund management FY2569 afternoon session (2.4 hrs) -- LTC, audit changes
   - `R_g1VNkQ65w` -- Nursing clinic billing (3.2 hrs) -- AM Care Plus, claim process
3. **e-Claim System Guide** -- From NHSO Region 7 Khon Kaen, covering system workflow, 16-file specification, error codes
4. **Q&A Series "ตอบทุกข้อสงสัยการเบิกจ่าย"** -- 93 episodes of live Q&A between NHSO and healthcare providers (indexed but not yet transcribed)

### Methodology

- Test cases are constructed from **real deny patterns** documented in NHSO official materials
- ICD-10 codes, ICD-9-CM codes, and deny reasons are based on **Thai DRG v6.3.3** grouper logic
- Amount estimates use **FY2569 Base Rate of 8,350 THB/Adj.RW** for in-network IP claims
- Deny rates and statistics are **estimated** from patterns across NHSO publications and training materials; exact hospital-level data requires access to individual hospital reports
- All C-codes and deny codes are from **official NHSO documentation** and e-Claim system specifications

### Limitations

- Individual hospital deny rate data is confidential and not publicly available
- Exact financial amounts vary by DRG group, RW, and LOS
- FY2569 introduced Zero C system for UC -- some C-codes are being replaced by new denial mechanism
- Research papers on Thai DRG deny rates exist but require institutional access (HSRI, ThaiJO databases)

### Recommended Additional Data Collection

To strengthen this test dataset, the following sources should be pursued:

1. **Hospital's own deny report** from e-Claim REP files -- contains actual deny codes and amounts
2. **PPFS audit results** -- specific cases flagged by NHSO auditors
3. **SLE Audit findings** -- electronic audit results from new system
4. **สปสช. ตอบทุกข้อสงสัย Q&A series** (episodes 84-93) -- real questions from providers about specific deny cases
5. **HSRI research papers** at https://kb.hsri.or.th -- academic studies on Thai hospital claim denial patterns
6. **ThaiJO (Thai Journals Online)** -- published research on DRG audit and medical coding accuracy in Thai hospitals
7. **Facebook groups**: "สปสช. เบิกจ่าย" and hospital billing officer communities for real-world case discussions
