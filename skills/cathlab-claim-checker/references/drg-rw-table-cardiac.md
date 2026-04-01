# Thai DRG v6.3.3 — Cardiac RW Table (MDC 05)

> Source: Thai DRG and Relative Weight Version 6.3.3, Appendix G
> Published: December 2020 by สำนักพัฒนากลุ่มโรคร่วมไทย (สรท./TCMC)
> Payment Formula: **DRG Payment = AdjRW × Base Rate**
> Base Rate ปีงบ 69: ในเขต **8,350** / นอกเขต **9,600** บาท/AdjRW

## Column Definitions

| Column | Meaning |
|--------|---------|
| DRG | DRG code (5 digits: DDDDX where X=complexity level 0-4,9) |
| RW | Relative Weight (ค่าน้ำหนักสัมพัทธ์) |
| WtLOS | Weighted average Length of Stay (วันนอนเฉลี่ย) |
| OT | Outlier Trim point (จุดตัดวันนอนเกิน) |
| RW0d | RW สำหรับกรณีนอน ≤24 ชม. (≤1,440 นาที) |
| OF | Optimization Factor |

## PCL Formula (สูตรคำนวณ Patient Complexity Level)

```
PCL = Σ(Li × r^(i-1))  where r = 0.82
```
- Li = DCL ค่าที่ i (เรียงจากมากไปน้อย)
- PCL 0-9 (ปัดเศษ: <0.5 ปัดทิ้ง, ≥0.5 ปัดขึ้น, >9 เป็น 9)

## AdjRW Formula (สูตรปรับค่า RW ตามวันนอน)

- LOS ≤ OT → AdjRW = RW (ไม่ปรับ)
- LOS > OT → AdjRW = RW + per diem (ดู Appendix H)
- LOS ≤ 24 ชม. → ใช้ RW0d

---

## Cardiac Surgery & Transplant (Pre-MDC / MDC 05 Surgical)

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05019 | 18.3432 | 24.17 | 73 | 8.0710 | Valve replacement and open valvuloplasty w cath |
| 05020 | 13.2288 | 12.87 | 39 | 8.9956 | Valve replacement and open valvuloplasty wo sig CCC |
| 05021 | 15.9402 | 19.07 | 57 | 8.9956 | Valve replacement and open valvuloplasty w min CCC |
| 05022 | 19.3869 | 24.40 | 73 | 8.9956 | Valve replacement and open valvuloplasty w mod CCC |
| 05039 | 29.3120 | 21.98 | 66 | 12.8973 | Coronary bypass with PTCA |
| 05049 | 23.1477 | 24.44 | 73 | 10.1850 | Coronary bypass with cath |
| 05059 | 18.1845 | 13.75 | 41 | 12.3655 | Coronary bypass |

## PCI (Percutaneous Coronary Intervention)

### Acute MI with PCI

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| **05259** | **32.5414** | **22.89** | **69** | **14.3182** | **Acute MI w CAB or VSD repair w PTCA** |
| **05269** | **22.2634** | **21.59** | **65** | **9.7959** | **Acute MI w CAB or VSD repair wo PTCA** |
| **05270** | **10.0192** | **4.31** | **13** | **9.1175** | **Acute MI w multiple vessel PTCA wo sig CCC** |
| **05271** | **12.1597** | **8.90** | **27** | **10.2141** | **Acute MI w multiple vessel PTCA w min CCC** |
| **05290** | **8.6544** | **3.57** | **11** | **7.8755** | **Acute MI w single vessel PTCA wo sig CCC** |
| **05291** | **11.4820** | **6.54** | **20** | **9.6449** | **Acute MI w single vessel PTCA w min CCC** |

