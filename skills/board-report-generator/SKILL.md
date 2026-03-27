---
name: board-report-generator
description: "สร้าง Board Report อัตโนมัติสำหรับ CEO/ผอ.โรงพยาบาล — รายงานประจำเดือน Financial, Operations, Quality, HR, Patient Experience พร้อม KPI dashboard ใช้ skill นี้เมื่อ: board report, รายงานกรรมการ, monthly report, KPI report, executive summary, รายงาน ผอ., management report, สรุปรายเดือน"
---

# Board Report Generator — รายงานคณะกรรมการบริหาร

สร้างรายงานประจำเดือนอัตโนมัติ ครอบคลุม 7 ด้านหลักของ รพ.

## วิธีใช้

### Step 1: รวบรวมข้อมูล
ถามผู้ใช้:
- เดือน/ปี ที่ต้องการ
- ชื่อโรงพยาบาล
- ข้อมูล KPI (ถ้ามี) หรือใช้ placeholder

### Step 2: สร้างรายงาน 7 ส่วน
อ่าน `templates/board-report-template.md` แล้วเติมข้อมูล

### Step 3: เปรียบเทียบกับ Benchmark
อ่าน KPI benchmarks จาก `~/.claude/skills/hospital-ceo-agent/references/hospital-kpi-benchmarks.md`
- 🟢 Green = meets/exceeds benchmark
- 🟡 Yellow = within 10% of benchmark
- 🔴 Red = below benchmark

### Step 4: Output
- Markdown format (แปลงเป็น Word ได้ด้วย /memento-docx)
- หรือ PDF ด้วย /memento-pdf

## Reference Files
| File | อ่านเมื่อ |
|------|----------|
| `templates/board-report-template.md` | ทุกครั้ง — template หลัก |
| `templates/kpi-summary-table.md` | สร้างตาราง KPI |
| `references/report-guidelines.md` | tips การเขียน report |
