# ER/UCEP — Common Deny Causes & Fixes

## Deny 1: ไม่เข้าเกณฑ์ฉุกเฉินวิกฤต
**สาเหตุ:** Triage level ไม่ document หรือ document เป็น Yellow/Green
**วิธีแก้:** ตรวจ medical record → ถ้ามี vital signs/symptoms ตรง Red/Orange → เพิ่ม triage documentation → resubmit
**Recovery:** 60% (ถ้ามีหลักฐาน clinical จริง)

## Deny 2: เกิน 72 ชม. UCEP Window
**สาเหตุ:** LOS > 72 ชม. แต่ claim ทั้งหมดเป็น UCEP
**วิธีแก้:** Split billing — UCEP สำหรับ 72 ชม.แรก + สิทธิปกติหลัง 72 ชม.
**Recovery:** 80% (ได้ UCEP ส่วนแรก)

## Deny 3: Refer Protocol ไม่ครบ
**สาเหตุ:** ไม่ได้ refer กลับหลัง 72 ชม. หรือ refer form ไม่ครบ
**วิธีแก้:** Document เหตุผลที่ย้ายไม่ได้ (clinical instability) → อุทธรณ์
**Recovery:** 70%

## Deny 4: Emergency Authen Code Missing
**สาเหตุ:** ไม่ได้ขอ authen code ทันที
**วิธีแก้:** ขอ authen code ย้อนหลัง (ถ้าอยู่ในกรอบเวลา) หรืออุทธรณ์พร้อมหลักฐาน
**Recovery:** 50%

## Deny 5: Wrong Project Code
**สาเหตุ:** ใช้ UC project code แทน UCEP project code
**วิธีแก้:** แก้ project code ใน FDH → resubmit
**Recovery:** 95%
