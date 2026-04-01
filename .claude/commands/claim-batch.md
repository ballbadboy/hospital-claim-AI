รัน Auto Claim Pipeline จากไฟล์ CSV ที่ผู้ใช้แนบมา

1. หาไฟล์ CSV ที่ผู้ใช้ upload หรือระบุ path
2. รันคำสั่ง: `python scripts/auto_claim_pipeline.py <csv_path>`
3. แสดงสรุปผล: จำนวนเคส, deny, pass, total loss, เวลา
4. บอก path ของ DOCX ที่สร้างได้

ถ้าผู้ใช้ไม่ได้แนบไฟล์ ให้ถามว่า CSV อยู่ที่ไหน
