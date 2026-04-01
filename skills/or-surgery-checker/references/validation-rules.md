# OR Surgery — 8 Checkpoints

## Checkpoint 1: Basic Data Validation
- HN, AN, admit/discharge dates ครบถ้วน
- LOS สมเหตุสมผลกับ procedure complexity
- Patient demographics (age, sex) ตรงกับ procedure

## Checkpoint 2: Procedure Code Validation
- Main procedure coded first (determines DRG group)
- Multiple procedure bundling rules ถูกต้อง
- Extension codes (position + count) สำหรับ bilateral/multiple sites
- ICD-9-CM code ตรงกับ operative note description

## Checkpoint 3: OPTYPE Verification
- Major OR (1): procedures requiring general/regional anesthesia in OR
- Minor OR (2): procedures under local anesthesia or bedside
- Non-OR (3): diagnostic/therapeutic procedures not in OR
- OPTYPE must match actual procedure performed

## Checkpoint 4: Implant/Prosthesis Documentation
- ADP TYPE 4 (ข้อต่อ) or TYPE 5 (อวัยวะเทียม) coded correctly
- Lot number / Serial number recorded
- GPO VMI/SMI matching (if applicable)
- Implant specifications: type, size, manufacturer, quantity

## Checkpoint 5: Anesthesia Coding
- GA (general) vs Regional (spinal/epidural) coded separately
- Anesthesia code matches procedure type
- Anesthesia record documentation present

## Checkpoint 6: Documentation Completeness
- [ ] Operative note (detailed procedure description)
- [ ] Anesthesia record
- [ ] Implant details (type, size, manufacturer, lot, qty)
- [ ] Indication for surgery documented
- [ ] Consent form signed
- [ ] Post-op complications documented if any

## Checkpoint 7: DRG Optimization
- Surgical DRG weight >> Medical DRG → ensure OR procedure coded
- Post-op complications as CC/MCC:
  - SSI (T81.4) = CC
  - DVT (I82.4x) = MCC
  - PE (I26.x) = MCC
  - Wound dehiscence (T81.3) = CC
- Bilateral procedures → extension code = higher RW

## Checkpoint 8: Timing & Submission
- Submit within 30 days of discharge
- Authen Code obtained
- Pre-authorization for elective high-cost procedures
