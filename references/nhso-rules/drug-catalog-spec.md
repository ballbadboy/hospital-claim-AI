# Drug Catalogue Specification — สปสช.

> Source: คู่มือรหัสยามาตรฐาน TMT และโปรแกรม Drug Catalogue — สปสช.
> System: http://drug.nhso.go.th/drugcatalogue/ (ต้อง login)
> TMT Browser: http://tmt.this.or.th/
> Master TTMT: https://this.or.th/ (download MasterTTMT_20260316.zip)

## TMT Code Structure (Thai Medicines Terminology)

### TMT Hierarchy
```
SUBS (Substance)           ← ตัวยาสำคัญ เช่น clopidogrel
  ↓ IS_A
VTM (Virtual Therapeutic Moiety) ← ชื่อสามัญ เช่น clopidogrel
  ↓ IS_A
GP (Generic Product)       ← ยาสามัญ + รูปแบบ + ความแรง
  ↓ IS_A                     เช่น clopidogrel 75 mg film-coated tablet
GPU (Generic Product Use)  ← ยาสามัญ + หน่วยใช้
  ↓ IS_A                     เช่น clopidogrel 75 mg film-coated tablet, 1 tablet
GPP (Generic Product Pack) ← ยาสามัญ + บรรจุภัณฑ์
                              เช่น clopidogrel 75 mg film-coated tablet, 1 tablet, 28 x 1 tab

TP (Trade Product)         ← ชื่อการค้า + รูปแบบ + ความแรง
  ↓ IS_A                     เช่น PLAVIX (clopidogrel 75 mg) film-coated tablet
TPU (Trade Product Use)    ← ชื่อการค้า + หน่วยใช้
  ↓ IS_A
TPP (Trade Product Pack)   ← ชื่อการค้า + บรรจุภัณฑ์
```

**TMTID format:** ตัวเลข 6 หลัก (เช่น 229117, 254782)
**ระบบ Drug Catalogue สปสช. ใช้ TMTID ระดับ GPU (Generic Product Use)**

## Drug Catalogue Data Dictionary (21 fields)

| # | Field | คำอธิบาย | ตัวอย่าง |
|---|-------|---------|---------|
| 1 | **HospDrugCode** | รหัสยาของ รพ. | ABA100E |
| 2 | **ProductCat** | ประเภทยาและเวชภัณฑ์ (1-7) | 1 |
| 3 | **TMTID** | รหัส TPU Code ในฐานข้อมูล TMT | 1041959 |
| 4 | **SpecPrep** | ประเภทผลิตภัณฑ์ยาพิเศษ (R/X/F/M + 0-9, A-Z) | - |
| 5 | **GenericName** | ชื่อยาสามัญ (ถ้าเป็นยาผสมใช้ "+") | clopidogrel |
| 6 | **TradeName** | ชื่อทางการค้า | PLAVIX |
| 7 | **DSFCode** | รหัสรูปแบบยา | 1 |
| 8 | **DosageForm** | ชื่อรูปแบบยา | film-coated tablet |
| 9 | **Strength** | ความแรงยา | 75 mg |
| 10 | **Content** | ขนาดบรรจุ | 1 tablet |
| 11 | **UnitPrice** | ราคาขายต่อหน่วย | 2.50 |
| 12 | **Distributor** | ชื่อบริษัทผู้จำหน่าย | - |
| 13 | **Manufacturer** | ชื่อบริษัทผู้ผลิต | Sanofi |
| 14 | **ISED** | ประเภทบัญชียาหลัก (E/N/E*) | E |
| 15 | **NDC24** | รหัสยามาตรฐาน 24 หลัก กระทรวงสาธารณสุข | - |
| 16 | **PackSize** | กรณียาต้องขายเป็น pack | 28 |
| 17 | **PackPrice** | ราคาต่อหน่วยจ่ายแบบหีบห่อ | 70.00 |
| 18 | **UpdateFlag** | A=เพิ่ม, D=ยกเลิก, E=แก้ไข, U=แก้ราคา | A |
| 19 | **DateChange** | วันที่แก้ไข | 01/10/2568 |
| 20 | **DateUpdate** | วันที่เปลี่ยนราคาขาย | - |
| 21 | **DateEffective** | วันที่เริ่มใช้ (dd/mm/yyyy hh:mm) | 01/10/2568 00:00 |

## ProductCat (ประเภทยา) — Code 2

| รหัส | ความหมาย | หมายเหตุ |
|------|---------|---------|
| **1** | ยาแผนปัจจุบันที่เป็นผลิตภัณฑ์ทำ | ยาส่วนใหญ่ |
| **2** | ยาแผนปัจจุบันผลิตใช้เอง | เภสัชตำรับ รพ. |
| **3** | ยาแผนไทยที่เป็นผลิตภัณฑ์ทางการค้า | |
| **4** | ยาแผนไทยผลิตใช้เอง | |
| **5** | ยาแผนการรักษาทางเลือกอื่น | สมุนไพรจีน ฯลฯ |
| **6** | เวชภัณฑ์ | จ่ายผ่านห้องยา |
| **7** | อื่นๆ | |

