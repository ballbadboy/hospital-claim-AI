---
type: concept
tags: [audit, MRA, OPD, ER, medical-record, billing, quality]
sources: []
last_updated: 2026-04-14
---

# MRA — เกณฑ์ตรวจประเมินเวชระเบียนผู้ป่วยนอก/ฉุกเฉิน (OPD/ER)

## ประเภทที่ประเมิน

| ประเภท | รายละเอียด |
|--------|-----------|
| **General case** | OPD ทั่วไป + ER — ใช้ข้อมูลจาก visit ที่ตรวจ |
| **Chronic case** | โรคเรื้อรัง (DM, HT, COPD, หืด, หัวใจ, หลอดเลือดสมอง) — ใช้ First visit date ของปี |

## หัวข้อที่ประเมิน OPD/ER

### 1. Patient Identification
**ข้อมูลตัวตนผู้ป่วย**

| # | เกณฑ์ |
|---|-------|
| 1 | ชื่อ นามสกุล เพศ อายุ (หรือวันเกิด) ถูกต้องครบ |
| 2 | เลขประจำตัวประชาชน 13 หลัก (หรือเลขต่างด้าว) |
| 3 | สิทธิ์การรักษา (UC/ประกันสังคม/ราชการ ฯลฯ) |
| 4 | HN และ Visit date ถูกต้อง |

---

### 2. Chief Complaint & Present Illness
**อาการสำคัญและประวัติปัจจุบัน**

| # | เกณฑ์ |
|---|-------|
| 1 | Chief complaint ชัดเจน ระบุระยะเวลา |
| 2 | Present illness ครอบคลุมอาการที่เกี่ยวข้อง |
| 3 | ประวัติการรักษาก่อนหน้า (ถ้ามี) |
| 4 | ประวัติแพ้ยา |

---

### 3. Physical Examination
**การตรวจร่างกาย**

| # | เกณฑ์ |
|---|-------|
| 1 | Vital signs (BP, PR, RR, Temp) |
| 2 | General appearance |
| 3 | การตรวจระบบที่เกี่ยวข้องกับโรค |
| 4 | ลายมือที่อ่านออกได้ |

---

### 4. Diagnosis & Plan
**การวินิจฉัยและแผนการรักษา**

| # | เกณฑ์ |
|---|-------|
| 1 | Diagnosis เป็น clinical term (ไม่ใช่แค่ ICD code) |
| 2 | Diagnosis สอดคล้องกับอาการและการตรวจ |
| 3 | Investigation ที่สั่ง (ถ้ามี) |
| 4 | Treatment สอดคล้องกับ diagnosis |
| 5 | Follow up plan / นัดครั้งต่อไป |

---

### 5. Medication Record
**บันทึกยา**

| # | เกณฑ์ |
|---|-------|
| 1 | ชื่อยาครบถ้วน (generic name หรือ brand) |
| 2 | Dose, Route, Frequency ถูกต้อง |
| 3 | ระยะเวลาการใช้ยา |
| 4 | ลายมือชื่อแพทย์หรือผู้สั่งยา |

---

### 6. Follow Up Record (เฉพาะ Chronic case)
**การติดตามผู้ป่วยโรคเรื้อรัง**

| # | เกณฑ์ |
|---|-------|
| 1 | บันทึกผล Lab ที่เกี่ยวข้อง (HbA1c, BP, FBS ฯลฯ) |
| 2 | ประเมินการควบคุมโรค (ดี/พอใช้/ไม่ดี) |
| 3 | ปรับยาหรือแผนการรักษา (ถ้ามี) |
| 4 | การสอน/แนะนำผู้ป่วย (Diet, Exercise, ยา) |
| 5 | นัด Follow up ครั้งต่อไป |

---

### 7. Physician Signature
**ลายมือชื่อแพทย์**

| # | เกณฑ์ |
|---|-------|
| 1 | ลายมือชื่อแพทย์ทุกหน้าที่บันทึก |
| 2 | ระบุชื่อ นามสกุลอ่านออกได้ |
| 3 | เลขที่ใบประกอบวิชาชีพเวชกรรม |
| 4 | วันเดือนปีและเวลาที่บันทึก |

---

## แบบฟอร์ม MRA OPD/ER (MRA Form)

```
Hcode: _________ Hname: _________ HN: _________ PID: _________

□ General case     Diagnosis: _________ Visit Date: _________
□ Chronic case     Diagnosis: _________ 1st Visit Date: _________
                   ช่วงเวลาที่ตรวจสอบ: _______ ถึง _______
```

**การบันทึก NA:** ใช้เมื่อไม่จำเป็นต้องมีเอกสารใน Content นั้น  
เช่น Follow up, Operative note, Informed consent, Rehabilitation record ที่ไม่มีการให้บริการ

---

## จุดที่ Claim ได้รับผลกระทบ (OPD)

| ปัญหา MRA | ผลต่อ Claim |
|-----------|-----------|
| ไม่มี Diagnosis | claim ถูก reject — ไม่ผ่าน 16 แฟ้ม |
| Diagnosis เป็น ICD code ล้วน | coder coding ผิด → DRG/Fee schedule ผิด |
| ไม่มีลายมือชื่อแพทย์ | claim ถูก deny — ไม่มีหลักฐานผู้รักษา |
| Chronic case ไม่มี HbA1c/BP ใน chart | PP NCD audit ปฏิเสธ |
| Visit date ไม่ตรง | C179 (OPD ซ้ำ) หรือ claim วันผิด |

---

## Related Concepts

- [[concepts/MRA-ภาพรวม]] — ภาพรวม MRA
- [[concepts/mra-คำนิยาม]] — คำนิยาม
- [[concepts/mra-ipd-เกณฑ์]] — เกณฑ์ IPD 12 หัวข้อ
- [[concepts/op-opd-ผู้ป่วยนอก]] — การเบิกจ่าย OPD
- [[concepts/ncd-โรคเรื้อรัง]] — NCD claim
- [[concepts/er-ucep-ฉุกเฉิน]] — UCEP/ER
