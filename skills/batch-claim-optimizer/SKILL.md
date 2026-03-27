---
name: batch-claim-optimizer
description: "ตรวจสอบและ optimize claims ทั้ง รพ. พร้อมกัน — upload CSV แล้ว AI ตรวจทุกเคส เรียงตามมูลค่า ใช้ skill นี้เมื่อ: batch check, optimize ทั้งล็อต, upload CSV claims, ตรวจก่อนส่งเบิกทั้งเดือน, เพิ่ม RW, CC/MCC optimization batch, ตรวจ claims ทั้งหมด"
---

# Batch Claim Optimizer — ตรวจ + Optimize ทั้ง รพ.

Upload CSV/Excel → AI ตรวจทุกเคส → เรียงตาม revenue impact

## วิธีใช้
1. รับ CSV/Excel (HN, AN, PDx, SDx, Procedures, DRG, RW)
2. ตรวจ validation ทุกเคส
3. หา CC/MCC optimization opportunities
4. เรียงตาม revenue impact (สูงสุดก่อน)
5. สรุป: total claims, issues, potential RW increase, estimated revenue gain

## Output
```
═══════════════════════════════════════════════
  BATCH OPTIMIZATION SUMMARY
═══════════════════════════════════════════════
  Total Claims:     200
  Issues Found:     45 (23%)
  Optimization:     32 claims can increase RW
  Potential Gain:   +18.5 RW = ~฿154,525

  TOP 10 PRIORITY FIXES:
  1. AN-12345: +2.1 RW (฿17,535) — add MCC N17.9
  2. AN-12346: +1.8 RW (฿15,030) — fix proc sequence
  ...
═══════════════════════════════════════════════
```

## References
| File | ใช้เมื่อ |
|------|---------|
| `references/batch-process-guide.md` | วิธี process CSV |
| `references/optimization-patterns.md` | CC/MCC patterns |
| `references/priority-scoring.md` | วิธีเรียงลำดับ |