**หมายเหตุ:** ยาแผนไทย (cat 3-4) ไม่มี TMT และเป็น ProductCat 3 หรือ 4 เท่านั้น

## SpecPrep (ผลิตภัณฑ์พิเศษ)

| ประเภท | ความหมาย |
|--------|---------|
| **R** | Repackaged — เปลี่ยนขนาดบรรจุ (R1, R2, ...) |
| **M** | Reformulated — เปลี่ยนรูปแบบ/ความแรง |
| **F** | Hospital Formula — ปรุงตามเภสัชตำรับ |
| **X** | Extemporaneous — เตรียมเฉพาะราย |
| *ว่าง* | ยาสำเร็จรูปปกติ |

## Cath Lab Drug List (ยาที่ใช้บ่อยในห้อง Cath Lab)

| Generic Name | Trade Name (ตัวอย่าง) | Dosage Form | Strength | ProductCat | ใช้สำหรับ |
|---|---|---|---|---|---|
| **clopidogrel** | PLAVIX, CLOPILET | film-coated tablet | 75 mg, 300 mg | 1 | Antiplatelet (DAPT) |
| **ticagrelor** | BRILINTA | film-coated tablet | 60 mg, 90 mg | 1 | Antiplatelet (DAPT) |
| **prasugrel** | EFFIENT | film-coated tablet | 5 mg, 10 mg | 1 | Antiplatelet (DAPT) |
| **aspirin** | ASA, ASPENT | tablet/enteric-coated | 81 mg, 100 mg, 300 mg | 1 | Antiplatelet |
| **heparin sodium** | HEPARIN | injection | 5,000 IU/mL, 25,000 IU/5mL | 1 | Anticoagulant (PCI) |
| **enoxaparin** | CLEXANE, LOVENOX | injection | 20 mg, 40 mg, 60 mg | 1 | LMWH |
| **eptifibatide** | INTEGRILIN | injection | 2 mg/mL, 0.75 mg/mL | 1 | GP IIb/IIIa inhibitor |
| **tirofiban** | AGGRASTAT | injection | 0.25 mg/mL | 1 | GP IIb/IIIa inhibitor |
| **nitroglycerin** | NTG | injection | 5 mg/mL | 1 | Vasodilator (IC) |
| **contrast media** | VISIPAQUE, OMNIPAQUE | injection | various | 6 | Iodinated contrast |
| **alteplase** | ACTILYSE | injection | 50 mg | 1 | Thrombolytic (STEMI) |
| **atorvastatin** | LIPITOR | film-coated tablet | 10, 20, 40, 80 mg | 1 | High-intensity statin |
| **rosuvastatin** | CRESTOR | film-coated tablet | 5, 10, 20, 40 mg | 1 | High-intensity statin |
| **morphine sulfate** | MORPHINE | injection | 10 mg/mL | 1 | Pain (STEMI) |

## TMT Lookup Sources

1. **TMT Browser (ออนไลน์):** http://tmt.this.or.th/TMTBrowser.dll/
2. **Master TTMT File (download):** https://this.or.th/ → ต้อง login → MasterTTMT_20260316.zip
3. **Drug Code สปสช. (สืบค้น):** http://drug.nhso.go.th/DrugCode/ → สืบค้นรหัสยามาตรฐาน
4. **Drug Catalogue (จัดทำ):** http://drug.nhso.go.th/drugcatalogue/ → ต้อง login รพ.
5. **โปรแกรมยา clopidogrel:** nhso.go.th → บริการออนไลน์ → ระบบยา → โปรแกรมยา clopidogrel

## ข้อสำคัญสำหรับ AI Agent

1. **HospDrugCode ≠ TMTID** — ทุก รพ. มี HospDrugCode เฉพาะ ต้อง map กับ TMTID
2. **Drug Catalogue ต้อง approve ก่อนใช้** — ส่งรายการยาเข้า Drug Catalogue → สปสช. ตรวจ → ผ่าน/ไม่ผ่าน
3. **ยาที่ไม่มีใน Drug Catalogue ของ รพ. จะเบิกไม่ได้** → ติด C error
4. **Clopidogrel deny** (เคสจริง HC09) — สาเหตุที่เป็นไปได้:
   - HospDrugCode ไม่ได้ map กับ TMTID
   - TMTID ไม่อยู่ใน Drug Catalogue ที่ approve แล้ว
   - ProductCat ผิด
   - ราคา UnitPrice ไม่ตรง
5. **Master TTMT ต้อง update ล่าสุด** — version ปัจจุบัน MasterTTMT_20260316
