# Deny Fixes & C-Code Solutions for Cath Lab

## Common C-Code Errors

### C-438: สิทธิประโยชน์ไม่ตรง
**สาเหตุ:** เลือกเงื่อนไขสิทธิประโยชน์ไม่ตรงกับสิทธิที่พึงเบิกได้
**วิธีแก้:**
1. ตรวจสอบสิทธิผู้ป่วย (UC/SSS/CSMBS)
2. เลือกสิทธิประโยชน์ในการเบิกชดเชยให้ตรงกับสิทธิ
3. กรณีเบิกชดเชยไม่ตรงกับสิทธิหลัก → ตรวจสอบรหัสโครงการพิเศษ
4. บันทึกข้อมูลให้ถูกต้องตามเงื่อนไข แล้วส่งใหม่

### Drug Catalog Mismatch
**สาเหตุ:** รหัสยาใน DRU file ไม่ตรงกับ FDH Drug Catalog
**วิธีแก้:**
1. ดาวน์โหลด Drug Catalog ล่าสุดจาก FDH
2. Map รหัสยาใน HIS กับ GPUID ที่ FDH กำหนด
3. ยาที่ใช้บ่อยใน Cath Lab ต้อง map ก่อน: Heparin, Clopidogrel, Ticagrelor, Prasugrel, Aspirin, GP IIb/IIIa
4. แก้ไขใน DRU file แล้วส่งใหม่

### Lab Catalog Mismatch
**สาเหตุ:** รหัส Lab ไม่ตรง FDH Lab Catalog
**วิธีแก้:** เช่นเดียวกับ Drug Catalog — map รหัส Lab กับ FDH standard

### ADP File Error (Device Code)
**สาเหตุ:** รหัสอุปกรณ์ (stent, balloon, guidewire) ใน ADP file ไม่ถูกต้อง
**วิธีแก้:**
1. ตรวจ TYPE field: 3=วัสดุสิ้นเปลือง, 4=วัสดุข้อต่อ, 5=อวัยวะเทียม
2. CODE ต้องตรงกับที่ สปสช. กำหนด
3. จำนวนต้องตรงกับ procedure note
4. Lot number ต้องตรงกับ GPO VMI record

### DRG Version Pending / อยู่ระหว่างปรับปรุงข้อมูล DRG
**สาเหตุ:** ข้อมูลยังไม่ผ่าน DRG grouper ของ สปสช.
**วิธีแก้:**
1. เช็คว่าข้อมูล 16 แฟ้มครบถ้วน
2. PDx ต้องอยู่ใน ICD-10-TM library ที่ valid
3. Procedure codes ต้องไม่มี error (invalid code, duplicate)
4. ตรวจ LOS, Age, Sex ว่าไม่ conflict กับ DRG grouper logic
5. ส่งข้อมูลแก้ไขใหม่ผ่าน FDH

### Authen Code Missing/Expired
**สาเหตุ:** ไม่มี Authen Code หรือหมดอายุ
**วิธีแก้:**
1. ผู้ป่วยต้อง verify ตัวตนผ่าน Authen Code ก่อนจำหน่าย
2. ถ้าลืม → ติดต่อ สปสช. เขตเพื่อขอผ่อนผัน
3. บางกรณี (ฉุกเฉิน STEMI) สามารถขอ authen ย้อนหลังได้

### Late Submission (ส่งเกิน 30 วัน)
**สาเหตุ:** ส่งข้อมูลเบิกจ่ายเกิน 30 วันหลัง discharge
**วิธีแก้:**
1. ส่งภายใน 24 ชม. = fast track (สปสช. จ่ายภายใน 72 ชม.)
2. ส่งภายใน 30 วัน = flow ปกติ (OPD 15 วัน, IPD 30 วัน)
3. เกิน 30 วัน = ถูกปรับลดอัตราจ่าย
4. ต้องมีระบบ alert เตือนก่อนครบกำหนด

## DRG-Specific Deny Reasons

### Deny: Diagnosis-Procedure Mismatch
**อาการ:** DRG group ไม่ตรงที่คาดหวัง (RW ต่ำกว่าที่ควร)
**สาเหตุที่พบบ่อย:**
- PDx เป็น Acute MI แต่ไม่มี PCI procedure code → group เป็น medical MI (RW ต่ำ)
- มี PCI code แต่ PDx เป็น chronic IHD → group เป็น PTCA wo CCC (RW ต่ำกว่า Acute MI + PCI)
**วิธีแก้:** ตรวจสอบ PDx ให้ตรงกับ clinical reality → ถ้าเป็น acute event จริง ต้อง code เป็น I21.x

### Deny: Incomplete Data
**อาการ:** Error code จาก DRG grouper
**Error codes:**
- Error 1: No Principal Diagnosis → ใส่ PDx ใน DIA file
- Error 2: Invalid PDx → ตรวจ ICD-10 code ว่า valid
- Error 3: Unacceptable PDx → บาง code ห้ามใช้เป็น PDx
- Error 4: PDx not valid for age → ตรวจอายุผู้ป่วย
- Error 5: PDx not valid for sex → ตรวจเพศ
- Error 7: Ungroupable due to sex error → แก้ข้อมูลเพศ

### Deny: High Cost Case (HC) ไม่ผ่าน
**อาการ:** เคส claim สูง แต่ไม่ได้รับชดเชยเพิ่มจากกองทุน HC
**วิธีแก้:**
1. ตรวจว่าเข้าเกณฑ์ HC (ค่ารักษาสูงกว่า threshold)
2. ส่งเอกสารประกอบครบ
3. อุปกรณ์ (stent) ต้อง claim ผ่าน ADP file ไม่ใช่ CHA file

## Template: หนังสืออุทธรณ์

```
เรื่อง: ขอทบทวนการจ่ายชดเชยค่าบริการ กรณี [ระบุ]
เรียน: ผู้อำนวยการสำนักงานหลักประกันสุขภาพแห่งชาติ เขต [X]

เนื่องด้วยโรงพยาบาล [ชื่อ] ได้ให้บริการรักษาผู้ป่วย
- HN: [xxx] 
- วันที่รับเข้ารักษา: [xx/xx/xxxx]
- วันที่จำหน่าย: [xx/xx/xxxx]
- การวินิจฉัย: [ICD-10 code + ชื่อโรค]
- หัตถการ: [ICD-9-CM codes + ชื่อหัตถการ]

ทางโรงพยาบาลได้ส่งข้อมูลเบิกจ่ายผ่านระบบ FDH แล้ว 
แต่พบว่าเคสดังกล่าวไม่ได้รับการชดเชย/ได้รับชดเชยต่ำกว่าที่ควร
เนื่องจาก: [ระบุเหตุผลที่ deny]

ข้อชี้แจง:
[ระบุเหตุผลทางคลินิกที่สนับสนุน พร้อมอ้างอิงแนวทางเวชปฏิบัติ]

เอกสารประกอบ:
1. สำเนาเวชระเบียน
2. รายงานผลการสวนหัวใจ (Cath report)
3. ผลตรวจ Troponin / EKG
4. ใบรายงานผลหัตถการ
5. [อื่นๆ ตามความเหมาะสม]

จึงขอให้ทบทวนการจ่ายชดเชยดังกล่าว

ลงชื่อ ............................
([ชื่อ-สกุล])
ตำแหน่ง: [ตำแหน่ง]
โรงพยาบาล [ชื่อ]
```
