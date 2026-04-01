# Thai DRG v6.3 — Cardiac Grouping (MDC 05)

## DRG Grouping Logic for Cath Lab Cases

### Grouping Flow
1. PDx determines MDC (I20-I25 → MDC 05: Diseases of Circulatory System)
2. Check OR Procedure list → Surgical or Medical DRG
3. Cardiac cath (37.21-37.23) = Non-OR procedure affecting DRG
4. PCI (36.01-36.09) = OR Procedure → Surgical DRG
5. Check CC/MCC (PCCL level) → final DRG assignment

### Surgical DRGs (มี OR Procedure)

| Scenario | PDC | DC Range | DRG Pattern |
|----------|-----|----------|-------------|
| PCI with DES + Acute MI | 5PA | Varies | Acute MI w/ PCI (สูงสุด) |
| PCI with BMS + Acute MI | 5PA | Varies | Acute MI w/ PCI |
| PCI + non-acute diagnosis | 5PA | Varies | PTCA wo sig CCC (ต่ำกว่า) |
| CABG | 5PB | Varies | Cardiac valve/major cardiothoracic |
| Pacemaker/ICD implant | 5PC | Varies | Perm pacemaker implant |

### Medical DRGs (ไม่มี OR Procedure)

| Scenario | DC Range | DRG Pattern |
|----------|----------|-------------|
| Acute MI (medical, no PCI) | 0510-0519 | AMI discharged alive |
| Acute MI died | 0510-0519 | AMI expired |
| Circ dx with cardiac cath | 0550-0559 | Circ disorders w/ cath |
| Circ dx without cath | 0560-0569 | Circ disorders wo cath |
| Heart failure | 0570-0579 | Heart failure |
| Chest pain | 0590-0599 | Chest pain |

### CC/MCC Impact on DRG Weight

Thai DRG ใช้ PCCL (Patient Clinical Complexity Level) ในการปรับ RW:
- PCCL 0: ไม่มี CC → base RW
- PCCL 1-2: มี CC → RW สูงขึ้นเล็กน้อย
- PCCL 3-4: มี MCC → RW สูงขึ้นมาก

**DCL (Diagnosis Complexity Level):**
แต่ละ SDx มีค่า DCL ต่างกันในแต่ละ DC
- DCL 0 = ไม่เป็น CC ใน DC นี้
- DCL 1-4 = CC ระดับต่ำ-สูง

**CC Exclusion:**
บาง SDx จะถูกตัดออกจาก CC ถ้าเกี่ยวข้องกับ PDx
ตัวอย่าง: I50 (HF) อาจไม่นับเป็น CC ถ้า PDx เป็น I21 (MI) ใน DC บางตัว
→ ตรวจ CC Exclusion List (Appendix F2) เสมอ

### Relative Weight (RW) Estimation

| DRG Group | Approx RW | Approx Payment (base 8,350) |
|-----------|-----------|------------------------------|
| Acute MI w/ PCI + MCC | 3.5-5.0 | 29,225-41,750 |
| Acute MI w/ PCI wo CCC | 2.5-3.5 | 20,875-29,225 |
| Acute MI medical + MCC | 1.5-2.5 | 12,525-20,875 |
| Acute MI medical wo CCC | 0.8-1.5 | 6,680-12,525 |
| Circ dx w/ cath + MCC | 1.5-2.5 | 12,525-20,875 |
| Circ dx w/ cath wo CCC | 0.8-1.5 | 6,680-12,525 |
| PTCA wo CCC | 1.5-2.5 | 12,525-20,875 |

*หมายเหตุ: RW เป็นค่าประมาณ — ค่าจริงดูจาก RW table ของ TDRG v6.3.3*
*Base rate ปีงบ 69: ในเขต 8,350 / นอกเขต 9,600 บาท/Adj.RW*

### LOS Adjustment
Thai DRG ปรับ RW ตาม Length of Stay:
- LOS < Trim Low → ลด RW (outlier สั้น)
- LOS ปกติ → RW ตามกลุ่ม
- LOS > Trim High → เพิ่ม RW (outlier ยาว — per diem)

สำหรับ Cath Lab:
- PCI ปกติ: LOS 2-5 วัน
- Acute MI + PCI: LOS 3-7 วัน
- Complicated: LOS 7-14+ วัน
