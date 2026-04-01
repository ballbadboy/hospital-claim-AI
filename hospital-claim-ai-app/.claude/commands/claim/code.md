แปลง clinical notes ภาษาไทย/อังกฤษ เป็น ICD-10 + ICD-9-CM อัตโนมัติ

Input: $ARGUMENTS (clinical notes เช่น "ผู้ป่วยชาย 65 ปี เจ็บหน้าอก ST elevation V1-V4 ทำ PCI ใส่ stent LAD 1 ตัว")

ใช้ skill smart-coder:
1. วิเคราะห์ text → สกัด diagnosis keywords (STEMI/NSTEMI/UA/CAD)
2. ระบุ wall/territory (anterior, inferior, lateral, posterior)
3. สกัด procedure keywords (PCI, stent, catheterization, angiography)
4. แนะนำ PDx (ICD-10-TM) + SDx + CC/MCC optimization
5. แนะนำ Procedures (ICD-9-CM)
6. ประมาณ DRG + RW + expected payment

Output: PDx, SDx[], Procedures[], Expected DRG, RW, Payment estimate