### Cardiac Cath/Angiography

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05210 | 2.7603 | 3.87 | 12 | 2.5119 | Cardiac cath/angiography for complex Dx wo sig CCC |
| 05211 | 5.5237 | 8.85 | 27 | 4.6399 | Cardiac cath/angiography for complex Dx w min CCC |
| 05212 | 9.1898 | 13.12 | 39 | 6.2491 | Cardiac cath/angiography for complex Dx w mod CCC |
| 05220 | 2.1360 | 2.16 | 6 | 2.1360 | Cardiac cath/angiography wo sig CCC |
| 05221 | 3.0615 | 3.73 | 11 | 2.7860 | Cardiac cath/angiography w min CCC |
| 05222 | 5.3864 | 10.58 | 32 | 4.0937 | Cardiac cath/angiography w mod CCC |

### Percutaneous Cardiovascular Procedures (PCI without acute MI)

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05230 | 6.8786 | 2.14 | 6 | 6.8786 | Percut cardiovas proc w stent insertion wo sig CCC |
| 05231 | 8.0392 | 2.56 | 8 | 8.0392 | Percut cardiovas proc w stent insertion w min CCC |
| 05232 | 9.8158 | 5.19 | 16 | 8.9324 | Percut cardiovas proc w stent insertion w mod CCC |
| 05240 | 6.5804 | 2.18 | 7 | 6.5804 | Percut cardiovas proc wo sig CCC |
| 05241 | 7.7565 | 2.76 | 8 | 7.7565 | Percut cardiovas proc w min CCC |
| 05242 | 9.2851 | 5.75 | 17 | 8.4494 | Percut cardiovas proc w mod CCC |

## Other Cardiac Procedures

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05060 | 9.7878 | 5.53 | 17 | 8.9069 | Other cardiothoracic proc wo sig CCC |
| 05061 | 12.2013 | 13.69 | 41 | 9.0047 | Other cardiothoracic proc w min CCC |
| 05079 | 22.4312 | 17.70 | 53 | 13.4588 | Thoracoabdominal proc combination |
| 05080 | 8.4539 | 7.10 | 21 | 7.1013 | Major cardiovascular proc wo sig CCC |
| 05081 | 12.0728 | 15.46 | 46 | 7.2436 | Major cardiovascular proc w min CCC |
| 05090 | 4.5621 | 14.57 | 44 | 3.1022 | Major amputation for CVS disorders wo sig CCC |
| 05091 | 8.0812 | 23.82 | 71 | 3.5557 | Major amputation for CVS disorders w min CCC |
| 05109 | 9.5307 | 12.57 | 38 | 6.4809 | Perm pacemaker proc comb for AMI, HF, Shock |
| 05110 | 3.2787 | 4.50 | 14 | 2.9836 | Perm pacemaker proc comb wo sig CCC |
| 05111 | 4.8684 | 6.98 | 21 | 4.0895 | Perm pacemaker proc comb w min CCC |
| 05112 | 7.6522 | 13.53 | 41 | 5.2035 | Perm pacemaker proc comb w mod CCC |
| 05120 | 4.9904 | 3.94 | 12 | 4.5413 | Automat cardioverter proc wo sig CCC |
| 05121 | 7.3820 | 7.09 | 21 | 6.2008 | Automat cardioverter proc w min CCC |
| 05122 | 9.9119 | 15.57 | 47 | 6.2008 | Automat cardioverter proc w mod CCC |
| 05130 | 8.7454 | 9.00 | 27 | 7.3461 | Simple cardiothoracic proc wo sig CCC |
| 05131 | 11.8708 | 12.03 | 36 | 8.0722 | Simple cardiothoracic proc w min CCC |
| 05149 | 5.7297 | 3.22 | 10 | 5.2140 | Cardiac electrophysiologic proc |
| 05150 | 3.3140 | 3.56 | 11 | 3.0157 | Other vascular proc wo sig CCC |
| 05151 | 6.0702 | 8.57 | 26 | 5.0990 | Other vascular proc w min CCC |
| 05152 | 8.9979 | 18.51 | 56 | 5.0990 | Other vascular proc w mod CCC |

