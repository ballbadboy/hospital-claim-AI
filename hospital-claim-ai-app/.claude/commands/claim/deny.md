วิเคราะห์สาเหตุ claim ถูก deny จาก สปสช.

Input: $ARGUMENTS (AN, deny codes เช่น HC09/HC13/IP01/C438, deny reason text)

ใช้ skill deny-analyzer:
1. รับ deny codes + denied items
2. จำแนก category (device/coding/drug/eligibility/timing/payment)
3. หา root cause — อธิบายสาเหตุชัดเจน
4. แนะนำวิธีแก้ไข (fix steps) ที่ actionable
5. ประเมิน recovery chance (%)
6. ถ้าควร appeal → ร่าง appeal draft อัตโนมัติ
7. ถ้าแก้ข้อมูลได้ → แนะนำแก้ ADP/DRU/DIA file แล้วส่งใหม่

Recommended action: auto_fix / appeal / escalate / write_off
