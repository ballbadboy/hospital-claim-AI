# Batch Processing Guide

## Expected CSV Format
| Column | Required | Description |
|--------|----------|-------------|
| HN | Yes | Hospital Number |
| AN | Yes | Admission Number |
| PDx | Yes | Principal Diagnosis (ICD-10) |
| SDx | No | Secondary Dx (comma-separated) |
| Procedures | No | ICD-9-CM (comma-separated) |
| DRG | No | Current DRG code |
| RW | No | Current Relative Weight |
| Department | No | Department name |
| LOS | No | Length of Stay |
| Charge | No | Charge amount |

## Processing Steps
1. Parse CSV → validate columns
2. For each row: check Dx-Proc match, CC/MCC completeness
3. Calculate potential RW improvement
4. Score by money impact: ΔRW × Base Rate (฿8,350)
5. Sort descending by money impact
