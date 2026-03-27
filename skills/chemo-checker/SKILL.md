---
name: chemo-checker
description: "ตรวจสอบเคสเคมีบำบัด (Chemotherapy) ก่อนส่งเบิก สปสช. ใช้ skill นี้เมื่อ: มีเคสเคมีบำบัดที่ต้องส่งเบิก, ตรวจสอบ regimen/protocol, drug fee schedule, cycle tracking, หรือเมื่อพูดถึง chemo, เคมีบำบัด, มะเร็ง, cancer, oncology, Herceptin, FOLFOX, CHOP, targeted therapy"
---

# Chemo Claim Checker

ตรวจสอบเคสเคมีบำบัดก่อนส่งเบิก — protocol matching, drug FS, cycle tracking

## 8 Checkpoints
1. Cancer diagnosis specific (C00-C97 + site + morphology)
2. Protocol matching — regimen ตรง NHSO-approved
3. Drug fee schedule — ยาทุกตัวอยู่ใน FS + ceiling ราคา
4. Cycle tracking — cycle number + cumulative dose
5. Pathology confirmation — biopsy report
6. Staging — TNM documented
7. Lab clearance — CBC, LFT, RFT each cycle
8. Special requirements — HER2/EGFR/ALK test for targeted therapy

## Reference Files
| File | อ่านเมื่อ |
|------|----------|
| `references/validation-rules.md` | ทุกเคส |
| `references/cancer-regimens.md` | เช็ค regimen |
| `references/drug-fee-schedule-chemo.md` | เช็คยา + ceiling |
| `references/deny-fixes.md` | เคสติด deny |
