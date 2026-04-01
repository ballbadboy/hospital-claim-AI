# OR Surgery — Common Deny Causes & Fixes

## Deny 1: Multiple Procedure Bundling Error
**สาเหตุ:** Code sequence ผิด — main procedure ไม่ได้อยู่ลำดับแรก
**วิธีแก้:** เรียง main procedure (highest RW) เป็น code แรก → DRG grouper จะจัดกลุ่มถูก
**Recovery:** 90%

## Deny 2: Extension Code Error
**สาเหตุ:** ICD-9-CM extension code (position + count) ไม่ถูก เช่น bilateral procedure ไม่ได้ใส่ extension
**วิธีแก้:** ตรวจ operative note → เพิ่ม extension code ที่ถูกต้อง (ตำแหน่ง + จำนวน)
**Recovery:** 85%

## Deny 3: Implant/ADP Mismatch
**สาเหตุ:** Prosthesis ไม่ตรง ADP file หรือ GPO record
**วิธีแก้:** ตรวจ lot/serial number ตรงกับ GPO VMI/SMI → แก้ ADP file
**Recovery:** 80%

## Deny 4: OPTYPE Wrong
**สาเหตุ:** OPTYPE ไม่ตรง — เช่น Minor OR แต่ใส่ Major OR
**วิธีแก้:** ตรวจ operative note → OPTYPE ต้องตรงกับ anesthesia type + setting
**Recovery:** 95%

## Deny 5: Anesthesia Not Coded
**สาเหตุ:** Anesthesia procedure ไม่ได้ code แยก
**วิธีแก้:** เพิ่ม anesthesia code (96.xx series) ตาม anesthesia record
**Recovery:** 90%

## Deny 6: Missing Operative Note
**สาเหตุ:** เอกสาร operative note ไม่ครบ
**วิธีแก้:** ขอ operative note จากศัลยแพทย์ → แนบในเวชระเบียน → resubmit
**Recovery:** 85%
