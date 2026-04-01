# OR Surgery Module

## Key Deny Causes
1. **Multiple procedure bundling** — code sequence matters, main procedure first
2. **Extension code errors** — ICD-9-CM + 2-digit extension (position+count)
3. **Implant mismatch** — prosthesis ไม่ตรง ADP file + GPO record
4. **OPTYPE wrong** — Major OR(1) vs Minor OR(2) vs Non-OR(3)
5. **Anesthesia coding** — GA/regional ต้อง code แยก

## High-Value Implants
| Category | Items | ADP TYPE | Cost Range |
|----------|-------|----------|-----------|
| Ortho | Total hip/knee, plates, screws | 4-5 | 50-200K |
| Spine | Pedicle screws, cages, rods | 4-5 | 100-500K |
| General | Mesh (hernia), stapler | 3-4 | 5-50K |
| Vascular | Graft, stent (non-coronary) | 5 | 30-150K |
| Neuro | VP shunt, DBS lead | 5 | 50-300K |

## Procedure Code Families
| ICD-9-CM | Category |
|----------|----------|
| 77-84 | Musculoskeletal (ortho) |
| 01-05 | Nervous system (neuro) |
| 42-54 | Digestive (GI surgery) |
| 55-59 | Urinary system |
| 65-71 | Female genital (OB/GYN) |
| 38-39 | Vascular |

## DRG Optimization
- Surgical DRG weight >> Medical → ensure OR procedure coded correctly
- Post-op complications (SSI T81.4, DVT I82.4, PE I26.x) = MCC → code if documented
- Bilateral procedures: extension code = higher RW
- Main procedure sequenced first determines primary DRG group

## Documentation Checklist
- [ ] Operative note (detailed procedure description)
- [ ] Anesthesia record
- [ ] Implant details (type, size, manufacturer, lot, qty)
- [ ] Indication for surgery documented
- [ ] Consent form
- [ ] Post-op complications documented if any
