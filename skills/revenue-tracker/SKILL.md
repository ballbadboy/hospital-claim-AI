---
name: revenue-tracker
description: "ติดตามรายได้จาก claim ตั้งแต่ส่งเบิกจนได้เงิน — track: submitted→processing→paid/denied→appeal→recovered ใช้ skill นี้เมื่อ: ติดตามเงิน, revenue tracking, claim status, เงินค้าง, AR aging, appeal tracking, recovery rate, payment status"
---

# Revenue Tracker — ติดตามรายได้จาก Claim

Track claim lifecycle: Submit → Process → Paid/Denied → Appeal → Recovered

## วิธีใช้
1. สร้าง/maintain revenue tracking dashboard
2. Track claim lifecycle ทุก stage
3. คำนวณ: days to payment, denial rate, recovery rate
4. Alert: claims pending >30 days, high-value denials

## Key Metrics
- **AR Days:** Avg days from submit to payment
- **Denial Rate:** Denied / Total submitted × 100%
- **Recovery Rate:** Recovered from appeal / Total denied × 100%
- **Clean Claim Rate:** Paid first submission / Total × 100%
- **Revenue at Risk:** Sum of denied + pending >60 days

## Templates
| File | ใช้เมื่อ |
|------|---------|
| `templates/revenue-dashboard.md` | สร้าง dashboard |
| `templates/weekly-report.md` | สรุปรายสัปดาห์ |

## References
| File | ใช้เมื่อ |
|------|---------|
| `references/tracking-methodology.md` | วิธี track |
| `references/escalation-rules.md` | เมื่อไหร่ต้อง escalate |
