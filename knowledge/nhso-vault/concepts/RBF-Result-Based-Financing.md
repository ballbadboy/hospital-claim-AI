---
type: concept
name: RBF (Results-Based Financing)
aliases: [การจ่ายตามผลงาน, ราคา RBF, rbf]
related_entities: [entities/สปสช]
related_concepts: [concepts/seamless-for-dmis, concepts/ตรวจสุขภาพกลุ่มวัย, concepts/ใบเบิกจ่าย]
sources: [sources/ZCKCYr0bO8U]
last_updated: 2026-04-13
---

# RBF — Results-Based Financing

**RBF** (Results-Based Financing) คือกลไกการจ่ายชดเชยของ [[entities/สปสช]] ที่จ่ายตามผลงานที่หน่วยบริการทำได้จริง ใช้กับบริการตรวจสุขภาพที่จำเป็นตามกลุ่มวัย ([[concepts/ตรวจสุขภาพกลุ่มวัย]])

## การดูรายงาน RBF ใน Seamless for DMIS

เส้นทาง: Portal → **Krungthai Digital Health Platform** → DMIS → **ข้อมูล** → **RBF**

รายงานที่มี:
- **RBF : ราคา RBF และ SUMMARY** — ยอดรวมของหน่วยบริการ
- **RBF : ราคา RBF และ INDIVIDUAL** — รายละเอียดรายบุคคล

→ ดูขั้นตอนเต็มใน [[concepts/Seamless-DMIS]]

## อัตราชดเชยตัวอย่าง (จากวิดีโอ)

| รายการ | รวมเงิน |
|--------|---------|
| รายการที่ 1 | 80.00 บาท |
| รายการที่ 2 | 80.00 บาท |
| รายการที่ 3 | 120.00 บาท |

**หมายเหตุ:** คอลัมน์ "ราคาเบิก" อาจแสดง 0.00 แต่ "รวมเงิน" คือยอดชดเชยจริงที่ สปสช. จ่ายให้ (fixed-rate)

## PS CODE

รหัสประจำรายการบริการ (PS CODE) ใช้ระบุว่ารายการตรวจสุขภาพใดที่ขอชดเชย ปรากฏในรายงาน RBF ทุก record

## Sources

- [[sources/วิธีการตรวจสอบยอดเงินโอนเข้ารายการตรวจสุขภาพที่จำเป็นตามกลุ่มวัย-ZCKCYr0bO8U]] — สาธิตการดูรายงาน RBF สำหรับตรวจสุขภาพกลุ่มวัย
