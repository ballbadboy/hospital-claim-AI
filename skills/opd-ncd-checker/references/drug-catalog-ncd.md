# NCD Drug Catalog — Common GPUID Issues
| Drug | Class | Common Issue |
|------|-------|-------------|
| Metformin 500/850/1000 | DM | Brand vs generic GPUID |
| Glipizide | DM | Formulation mismatch |
| Amlodipine 5/10 | HT | Brand-specific GPUID |
| Enalapril | HT | Dose form mismatch |
| Losartan | HT | Different GPUID per strength |
| Atorvastatin | Lipid | Original vs generic |
| Salbutamol inhaler | COPD/Asthma | Brand GPUID |
| Budesonide inhaler | COPD/Asthma | Brand GPUID |

## Key Rule
- Drug Catalog version เปลี่ยน → ต้อง remap ใน HIS ทุกครั้ง
- GPUID ต้อง exact match (ไม่ใช่ชื่อยา match)
