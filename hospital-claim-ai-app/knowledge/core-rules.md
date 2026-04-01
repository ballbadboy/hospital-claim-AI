# Core Rules — อ่านทุกครั้งที่ตรวจเคส

## Thai DRG v6.3.3 Grouping

### Flow: PDx → MDC → OR check → PDC → DC → DRG → PCCL → final RW

### MDC ที่พบ deny บ่อย
| MDC | System | Departments |
|-----|--------|-------------|
| 05 | Circulatory | Cath Lab, Cardiac surgery |
| 08 | Musculoskeletal | Ortho OR (hip/knee) |
| 11 | Kidney/Urinary | Dialysis, Urology |
| 17 | Myeloproliferative | Chemo, Hematology |
| 04 | Respiratory | ICU, Ventilator |
| Pre-MDC | Special | Transplant, Tracheostomy, ECMO |

### DRG Error Codes
| Error | Meaning | Fix |
|-------|---------|-----|
| 1 | No PDx | Add PDx to DIA file |
| 2 | Invalid PDx | Fix ICD-10 code |
| 3 | Unacceptable PDx | Use valid PDx |
| 4 | PDx invalid for age | Check age |
| 5 | PDx invalid for sex | Check sex |
| 7 | Ungroupable (sex) | Fix sex data |
| 8 | Ungroupable (D/C) | Fix discharge type |
| 9 | LOS error | Fix dates |

### LOS Adjustment
- LOS < Trim Low → RW reduced
- Trim Low ≤ LOS ≤ Trim High → base RW
- LOS > Trim High → RW increased (per diem)

---

## FDH 16-File Validation

### Required Fields (ทุก department)
| File | Key Fields | Common Error |
|------|-----------|-------------|
| IPD | AN, DATEADM, DATEDSC, DISCHT, WARD | Date format, D/C < ADM |
| DIA | DIAG (ICD-10), DXTYPE (1=PDx) | Invalid code, no PDx |
| OPR | OPCODE (ICD-9-CM), DATEOP, OPTYPE | Invalid code, date out of range |
| ADP | TYPE (3-5), CODE, QTY, RATE, SERIALNO | Code mismatch, qty wrong |
| DRU | DID (GPUID), AMOUNT | Drug catalog mismatch |
| CHA | CHRGITEM, AMOUNT | Missing items |
| INS | INSCL (สิทธิ) | Wrong fund |

### Timing
- ≤24 hrs after D/C = **fast track** (สปสช. จ่ายใน 72 ชม.)
- ≤30 days = normal (IPD จ่ายใน 30 วัน)
- >30 days = **penalty** (ลดอัตราจ่าย)

### ADP TYPE by Department
| Department | TYPE | Items |
|-----------|------|-------|
| Cath Lab | 5 | Stent, balloon, guidewire |
| OR | 4-5 | Implants, plates, screws |
| Chemo | 3 | Chemo drugs (if not in DRU) |
| Dialysis | 3 | Dialyzer, tubing |
| ICU | 3-5 | ECMO, IABP, temp pacemaker |

---

## Standard Coding Guidelines 2026 (กฎใหม่)

> อ้างอิง: `references/nhso-rules/standard-coding-guidelines-2026.md` (53 ข้อ ฉบับเต็ม)

### กฎสำคัญที่มีผลต่อ DRG/Claim

