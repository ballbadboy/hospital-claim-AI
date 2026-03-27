# Dialysis Drug Catalog

## EPO (Erythropoietin)
| Drug | Route | GPUID Check |
|------|-------|-------------|
| Epoetin alfa | SC/IV | Match exact brand GPUID |
| Epoetin beta | SC/IV | Match exact brand GPUID |
| Darbepoetin | SC | Match exact brand GPUID |

## IV Iron
| Drug | Route | Notes |
|------|-------|-------|
| Iron Sucrose (Venofer) | IV | Most common |
| Ferric Carboxymaltose | IV | Higher dose per session |

## Anticoagulation
| Drug | Notes |
|------|-------|
| Unfractionated Heparin | Standard for HD |
| LMWH (Enoxaparin) | Alternative |
| Heparin-free | Document allergy/HIT |

## Common GPUID Mismatch Issues
- Version change ใน Drug Catalog → ต้อง remap ใน HIS
- Brand-specific GPUID ≠ generic GPUID
- Dose form mismatch (prefilled syringe vs vial)