## Peripheral Stent / Amputation

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05310 | 3.9910 | 2.42 | 7 | 3.9910 | Peripheral stent insertion wo sig CCC |
| 05311 | 7.5004 | 10.10 | 30 | 5.7003 | Peripheral stent insertion w min CCC |
| 05160 | 1.6835 | 6.64 | 20 | 1.4141 | Minor amputation wo sig CCC |
| 05161 | 4.0676 | 12.92 | 39 | 2.7659 | Minor amputation w min CCC |

## Medical Cardiac DRGs (No OR Procedure)

### Acute MI (Medical Management)

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05500 | 2.4222 | 3.56 | 11 | 2.2042 | Acute MI w major comp w thrombol inj wo sig CCC |
| 05501 | 6.0220 | 10.06 | 30 | 4.5767 | Acute MI w major comp w thrombol inj w min CCC |
| 05510 | 2.1349 | 3.59 | 11 | 1.9428 | Acute MI w thrombol inj wo sig CCC |
| 05511 | 2.6876 | 5.20 | 16 | 2.4457 | Acute MI w thrombol inj w min CCC |
| 05520 | 1.5851 | 4.86 | 15 | 1.4424 | Acute MI w major comp, not transferred wo sig CCC |
| 05521 | 2.9432 | 7.45 | 22 | 2.4723 | Acute MI w major comp, not transferred w min CCC |
| 05522 | 4.0802 | 9.40 | 28 | 3.1009 | Acute MI w major comp, not transferred w mod CCC |
| 05523 | 6.7633 | 13.91 | 42 | 4.5990 | Acute MI w major comp, not transferred w maj CCC |
| 05530 | 1.0396 | 4.00 | 12 | 0.9460 | Acute MI, not transferred wo sig CCC |
| 05531 | 1.3637 | 4.94 | 15 | 1.2410 | Acute MI, not transferred w min CCC |
| 05532 | 2.0671 | 6.88 | 21 | 1.7363 | Acute MI, not transferred w mod CCC |
| 05533 | 3.2701 | 9.33 | 28 | 2.4853 | Acute MI, not transferred w maj CCC |

### Heart Failure

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05550 | 0.6831 | 3.36 | 10 | 0.6216 | Heart failure and shock wo sig CCC |
| 05551 | 1.3294 | 5.24 | 16 | 1.2098 | Heart failure and shock w min CCC |
| 05552 | 2.9495 | 8.57 | 26 | 2.4776 | Heart failure and shock w mod CCC |
| 05553 | 5.5413 | 12.72 | 38 | 3.7681 | Heart failure and shock w maj CCC |
| 05554 | 7.3352 | 18.81 | 56 | 3.8143 | Heart failure and shock w ext CCC |

### Coronary Atherosclerosis & Unstable Angina

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05590 | 0.5561 | 2.31 | 7 | 0.5561 | Coronary atherosclerosis and unstable angina wo sig CCC |
| 05591 | 0.8915 | 3.55 | 11 | 0.8113 | Coronary atherosclerosis and unstable angina w min CCC |
| 05592 | 1.6921 | 5.75 | 17 | 1.5398 | Coronary atherosclerosis and unstable angina w mod CCC |
| 05593 | 2.9651 | 8.20 | 25 | 2.4907 | Coronary atherosclerosis and unstable angina w maj CCC |
| 05594 | 6.3327 | 12.71 | 38 | 4.3062 | Coronary atherosclerosis and unstable angina w ext CCC |

### Arrhythmia

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05630 | 0.8116 | 2.13 | 6 | 0.8116 | Major arrhythmia and cardiac arrest wo sig CCC |
| 05631 | 1.9084 | 3.87 | 12 | 1.7366 | Major arrhythmia and cardiac arrest w min CCC |
| 05632 | 3.6236 | 6.68 | 20 | 3.0438 | Major arrhythmia and cardiac arrest w mod CCC |
| 05633 | 7.4736 | 12.38 | 37 | 5.0820 | Major arrhythmia and cardiac arrest w maj CCC |

### Other Circulatory

