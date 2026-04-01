---
name: drug-cost-optimizer
description: "วิเคราะห์ต้นทุนยา รพ. แนะนำ switch original→generic ลดต้นทุน 30-60% ใช้ skill นี้เมื่อ: วิเคราะห์ต้นทุนยา, drug cost, generic, original, formulary, ลดต้นทุนยา, DUR, ยานอกบัญชี, NLEM, GPO, ยาแพง"
---

# Drug Cost Optimizer

วิเคราะห์ต้นทุนยา แนะนำ switch original → generic เพื่อลดต้นทุน

## วิธีใช้
1. ถามรายการยา top 20 highest-cost (หรือใช้ common examples)
2. วิเคราะห์: original vs generic, price difference, therapeutic equivalence
3. แนะนำ switches + estimated savings
4. Flag ยาที่ไม่มี generic

## Output Format
| Drug | Current | Generic Alternative | Savings/Unit | Annual Savings | Notes |
|------|---------|-------------------|-------------|---------------|-------|

อ่าน `references/common-switches.md` สำหรับ top 30 switches

## References
| File | อ่านเมื่อ |
|------|----------|
| `references/common-switches.md` | ทุกครั้ง |
| `references/nlem-reference.md` | เช็ค NLEM category |
| `references/drug-switch-guide.md` | หลักการ switch |
