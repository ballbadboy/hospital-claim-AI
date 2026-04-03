# CAG Data Form — Field Reference

> แบบฟอร์มบันทึกข้อมูลหัตถการสวนหัวใจ ห้องสวนหัวใจ รพ.พญาไทศรีราชา
> ใช้ตรวจสอบความครบถ้วนของเอกสารก่อนส่ง claim + V993 Pre-Auth

---

## A. General Information (ข้อมูลทั่วไป)

| Field | ตัวอย่าง | จำเป็น | ใช้ใน |
|-------|---------|--------|-------|
| HCODE | 11855 | Yes | claim, V993 |
| PID (เลข 13 หลัก) | 3200800029197 | Yes | claim, V993 |
| วัน/เดือน/ปีเกิด | 04/04/1950 | Yes | age calc |
| เพศ | ชาย/หญิง | Yes | DRG |
| Race | ไทย | No | - |
| Admission Date | 05/05/2568 | Yes | claim, LOS |

---

## B. History & Risk Factors (ประวัติ + ปัจจัยเสี่ยง)

| Field | Type | ใช้ใน CC/MCC |
|-------|------|-------------|
| Height / Weight / BMI | ตัวเลข | Obesity E66.x (Asian BMI) |
| Cerebrovascular disease | Yes/No | SDx I69.x |
| Peripheral arterial disease | Yes/No | SDx I73.9 |
| Hypertension | Yes/No | I10 (ไม่มีผลต่อ RW) |
| Dyslipidemia + LDL/HDL | Yes/No + ค่า | E78.5 (ไม่มีผลต่อ RW) |
| DM | Yes/No | E11.x = CC |
| Current/Recent smoker | Yes/No | F17.2 |
| Prior MI | Yes/No | I25.2 |
| Aortic disease | Yes/No | SDx |
| Familial Hx premature CVD | Yes/No | - |

**ตรวจ CC/MCC:** ถ้า DM = Yes ต้องมี E11.x ใน SDx, ถ้า BMI ≥35 ต้องมี E66.8

---

## C. Clinical Indication (ข้อบ่งชี้ — 6 ประเภท)

### C1: CCS (Chronic Coronary Syndromes)
- **กลุ่ม CCS** (5 ตัวเลือก): suspicious CAD, new onset HF, >1yr post-diagnosis, vasospasm, screening
- **Indication for CAG:**
  - Improve symptoms (medically refractory) — ต้องระบุยาที่ใช้ (antiplatelet, beta blocker, CCB, nitrate, statin, ACEI/ARB, etc.)
  - Improve survival (high risk) — HF within 2wks, low EF, +ve EST, large ischemia, VT/VF
- **Indication for PCI:** 10 ตัวเลือก — สำคัญ: significant proximal LAD, ≥1 CAD >70% หรือ FFR <0.80
- **V993 จุดเสี่ยง:** CCS ที่ไม่มี functional test / FFR → สปสช. deny

### C2: NSTE-ACS (UA / NSTEMI)
- **Diagnostic key:** ischemic pain, ischemic ECG, biomarker elevation (1st/2nd), R/O non-ACS, LVEF
- **Risk stratification:**
  - Very high: shock/HF/hypotension/VT/VF
  - High: GRACE >140
  - Intermediate-Low: GRACE <140
- **Revascularization guideline:** 7 ตัวเลือก — สำคัญ: shock ห้าม routine multivessel PCI
- **V993 จุดเสี่ยง:** multivessel PCI ใน shock → deny

### C3: STE-ACS (STEMI)
- **Diagnostic key:** ischemic pain, ECG STE (anterior/lateral/inferior/RV), biomarker, R/O (dissection/PE/myopericarditis/Takotsubo)
- **Risk:** Very high (shock/VT-VF/3rd AVB) → High → Intermediate → Low
- **Reperfusion:** PCI if FMC-to-wire <120min, fibrinolysis if >120min, rescue PCI
- **Revascularization:** 11 ตัวเลือก — สำคัญ: asymptomatic occluded >24hr ห้ามทำ PCI
- **V993 จุดเสี่ยง:** ไม่มี ECG STE / door-to-balloon >120min

