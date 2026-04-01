---
name: deny-predictor
description: "ทำนายว่า claim จะถูก deny หรือไม่ก่อนส่งเบิก — วิเคราะห์ 10 risk factors ให้ probability score 0-100% ใช้ skill นี้เมื่อ: ทำนาย deny, predict denial, risk assessment, โอกาสถูก deny, เคสนี้จะผ่านมั้ย, deny probability, claim risk score, ส่งเบิกได้เลยมั้ย"
---

# Deny Predictor — ทำนาย Deny ก่อนส่งเบิก

วิเคราะห์ 10 risk factors → deny probability 0-100%

## วิธีใช้
1. รับ claim data (PDx, SDx, Procedures, DRG, LOS, department)
2. Score 10 risk factors (0-10 each)
3. คำนวณ deny probability
4. แสดง breakdown + recommended fixes

## 10 Risk Factors
อ่าน `references/risk-factors.md` สำหรับ scoring criteria

## Output Format
```
╔════════════════════════════════════════╗
║  DENY RISK PREDICTION                  ║
╠════════════════════════════════════════╣
║  Deny Probability: 73% ████████░░ HIGH ║
║                                        ║
║  Top Risk Factors:                     ║
║  🔴 Dx-Proc mismatch        9/10      ║
║  🔴 Documentation gaps      8/10      ║
║  🟡 CC/MCC incomplete       6/10      ║
║  🟢 Timing OK               2/10      ║
║                                        ║
║  Fix Priority:                         ║
║  1. แก้ procedure code → ลด risk 25%  ║
║  2. เพิ่มเอกสาร → ลด risk 20%         ║
║                                        ║
║  After fixes: ~28% ███░░░░░░░ MEDIUM   ║
╚════════════════════════════════════════╝
```

## References
| File | อ่านเมื่อ |
|------|----------|
| `references/risk-factors.md` | ทุกเคส — scoring criteria |
| `references/deny-patterns.md` | historical patterns |
| `references/probability-model.md` | วิธีคำนวณ |
