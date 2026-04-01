---
name: dialysis-checker
description: "ตรวจสอบเคสฟอกไต (Dialysis HD/CAPD) ก่อนส่งเบิก สปสช. ใช้ skill นี้เมื่อ: มีเคสฟอกไตที่ต้องส่งเบิก, session limit, drug catalog EPO/Iron, หรือเมื่อพูดถึง dialysis, HD, CAPD, ฟอกไต, ไตเทียม, CKD stage 5, ESRD, hemodialysis, AVF, vascular access"
---

# Dialysis Claim Checker (HD/CAPD)

ตรวจสอบเคสฟอกไตก่อนส่งเบิก — session limit, drug catalog, authen code

## 8 Checkpoints
1. Basic data — HN, diagnosis N18.5/ESRD
2. Modality code — HD (39.95) vs CAPD (54.98) match billing
3. Session limit — monthly count within allowed
4. Authen Code — required per session
5. Drug catalog — EPO, Iron, Heparin match GPUID
6. Documentation — nephrology eval, vascular access, Kt/V
7. Duplicate check — no duplicate between hospitals
8. Fee schedule — dialyzer, blood tubing, drugs match FS

อ่าน references/ สำหรับรายละเอียดแต่ละ checkpoint

## Reference Files
| File | อ่านเมื่อ |
|------|----------|
| `references/validation-rules.md` | ทุกเคส |
| `references/dialysis-codes.md` | เช็ค modality codes |
| `references/drug-catalog-dialysis.md` | เช็ค EPO/Iron/Heparin |
| `references/deny-fixes.md` | เคสติด deny |
