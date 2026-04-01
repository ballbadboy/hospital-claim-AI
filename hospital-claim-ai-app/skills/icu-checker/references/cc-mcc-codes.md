# Critical CC/MCC Codes for ICU Claims

## MCC (Major Complication/Comorbidity) — highest RW impact
| ICD-10 | Description | Common in |
|--------|-------------|-----------|
| J96.00-02 | Acute respiratory failure | All ICU |
| R65.20 | Severe sepsis w/o shock | Medical ICU |
| R65.21 | Severe sepsis WITH shock | Medical ICU |
| A41.01 | Sepsis due to MRSA | All ICU |
| A41.9 | Sepsis, unspecified | All ICU |
| I46.2/9 | Cardiac arrest | CCU |
| G93.1 | Anoxic brain injury | Post-arrest |
| N17.0-9 | Acute kidney injury | All ICU |
| K72.00 | Acute hepatic failure | Medical ICU |
| E11.10 | DM2 with ketoacidosis | Medical ICU |
| J80 | ARDS | All ICU |

## CC (Complication/Comorbidity) — moderate RW impact
| ICD-10 | Description |
|--------|-------------|
| E87.0 | Hyperosmolality |
| E87.1 | Hyponatremia |
| E87.6 | Hypokalemia |
| I48.x | Atrial fibrillation |
| J18.9 | Pneumonia, unspecified |
| N39.0 | UTI |
| L89.x | Pressure ulcer |
| D62 | Acute posthemorrhagic anemia |

## Optimization Rule
1. ตรวจ medical record ว่ามี condition ไหนที่ document แล้วแต่ยังไม่ได้ code
2. เพิ่ม CC/MCC codes → DRG weight เพิ่มขึ้น
3. ต้องมี documentation support (ห้ามเพิ่ม code โดยไม่มีหลักฐาน)
