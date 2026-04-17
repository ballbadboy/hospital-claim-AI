---
type: concept
tags: [billing, IP, critical-care, DRG, ICU, CC/MCC]
sources: []
last_updated: 2026-04-14
---

# ICU / ผู้ป่วยวิกฤต — การเบิกจ่ายใต้ระบบ สปสช.

## หลักการสำคัญ

สปสช. **ไม่มีการจ่ายค่า ICU แยกรายวัน** — ค่าใช้จ่ายทั้งหมดของ ICU รวมอยู่ใน **DRG weight (RW)** ที่ได้จากการจัดกลุ่มโรค ดังนั้นการ optimize การเบิก ICU คือการ **ลง ICD-10 CC/MCC ให้ครบ** เพื่อให้ได้ PCCL สูงและ RW สูงขึ้น

## โครงสร้างการจ่ายเงิน

| รายการ | วิธีจ่าย | หมายเหตุ |
|--------|---------|---------|
| ค่า ICU ห้อง + monitoring | รวมใน DRG RW | ไม่มีการแยกเบิก |
| ค่า Ventilator | รวมใน DRG RW | รวมอยู่ใน procedure codes |
| CRRT (ไตวายเฉียบพลัน) | **เบิกแยกนอก DRG** | ดู [[concepts/CRRT-ฟอกเลือดต่อเนื่อง]] |
| ECMO | เบิกแยก + ต้อง Prior Auth | ดู [[concepts/PAK-ขออนุมัติล่วงหน้า]] |
| ยาและ consumable | รวมใน DRG (ยกเว้นยาพิเศษ) | ยาเคมีบำบัด/ยาชีวภาพ แยก |

## PCCL และ RW ที่เพิ่มขึ้น

```
PCCL 0 = ไม่มี CC/MCC          → RW ต่ำสุด
PCCL 1-2 = มี CC (complication/comorbidity)
PCCL 3-4 = มี MCC (major CC)    → RW สูงสุด (บางกลุ่มเพิ่ม >2x)
```

### Diagnosis ที่เพิ่ม PCCL เป็น MCC (ต้องลงให้ครบ)

| ICD-10 | ภาวะ | หมายเหตุ |
|--------|------|---------|
| A41.9 | Sepsis, unspecified | พบบ่อย ICU, ต้องมีหลักฐานใน chart |
| A41.0–A41.5 | Sepsis specific organism | ระบุ organism ถ้าทราบผล culture |
| R65.2x | Severe sepsis / Septic shock | แยก R65.20 (w/o organ failure) / R65.21 (with) |
| J96.0, J96.1 | Acute/Chronic respiratory failure | ต้อง on vent หรือมี hypoxia documented |
| N17.x | Acute kidney injury | AKI stage 1-3 ตาม KDIGO |
| I46.9 | Cardiac arrest | ถ้า resuscitated |
| G93.1 | Anoxic brain damage | post-cardiac arrest |
| K72.x | Hepatic failure | ตับวายเฉียบพลัน |
| D65 | Disseminated intravascular coagulation (DIC) | |
| E87.x | Electrolyte disorder | ถ้า severe (Na <120, K >6.5 ฯลฯ) |

## Procedure Codes ที่ต้องลง (ICD-9-CM)

| ICD-9-CM | หัตถการ | เหตุผล |
|----------|---------|-------|
| 96.04, 96.05 | Endotracheal intubation / Mechanical ventilation | เพิ่ม OR flag → DRG ผ่าตัด |
| 39.95 | Hemodialysis (HD ฉุกเฉิน) | ถ้าทำใน ICU |
| 99.04 | Blood transfusion | ถ้าให้เลือดขณะ ICU |
| 89.52 | Electrocardiographic monitoring | |
| 93.90 | Respiratory therapy | |

## เกณฑ์หน่วยบริการ ICU

เพื่อ claim ICU cases และ high-complexity DRG ได้ หน่วยบริการต้องมีศักยภาพลงทะเบียนกับ สปสช.:
- **H50** — ICU/Critical Care capability (ต้องบันทึกใน CP PP)
- มีแพทย์ผู้เชี่ยวชาญดูแล (intensivist หรือแพทย์ที่ผ่านการอบรม)
- มีอุปกรณ์ monitoring ครบตามมาตรฐาน

## สาเหตุ Deny ที่พบบ่อย — ICU Cases

| สาเหตุ | อาการ | วิธีแก้ |
|--------|-------|--------|
| ไม่ลง sepsis ทั้งที่มีใน chart | DRG น้ำหนักต่ำกว่าความเป็นจริง | ตรวจ lab (WBC, lactate, culture) + ลง A41.x |
| PDx ไม่ใช่สาเหตุหลักที่นำเข้า ICU | Grouper จัดกลุ่มผิด MDC | PDx = สาเหตุ admit ไม่ใช่ภาวะแทรกซ้อน |
| ไม่ลง MCC ทั้งที่มีหลักฐาน | PCCL ต่ำกว่าที่ควร | Clinical coding audit ทุก ICU case |
| ไม่ครบ 16 แฟ้ม | Claim ถูก reject อัตโนมัติ | ดู [[concepts/ip-drg-ผู้ป่วยใน]] |
| ส่งเกิน 30 วัน | C998 error | ดู [[concepts/C998-ส่งเกินกำหนด]] |
| ไม่มีหลักฐานสนับสนุน diagnosis | ถูก deny หลัง audit | ต้องมี progress note / lab ยืนยัน |

## ขั้นตอนตรวจ ICU Claim ก่อนส่ง

1. **ตรวจ PDx** — ใช่สาเหตุที่นำผู้ป่วยมา admit จริงหรือไม่?
2. **ตรวจ CC/MCC** — ลง sepsis, organ failure ครบหรือยัง?
3. **ตรวจ Procedure** — ใส่ intubation, mechanical ventilation ถ้าทำ
4. **ตรวจอุปกรณ์พิเศษ** — CRRT/ECMO ต้องมี Prior Auth แยก
5. **ตรวจ PCCL** — รัน grouper ดูว่า PCCL ออกมาเป็นเท่าไหร่
6. **ตรวจ 16 แฟ้ม** — ครบถ้วนก่อนส่ง

## Related Concepts

- [[concepts/ip-drg-ผู้ป่วยใน]] — ระบบ DRG พื้นฐาน
- [[concepts/CRRT-ฟอกเลือดต่อเนื่อง]] — CRRT เบิกแยกนอก DRG
- [[concepts/er-ucep-ฉุกเฉิน]] — ผู้ป่วยที่เข้า ER ก่อน admit ICU
- [[concepts/DRG-กลุ่มวินิจฉัยโรคร่วม]] — DRG weight และ PCCL คำนวณอย่างไร
- [[concepts/PAK-ขออนุมัติล่วงหน้า]] — Prior Auth สำหรับ ECMO/อุปกรณ์พิเศษ
