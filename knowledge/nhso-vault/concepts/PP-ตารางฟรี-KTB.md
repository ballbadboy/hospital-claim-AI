---
aliases: [PP-free-schedule-KTB]
type: concept
tags: [billing, PP, KTB, procedure, free-schedule, innovation-unit]
sources: [31WgTss5e5s]
last_updated: 2026-04-13
---

# PP Free Schedule — การเบิกจ่ายผ่าน KTB Digital Health Platform

## Definition

ตั้งแต่ปีงบประมาณ 2568 เป็นต้นมา **บริการส่งเสริมสุขภาพและป้องกันโรค (PP) แบบ Free Schedule ทั้งหมด** ต้องเบิกจ่ายผ่าน **KTB Digital Health Platform (Krungthai Digital Health Platform)** ไม่ใช่ผ่าน e-Claim

## รายการที่เบิกผ่าน KTB

- วัคซีนต่างๆ (เช่น วัคซีนไข้หวัดใหญ่, HB, HC)
- บริการคัดกรองมะเร็ง (เช่น มะเร็งปากมดลูก, มะเร็งลำไส้ใหญ่)
- บริการส่งเสริมสุขภาพอื่นๆ ที่อยู่ใน PP Free Schedule
- ฟิตเนส/กิจกรรมส่งเสริมสุขภาพ (Fit Test)

## วิธีดำเนินการ

1. **บันทึกบริการ** ในระบบ HIS ของหน่วยบริการ (สำคัญ — ถ้าเป็น Paperless ต้องมีข้อมูลใน HIS)
2. **สร้างใบเบิกจ่าย** ใน KTB Digital Health Platform
3. **ตรวจสอบสถานะ** ผ่านระบบ Seamless for DMIS → ไอคอน KTB DHP → REP Summary
4. **ตรวจสอบยอดโอน** ผ่าน [[concepts/Smart-Money-Transfer-โอนเงินอัจฉริยะ]]

## ข้อสังเกตสำคัญ

- ถ้าสร้างใบเบิกจ่ายแล้วสถานะ **"รออนุมัติ"** → ข้อมูลยังไม่ถูกนำมาประมวลผล → ต้องส่งรายละเอียดเพิ่มเติมให้ทีมงาน สปสช.
- หน่วยบริการที่ **ไม่บันทึกใน HIS** มีความเสี่ยงถูกตรวจสอบ เพราะข้อมูลใน HIS มีรายละเอียดมากกว่าที่ส่งเบิก
- หน่วยที่บันทึกกระดาษต้องเก็บเวชระเบียนไว้เป็นหลักฐาน

## Related Concepts

- [[concepts/KTP-Digital-Health-Platform]] — รายละเอียดระบบ KTB DHP
- [[concepts/Seamless-DMIS]] — ตรวจสอบรายงาน REP ผ่าน KTB path
- [[concepts/PP-กองทุนส่งเสริมสุขภาพ-ปี69]] — นโยบาย PP ปีงบประมาณ 2569
- [[concepts/ใบเบิกจ่าย]] — กระบวนการสร้างใบเบิก

## Source Videos

- [[sources/สปสชตอบทุกข้อสงสัยการเบิกจ่าย-ครั้งที่-80-31WgTss5e5s]] — ครั้งที่ 80: ยืนยัน PP Free Schedule ทั้งหมดเบิกผ่าน KTB, วัคซีนไข้หวัดใหญ่, ฟิตเนส, กรณีรออนุมัติ
