# FDH 16-File Structure for Cath Lab Claims

## Overview
Financial Data Hub (FDH) รับข้อมูล 16 แฟ้มจาก HIS ของโรงพยาบาล
ข้อมูลถูกส่งเข้าที่ สปสช. เพื่อประมวลผล e-Claim

## แฟ้มที่สำคัญสำหรับ Cath Lab

### IPD — Inpatient Data
| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| AN | Admission number | ต้องไม่ว่าง |
| DATEADM | วันที่ admit | ต้องก่อน D/C date |
| DATEDSC | วันที่ discharge | ใช้คำนวณ LOS |
| DISCHT | Discharge type | 1=Approval, 2=Against advice |
| WARD | Ward code | ต้อง map กับ ward ที่ขึ้นทะเบียน |

### DIA — Diagnosis
| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| DIAG | ICD-10 code | ต้อง valid ใน ICD-10-TM library |
| DXTYPE | 1=PDx, 2=SDx, 3=External cause | PDx ต้องมี 1 ตัว SDx ได้หลายตัว |
| PROVIDER | รหัสแพทย์ | ต้องมี |

**Critical rules:**
- PDx (DXTYPE=1) ต้องมีเพียง 1 รหัส = เหตุผลหลักที่ admit
- SDx ทุกตัวต้องเป็น comorbidity ที่มีอยู่จริง ไม่ใช่ duplicate
- SDx ที่เป็น CC/MCC ต้อง code ครบเพื่อ optimize DRG weight

### OPR — Operation/Procedure
| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| ESSION | Episode/session | ตรง AN |
| OPTYPE | OR type | 1=major OR, 2=minor OR, 3=non-OR |
| OPCODE | ICD-9-CM code | ต้อง valid + extension code ถ้ามี |
| DATEOP | วันที่ทำ | ต้องอยู่ระหว่าง admit-discharge |
| PROVIDER | รหัสแพทย์ผ่าตัด | ต้องมี |

**Cath Lab procedure coding:**
- PCI (36.0x) = OPTYPE 1 (major OR) ใน Thai DRG
- Diagnostic cath (37.22) = OPTYPE 3 (non-OR) แต่มีผลต่อ DRG grouping
- ต้อง code ทุก procedure ที่ทำ ไม่ใช่แค่ main procedure

### ADP — Additional Payment (อุปกรณ์)
| Field | Description | Cath Lab Check |
|-------|-------------|----------------|
| TYPE | 3=วัสดุ, 4=ข้อต่อ, 5=อวัยวะเทียม | Stent = TYPE 5 |
| CODE | รหัสอุปกรณ์ สปสช. | ต้องตรงกับ Fee Schedule |
| QTY | จำนวน | ต้องตรง procedure note |
| RATE | ราคาต่อหน่วย | ต้องไม่เกิน ceiling ที่ สปสช. กำหนด |
| TOTAL | ราคารวม | QTY x RATE |
| SERIALNO | Lot/Serial number | ต้องตรง GPO VMI |

**Stent coding ใน ADP:**
- DES (Drug-Eluting Stent): ใช้ CODE ตามที่ สปสช. กำหนดสำหรับ DES
- BMS (Bare Metal Stent): CODE ต่างจาก DES
- Balloon catheter, guidewire: แยก CODE
- IABP: CODE เฉพาะ

### DRU — Drug
| Field | Description | Check |
|-------|-------------|-------|
| DID | Drug ID (GPUID) | ต้องตรง FDH Drug Catalog |
| AMOUNT | จำนวน | ต้องสมเหตุสมผล |
| TOTAL | ราคารวม | |

### CHA — Charge
| Field | Description |
|-------|-------------|
| CHRGITEM | Charge item code |
| AMOUNT | จำนวนเงิน |
| DATE | วันที่ |

## Common FDH Submission Errors

### Format Errors
- Date format ผิด (ต้องเป็น YYYYMMDD)
- Code มี leading/trailing spaces
- Numeric field มีตัวอักษร
- Required field เป็น null/empty

### Logic Errors
- D/C date ก่อน Admit date
- Procedure date นอกช่วง Admit-D/C
- PDx ไม่ valid สำหรับ age/sex ของผู้ป่วย
- SDx duplicate กับ PDx
- ADP quantity > reasonable limit

### Timing Rules
- ส่งภายใน 24 ชม. → fast track (สปสช. จ่ายภายใน 72 ชม.)
- ส่งภายใน 30 วัน → flow ปกติ (IPD จ่ายภายใน 30 วัน)
- เกิน 30 วัน → ปรับลดอัตราจ่าย
- Authen Code ต้อง verify ก่อน discharge
