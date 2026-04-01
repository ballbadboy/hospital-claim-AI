# Dialysis — Deny Causes & Fixes

## Deny 1: Session Limit Exceeded
**วิธีแก้:** ตรวจสอบจำนวน session จริง → ถ้าเกินจริง อุทธรณ์ด้วยเหตุผลทางคลินิก
**Recovery:** 40%

## Deny 2: Authen Code Missing
**วิธีแก้:** ขอ authen code ย้อนหลัง (ถ้ายังอยู่ในกรอบเวลา)
**Recovery:** 50%

## Deny 3: Drug Catalog Mismatch
**วิธีแก้:** ตรวจ GPUID ใน FDH Drug Catalog → แก้ให้ตรง → resubmit
**Recovery:** 90%

## Deny 4: Duplicate Claim
**วิธีแก้:** ตรวจว่า claim ซ้ำจริงหรือไม่ → ถ้าไม่ซ้ำ ส่งหลักฐานอุทธรณ์
**Recovery:** 70%
