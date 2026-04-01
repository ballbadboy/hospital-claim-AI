# Chemo Module — เคมีบำบัด & มะเร็ง

## Key Deny Causes
1. **Protocol mismatch** — regimen ต้องตรง NHSO-approved protocol ตาม tumor type
2. **ยาไม่อยู่ใน Fee Schedule** — เช็คก่อนให้ยา
3. **รพ. ไม่ผ่านเกณฑ์ประเมินศักยภาพเคมีบำบัด**
4. **Cycle tracking incomplete** — ต้อง document cycle number + cumulative dose
5. **Diagnosis ไม่ specific** — C00-C97 ต้องถึง site + morphology

## Cancer-Specific Rules
| Cancer | ICD-10 | Common Regimen | Special Requirement |
|--------|--------|---------------|-------------------|
| Breast | C50.x | AC-T, CMF, Herceptin | HER2 test for Herceptin |
| Colorectal | C18-C20 | FOLFOX, FOLFIRI | Staging must support chemo |
| Lung | C34.x | Cisplatin-based, targeted | EGFR/ALK test for targeted |
| Lymphoma | C81-C85 | CHOP, R-CHOP | Biopsy confirmation |
| Leukemia | C91-C95 | Per subtype | BMA/biopsy required |

## Documentation Required
- [ ] Pathology report (cancer confirmed + morphology)
- [ ] TNM staging (or disease-specific staging)
- [ ] Treatment plan signed by oncologist
- [ ] Regimen/protocol selection with rationale
- [ ] Prior cycle records + cumulative dose
- [ ] Lab clearance each cycle (CBC, LFT, RFT)
- [ ] Regimen code ตรงกับ สปสช. กำหนด

## มะเร็งรักษาทุกที่ (Cancer Anywhere)
- ผู้ป่วย UC รักษามะเร็งที่ รพ. ไหนก็ได้ที่พร้อม
- ไม่ต้อง refer จาก รพ. ต้นสังกัด
- ต้อง confirm diagnosis + staging + document
- ใช้ e-Claim project code เฉพาะมะเร็ง

## Fee Schedule สำหรับยาเคมีบำบัด
- ยาเคมีบำบัดเบิกตาม Fee Schedule (FS) ไม่ใช่ DRG
- มี ceiling ราคาต่อ regimen/cycle
- ยาที่ไม่อยู่ใน FS ไม่สามารถเบิกได้ → ตรวจก่อนให้ยา
- Targeted therapy (Herceptin, Imatinib) มีเกณฑ์เฉพาะ
