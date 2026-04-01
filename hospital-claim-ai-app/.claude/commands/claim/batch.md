ตรวจสอบและ optimize claims หลายเคสพร้อมกัน

Input: $ARGUMENTS (CSV data หรือ list ของ claims: HN, AN, PDx, SDx, Procedures, DRG, RW)

ใช้ skill batch-claim-optimizer:
1. รับ claims ทั้งล็อต (CSV/list)
2. ตรวจแต่ละเคสตาม 8 checkpoints
3. จัดกลุ่ม status: denied / at_risk / optimizable / ready
4. หา CC/MCC optimization opportunities → เพิ่ม RW
5. คำนวณ revenue impact (มูลค่าที่เพิ่มได้)
6. เรียง priority ตามมูลค่า (แก้เคสแพงก่อน)

Output: สรุปตาราง + total charge/denied/recoverable/optimization + action plan