### C4: CMP / CHF (Cardiomyopathy / Heart Failure)
- **Type:** Dilated, Hypertrophic, Restrictive, Takotsubo, ARVC, Other
- **Investigation:** ischemic ECG, Echo (LVEF), MRI, EST, CTA
- **Plan after CAG:** Heart Team → Medical Rx / CABG / PCI

### C5: Pre-operative Assessment of CAD
- **Diagnosis:** Hx of CAD, Valvular HD, Congenital HD, Pre/post transplant
- **Investigation:** เหมือน C4
- **Plan after CAG:** Heart Team → Medical Rx / CABG / PCI

### C6: Post Cardiac Arrest
- **STE:** With STE → immediate CAG / Without STE → delayed/selective strategy
- **Plan after CAG:** Heart Team → Medical Rx / CABG / PCI

---

## I. CAG Procedure (หัตถการ CAG)

| Field | Type | จำเป็น V993 |
|-------|------|------------|
| Date of CAG | วันที่ (≥ Admission Date) | Yes |
| Pre-CAG Risk | very high/high/intermediate/low | Yes |
| Risk reduction intervention | Yes/No | No |
| Responsible Physician + ว. | ชื่อ + เลขที่ใบอนุญาต | Yes |
| Filler person | Physician / RN / Technician | No |
| Access site | femoral/radial/brachial/other | No |
| **Lesions** | 1-vv / 2-vv / 3-vv / LM / non-obstructive | **Yes** |
| **% stenosis per location** | Gensini: 1-25/26-50/51-75/76-90/91-99/100% | **Yes** |
| Complications | death/stroke/ARF/allergic/hematoma/perforation/dissection/ACS/shock/arrest/bleeding | Yes |

**V993 ตรวจ:** stenosis ≤75% + ไม่มี FFR → deny PCI

---

## II. PCI Procedure (หัตถการ PCI)

### Target Arteries (5 เส้น)
| Artery | Segments |
|--------|---------|
| LM | Left Main |
| LAD/DG | Left Anterior Descending / Diagonal |
| Cx/OM | Circumflex / Obtuse Marginal |
| Trifurcation | จุดแยก 3 เส้น |
| RCA/PDA | Right Coronary / Posterior Descending |

### Per Artery Fields
| Field | Type | จำเป็น V993 |
|-------|------|------------|
| Previous PCI | Yes/No + segment | No |
| Previous Stent | BMS/DES + date + ISR/thrombosis | No |
| **Baseline stenosis** | Gensini range (%) | **Yes** |
| Measurement method | visual estimate / QCA | Yes (QCA preferred) |
| **Lesion type** | A / B1 / B2 / C | **Yes** |
| Pre-PCI TIMI | 0/1/2/3 | Yes |
| **SYNTAX Score** | low (0-22) / intermediate (23-32) / high (>33) | **Yes** |
| **Stent used** | ชื่อ + size + BMS/DES | **Yes** |
| Final stenosis | Gensini range (%) | Yes |
| Final TIMI | 0/1/2/3 | Yes |

### PCI Complications
เหมือน CAG + no reflow, ACS (STE/NSTE), shock, bradycardic arrest

---

## Checklist ตรวจสอบก่อนส่ง V993

| # | ตรวจ | เกณฑ์ผ่าน |
|---|------|----------|
| 1 | Stenosis ≥70% | ถ้า 50-70% ต้องมี FFR <0.80 |
| 2 | SYNTAX score | ≤33 → PCI OK, >33 → ต้อง Heart Team note |
| 3 | Indication ตรง type | C1→CCS, C2→NSTE-ACS, C3→STEMI, C4→CMP |
| 4 | CAG date ≥ Admission date | วันที่ต้องไม่ก่อน admit |
| 5 | Physician มี ว. | เลขที่ใบอนุญาตครบ |
| 6 | Shock + multivessel | ห้าม routine multivessel PCI ใน same setting |
| 7 | STEMI timing | FMC-to-wire <120min documented |
| 8 | Stent info | ชื่อ+size+type ครบ |
