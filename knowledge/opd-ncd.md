# OPD/NCD Module — ผู้ป่วยนอก & โรคเรื้อรัง

## OPD Claim Rules (สปสช.)
- จ่ายตาม **Fee Schedule (FS)** ไม่ใช่ DRG
- ส่งข้อมูลภายใน 30 วันหลังให้บริการ
- Authen Code required **ทุก visit**

## NCD Chronic Diseases
| Disease | ICD-10 | Key FS Items |
|---------|--------|-------------|
| DM | E10-E14 | HbA1c, eye exam, foot exam (annual) |
| HT | I10-I15 | BP monitoring, basic labs |
| CKD | N18.x | eGFR, urine albumin/protein |
| COPD | J44.x | Spirometry, inhalers |
| Asthma | J45.x | Peak flow, controller inhalers |

## Key Deny Causes
1. **Drug Catalog mismatch** — ยา NCD ต้อง match GPUID ใน FDH Drug Catalog
2. **Visit frequency exceeded** — บางบริการจำกัด 2 ครั้ง/คน/ปี
3. **FS item code missing** — รายการบริการไม่อยู่ใน Fee Schedule
4. **Authen Code missing** — ทุก visit ต้องมี
5. **P&P coding errors** — สร้างเสริมสุขภาพ/ป้องกันโรค ต้อง code ADP ถูก

## PP Fee Schedule (ส่งเสริมป้องกัน)
- ANC visits (ฝากครรภ์)
- Vaccination (childhood + adult)
- Cancer screening (cervical, breast, colorectal)
- NCD screening (DM, HT, CVD risk)
- ADP file: TYPE + CODE ตาม สปสช. กำหนดเฉพาะ PP

## Common OPD Drug Catalog Issues
- Metformin, Glipizide → must match GPUID exactly
- Amlodipine, Enalapril → common HT drugs often mismatch
- Inhalers (Salbutamol, Budesonide) → brand-specific GPUID
- ถ้า Drug Catalog เปลี่ยน version ต้อง remap ใน HIS
