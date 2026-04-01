ร่างหนังสืออุทธรณ์ claim ถูก deny ส่ง สปสช.

Input: $ARGUMENTS (ข้อมูลเคส: AN, HN, deny codes, deny reason, PDx, Procedures)

ใช้ skill appeal-drafter:
1. รับข้อมูลเคส + deny reason
2. เลือก appeal strategy (แก้ข้อมูล / ขอทบทวน DRG / อุทธรณ์ทางการ / ขอผ่อนผัน)
3. ร่างหนังสืออุทธรณ์ภาษาราชการไทย
4. แนะนำเอกสารแนบตามประเภท deny
5. ถ้าต้องการ DOCX → รัน scripts/generate_appeal.py

Output: หนังสืออุทธรณ์พร้อมส่ง + รายการเอกสารแนบ
Timeline: อุทธรณ์ได้ 2 ครั้ง, ครั้งละ 15 วันทำการ
