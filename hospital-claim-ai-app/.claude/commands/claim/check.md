ตรวจสอบเคส Cath Lab ก่อนส่งเบิก สปสช.

Input: $ARGUMENTS (ข้อมูลเคส: AN, HN, PDx, Procedures, stent, วันที่ admit/discharge)

ใช้ skill cathlab-claim-checker ตรวจ 8 checkpoints:
1. Basic Data — PDx, CID, วันที่
2. Dx-Proc Match — ICD-10 ตรงกับหัตถการ
3. Device Docs — stent serial/lot, GPO VMI
4. 16-File Completeness — format, LOS
5. Timing — ส่งภายใน 30 วัน, Authen Code
6. CC/MCC Optimization — หา coding เพิ่ม DRG weight
7. DRG Verification — group ถูกต้อง
8. Drug/Lab Catalog — TMT code ตรง

แสดงผล: Score, CRITICAL/WARNING/PASS, Expected DRG + RW + payment estimate
ถ้า score < 70 → แจ้งเตือนว่าไม่ควรส่ง
