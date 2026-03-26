ตรวจสอบ claim ด้วย 8 checkpoints ก่อนส่ง FDH

Input: $ARGUMENTS (AN number หรือ claim data)

1. อ่าน claim data จาก input
2. รัน Rule Engine (core/rule_engine.py) 8 checkpoints
3. ถ้าเปิด AI → เรียก AI Engine วิเคราะห์เพิ่ม
4. สรุปผล: Score, Pass/Warning/Critical, คำแนะนำ
5. ถ้า score < 70 → แจ้งเตือนว่าไม่ควรส่ง
