---
name: financial-simulator
description: "จำลองสถานการณ์การเงินโรงพยาบาล (What-if Analysis) — เปลี่ยนตัวแปรแล้วดูผลกระทบทันที ใช้ skill นี้เมื่อ: what-if, จำลองการเงิน, เพิ่มเตียง, ปรับเงินเดือน, เปลี่ยน payer mix, ลงทุน, เปิดศูนย์ใหม่, financial projection, feasibility, budget, ถ้าเพิ่ม...จะ..., ถ้าลด...จะ..."
---

# Financial Simulator — What-if Analysis

จำลองสถานการณ์การเงิน รพ. — ปรับตัวแปร ดูผลทันที

## วิธีใช้

### Step 1: ข้อมูล Baseline
ถามผู้ใช้ (หรือใช้ค่า default รพ.เอกชน 100 เตียง):
- จำนวนเตียง, Occupancy rate
- Revenue รวม, Expenses รวม
- Staff count, Average salary
- Payer mix (UC/SSO/Private/Cash)

### Step 2: เลือก Scenario
เสนอ 6 scenarios พร้อมกัน หรือให้ผู้ใช้กำหนดเอง:
1. เพิ่มเตียง (+N เตียง)
2. ปรับเงินเดือนพยาบาล (+X%)
3. เปลี่ยน Payer mix
4. เปิดศูนย์ใหม่ (cancer/heart/etc.)
5. ลด ALOS (-X วัน)
6. Drug cost optimization (switch generic)

### Step 3: คำนวณ
อ่าน `references/simulation-models.md` ใช้สูตรคำนวณ

### Step 4: แสดงผล
```
╔══════════════════════════════════════════════╗
║  FINANCIAL SIMULATION RESULT                 ║
╠══════════════════════════════════════════════╣
║  Scenario: เพิ่ม 20 เตียง                     ║
║  Current → Projected                         ║
║  Revenue:     ฿120M → ฿144M (+20%)           ║
║  Expenses:    ฿108M → ฿122M (+13%)           ║
║  Net Margin:  10% → 15.3% (+5.3 pp)         ║
║  ROI:         18 months                      ║
║  Risk Level:  Medium                         ║
╚══════════════════════════════════════════════╝
```

## References
| File | อ่านเมื่อ |
|------|----------|
| `references/simulation-models.md` | ทุก scenario |
| `references/industry-benchmarks.md` | validate ตัวเลข |
| `references/roi-calculations.md` | คำนวณ ROI |
