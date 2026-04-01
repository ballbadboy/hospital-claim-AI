---
name: opd-ncd-checker
description: "ตรวจสอบเคส OPD/NCD โรคเรื้อรัง ก่อนส่งเบิก สปสช. ใช้ skill นี้เมื่อ: เคส OPD, ผู้ป่วยนอก, NCD, โรคเรื้อรัง, เบาหวาน DM, ความดัน HT, CKD, COPD, asthma, P&P, สร้างเสริมสุขภาพ, ฝากครรภ์, วัคซีน, fee schedule, drug catalog"
---

# OPD/NCD Claim Checker

ตรวจสอบเคสผู้ป่วยนอกโรคเรื้อรัง — Fee Schedule, Drug Catalog, Authen Code

## 8 Checkpoints
1. Basic data — HN, visit date, NCD diagnosis
2. Fee Schedule — service items in NHSO FS
3. Drug Catalog — NCD drugs match GPUID
4. Authen Code — per visit
5. Visit frequency — within annual limit
6. P&P coding — prevention services correct ADP TYPE/CODE
7. Annual monitoring — HbA1c, eGFR, eye/foot exam
8. Submission timing — within 30 days

## Reference Files
| File | อ่านเมื่อ |
|------|----------|
| `references/validation-rules.md` | ทุกเคส |
| `references/ncd-codes.md` | เช็ค NCD diagnosis |
| `references/drug-catalog-ncd.md` | เช็คยา NCD |
| `references/fee-schedule-opd.md` | เช็ค FS items |
| `references/deny-fixes.md` | เคสติด deny |
