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

## CC/MCC Optimizer

### ทุกเคส IPD ต้องตรวจ comorbidities

**MCC (Major CC) — เพิ่ม RW 20-40%:**
| Code | Description |
|------|-------------|
| A41.x | Sepsis (ระบุ organism) |
| R65.2x | Severe sepsis |
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