| ข้อ | กฎ | ผลกระทบ |
|-----|---|--------|
| 1 | **R65 (SIRS) เลิกใช้** | ห้ามใช้ R65 เป็น SDx |
| 2 | **Sepsis (A41.9) ห้ามเป็น PDx** → ใช้ organ infection เป็น PDx | PDx ผิด = DRG ผิดทั้งเคส |
| 2 | Septic shock (R57.2) เป็น PDx ได้เฉพาะไม่พบ source | ปกติต้องเป็น SDx |
| 4 | Viral hepatitis **เป็นโรคร่วมได้** ถึงไม่รักษาก็ลง code ได้ | เพิ่ม CC |
| 14 | DIC ต้อง ISTH score ≥5 ถึง code D65 ได้ | ไม่ถึงเกณฑ์ → D69.5 + D68.4 |
| 15 | DM foot: ต้องระบุ neuropathy (E11.4) / PVD (E11.5) / both (E11.7) | specific code = RW สูงกว่า E11.9 |
| 19 | Obesity ใช้ **Asian BMI**: Class I ≥25, Class II ≥30, Class III ≥35 | Class III (E66.8) = CC |
| 20 | Electrolyte: ลง code เฉพาะ severe (Na<120, K<2.5, Mg<0.5) | ไม่ severe = ห้ามลง |
| 25 | STEMI I21.0-3, NSTEMI I21.4, Subsequent MI I22 | specific = RW สูงกว่า I21.9 |
| 26 | Ischemic cardiomyopathy I25.5: LVEF <40% + stenosis criteria | ได้ CC |
| 30 | Cardiac arrest: สาเหตุ = PDx, I46.0 = SDx | ลง PDx ผิด = DRG ผิด |
| 32 | Heart failure ต้องระบุ EF (HFpEF/HFmrEF/HFrEF) | specific = RW สูงกว่า I50.9 |
| 33 | Stroke ต้องระบุ embolism/thrombosis + territory (G46.*) | specific = RW สูงกว่า I64 |
| 38 | **COPD exacerbation J44.1 = MCC** | เพิ่ม RW 20-40%! |
| 42 | Respiratory failure: วินิจฉัยได้แม้ O2 sat ปกติ (ถ้า intubate) | J96.0x = MCC |
| 43 | Gastritis **ต้องมี endoscopy** ถ้าไม่ scope → dyspepsia | Gastritis without scope = audit risk |
| 51 | AKI prerenal → **R39.2 ไม่ใช่ N17** | N17 = MCC, R39.2 = ไม่ใช่ |
| 52 | **CKD 4-5 บังคับลงรหัสทุก IP** | N18.4 = MCC! เสียโอกาสถ้าไม่ลง |

---

## CC/MCC Optimizer

### ทุกเคส IPD ต้องตรวจ comorbidities

**MCC (Major CC) — เพิ่ม RW 20-40%:**
| Code | Description |
|------|-------------|
| A41.x | Sepsis (ระบุ organism) — **ต้องเป็น SDx ไม่ใช่ PDx (SCG 2026 ข้อ 2)** |
| ~~R65.2x~~ | ~~Severe sepsis~~ — **เลิกใช้แล้ว (SCG 2026 ข้อ 1)** |
| J96.0x | Acute respiratory failure |
| N17.x | Acute kidney injury |
| I50.2x | Acute systolic HF |
| I50.3x | Acute diastolic HF |
| N18.4 | CKD stage 4 |
| J44.1 | COPD acute exacerbation |

**CC — เพิ่ม RW 5-15%:**
| Code | Description |
|------|-------------|
| E11.x | DM type 2 |
| N18.3 | CKD stage 3 |
| I48.x | Atrial fibrillation |
| E87.x | Electrolyte disorders |
| D64.x | Anemia |

**ไม่มีผลต่อ RW:**
| Code | Description |
|------|-------------|
| I10 | Essential hypertension |
| E78.5 | Dyslipidemia |

**กฎ:** MCC 1 ตัว = RW สูงสุดในกลุ่มแล้ว (ไม่ต้อง stack)
**CC Exclusion:** บาง SDx ถูกตัดจาก CC เมื่อเกี่ยวกับ PDx → ตรวจ Appendix F2

---

## C-Code Errors & Fixes
| C-Code | Problem | Fix |
|--------|---------|-----|
| C-438 | สิทธิไม่ตรง | Check fund type + project code |
| Drug mismatch | DRU ≠ Drug Catalog | Remap GPUID |
| Lab mismatch | Lab ≠ Lab Catalog | Remap lab codes |
| ADP error | Device code/qty wrong | Match Fee Schedule + GPO |
| DRG pending | Data incomplete | Check all 16 files |
| Authen missing | No Authen Code | Verify before D/C |
| Late submission | >30 days | ต้องมี alert system |
