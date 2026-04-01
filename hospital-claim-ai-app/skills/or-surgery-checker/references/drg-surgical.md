# Surgical DRG Optimization

## Key Principle
Surgical DRG weight สูงกว่า Medical DRG อย่างมาก
→ ถ้าทำ OR procedure ต้อง code ให้เป็น Surgical DRG

## Post-op Complications = CC/MCC (code ถ้ามี documentation)
| Complication | ICD-10 | CC/MCC | RW Impact |
|-------------|--------|--------|-----------|
| Surgical Site Infection | T81.4 | CC | +0.2-0.5 |
| Deep Vein Thrombosis | I82.4x | MCC | +0.5-1.5 |
| Pulmonary Embolism | I26.x | MCC | +1.0-2.0 |
| Wound Dehiscence | T81.3 | CC | +0.2-0.4 |
| Post-op Hemorrhage | T81.0 | CC | +0.3-0.5 |
| Acute Kidney Injury | N17.x | MCC | +0.5-1.0 |
| Respiratory Failure | J96.0x | MCC | +1.0-2.0 |
| Sepsis | A41.x | MCC | +1.5-3.0 |

## Bilateral Procedure Optimization
- Bilateral = extension code → separate RW calculation
- Example: Bilateral TKR > 2x unilateral TKR (due to complexity)

## Procedure Sequencing Rules
1. Main procedure (highest RW determinant) FIRST
2. Secondary procedures in order of clinical significance
3. Anesthesia code last
4. Extension codes attached to their parent procedure
