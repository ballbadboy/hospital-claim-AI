---
name: smart-coder
description: "แปลง clinical notes ภาษาไทย/อังกฤษ เป็น ICD-10-TM + ICD-9-CM อัตโนมัติ — AI อ่าน notes แนะนำ codes + CC/MCC optimization ใช้ skill นี้เมื่อ: ให้ code, coding, ICD-10, ICD-9, แปลง notes เป็น code, auto code, ให้รหัสโรค, รหัสหัตถการ, clinical notes to ICD, ช่วย code, code ให้หน่อย"
---

# Smart Coder — AI Clinical Coding Assistant

แปลง clinical notes → ICD-10-TM + ICD-9-CM + CC/MCC optimization

## Process
1. **Parse** — extract medical entities from Thai/English text
2. **Map** — convert entities to ICD codes
3. **Optimize** — reorder for best DRG grouping
4. **Validate** — check Dx-Proc consistency
5. **Present** — show codes with confidence level

## Output Format
```
╔════════════════════════════════════════════╗
║  SMART CODING RESULT                       ║
╠════════════════════════════════════════════╣
║  Principal Dx: I21.0 STEMI anterior    [H] ║
║  Secondary Dx:                             ║
║    1. I25.10 CAD                       [H] ║
║    2. E11.9  DM type 2                [H]  ║
║    3. N17.9  AKI (contrast)    [MCC]  [M]  ║
║  Procedures:                               ║
║    1. 36.07 PTCA 1 vessel             [H]  ║
║    2. 36.06 DES insertion             [H]  ║
║  [H]=High [M]=Medium [L]=Low confidence    ║
║  💡 CC/MCC: N17.9 = MCC → +0.5 RW         ║
╚════════════════════════════════════════════╝
```

## References
| File | อ่านเมื่อ |
|------|----------|
| `references/coding-guidelines.md` | หลักการ coding |
| `references/common-dx-mapping.md` | Thai terms → ICD-10 |
| `references/common-proc-mapping.md` | Thai procedures → ICD-9 |
| `references/cc-mcc-list.md` | CC/MCC codes |
| `references/drg-optimization-tips.md` | optimize DRG |