| DRG | RW | WtLOS | OT | RW0d | Description |
|-----|-----|-------|-----|------|-------------|
| 05600 | 0.3341 | 1.91 | 6 | 0.3341 | Hypertension wo sig CCC |
| 05601 | 0.8421 | 3.45 | 10 | 0.7663 | Hypertension w min CCC |
| 05602 | 2.0261 | 6.29 | 19 | 1.7019 | Hypertension w mod CCC |
| 05603 | 3.7381 | 9.10 | 27 | 2.8409 | Hypertension w maj CCC |
| 05660 | 0.3602 | 1.63 | 5 | 0.3602 | Chest pain, syncope and collapse wo sig CCC |
| 05661 | 0.6192 | 2.48 | 7 | 0.6192 | Chest pain, syncope and collapse w min CCC |
| 05662 | 1.2428 | 4.29 | 13 | 1.1309 | Chest pain, syncope and collapse w mod CCC |
| 05663 | 1.9439 | 5.93 | 18 | 1.7689 | Chest pain, syncope and collapse w maj CCC |
| 05690 | 0.6719 | 1.81 | 5 | 0.6719 | Acute MI, transferred wo sig CCC |
| 05691 | 1.6614 | 3.90 | 12 | 1.5119 | Acute MI, transferred w min CCC |
| 05692 | 3.0483 | 6.32 | 19 | 2.5606 | Acute MI, transferred w mod CCC |
| 05693 | 5.3159 | 10.78 | 32 | 4.0401 | Acute MI, transferred w maj CCC |

---

## Payment Calculation Examples (Base Rate 8,350 บาท)

### Example 1: STEMI + Primary PCI (Single vessel)
- DRG 05290 (Acute MI w single vessel PTCA wo sig CCC)
- RW = 8.6544, AdjRW ≈ 8.65
- **Payment = 8.65 × 8,350 = 72,228 บาท**

### Example 2: STEMI + PCI + MCC (HF + CKD4)
- DRG 05291 (Acute MI w single vessel PTCA w min CCC)
- RW = 11.4820, AdjRW ≈ 11.48
- **Payment = 11.48 × 8,350 = 95,858 บาท**
- Difference from wo CCC: **+23,630 บาท** (ผลจาก CC/MCC)

### Example 3: Diagnostic Cath only (Chronic IHD)
- DRG 05220 (Cardiac cath/angiography wo sig CCC)
- RW = 2.1360, AdjRW ≈ 2.14
- **Payment = 2.14 × 8,350 = 17,869 บาท**

### Example 4: Elective PCI with stent (non-acute)
- DRG 05230 (Percut cardiovas proc w stent insertion wo sig CCC)
- RW = 6.8786, AdjRW ≈ 6.88
- **Payment = 6.88 × 8,350 = 57,448 บาท**

### Example 5: Acute MI medical (no PCI)
- DRG 05530 (Acute MI, not transferred wo sig CCC)
- RW = 1.0396
- **Payment = 1.04 × 8,350 = 8,684 บาท**
- vs PCI DRG 05290 RW 8.65 = 72,228 บาท
- **ผลต่าง: ~63,544 บาท** ← นี่คือสาเหตุที่ Dx-Proc match สำคัญมาก

---

## Key Insights for Cath Lab Claim Optimization

1. **Acute MI + PCI (05290) vs Medical MI (05530):** RW ต่างกัน 8.3x → ถ้าทำ PCI แต่ไม่ code procedure = เสียเงิน ~63,000 บาท
2. **CC/MCC impact (05290 vs 05291):** เพิ่ม CC/MCC = +23,630 บาท
3. **Cath only (05220) vs PCI (05230):** RW ต่างกัน 3.2x → ถ้าทำ PCI แต่ code แค่ cath = เสียเงิน ~40,000 บาท
4. **LOS > OT:** ถ้านอนเกิน OT จะได้ per diem เพิ่ม (ดู Appendix H)
5. **LOS ≤ 24 ชม.:** ใช้ RW0d ซึ่งต่ำกว่า RW ปกติ (~70-90%)
