# แนวทางมาตรฐานการให้รหัสโรค (Standard Coding Guidelines) ฉบับปรับปรุง 2026

> แหล่งที่มา: กองยุทธศาสตร์และแผนงาน สำนักงานปลัดกระทรวงสาธารณสุข กระทรวงสาธารณสุข
> สถานะ: ฉบับปรับปรุง (2026) — บังคับใช้

---

## สรุปจุดเปลี่ยนสำคัญ (Quick Reference)

| หัวข้อ | สิ่งที่เปลี่ยน | ผลกระทบ DRG/Claim |
|--------|--------------|-------------------|
| R65 SIRS | **เลิกใช้แล้ว** | ห้ามใช้ R65 เป็น SDx อีกต่อไป |
| Sepsis | **ห้ามเป็น PDx** → ใช้ organ infection เป็น PDx, sepsis (A41.9) เป็น SDx | PDx ผิด = DRG ผิดทั้งเคส |
| Septic shock (R57.2) | เป็น PDx ได้เฉพาะกรณีไม่พบ source of infection | ปกติต้องเป็น SDx |
| DM foot | ต้องระบุ neuropathy (E11.4†) หรือ PVD (E11.5†) หรือทั้งคู่ (E11.7†) | เพิ่ม CC/MCC ได้ |
| Heart failure | ต้องระบุ EF: HFpEF (>50%), HFmrEF (41-49.9%), HFrEF (<40%) | specific code = RW สูงกว่า |
| CKD 4-5 | **บังคับลงรหัสทุกกรณี** ในผู้ป่วยใน | N18.4 = MCC, เพิ่ม RW |
| Anemia | ต้อง code เมื่อ severe จนต้องให้เลือด/ตรวจเพิ่ม | code ถูก = CC เพิ่ม |
| Cancer | 8 กฎสำหรับ primary/secondary/history | PDx ผิดตำแหน่ง = DRG ผิด |
| CVA/Stroke | ต้องระบุ embolism/thrombosis + territory | specific code = RW สูงกว่า |
| Obesity | ใช้ Asian BMI cutoff (≥25 = Class I) | Obesity Class III = CC |

---

## ข้อ 1-2: Sepsis / Septic Shock

### กฎสำคัญ
- **R65.- (SIRS) เลิกใช้แล้ว** ตาม International conference on sepsis
- **Sepsis = SDx เสมอ** ห้ามใช้เป็น PDx
- ใช้ **qSOFA score ≥2** ร่วมกับภาวะติดเชื้อ ในการวินิจฉัย

### qSOFA Score (≥2 ข้อ = Sepsis)
1. หายใจ ≥22 ครั้ง/นาที
2. GCS <14
3. SBP <100 mmHg

### เกณฑ์การให้รหัส Sepsis

| สถานการณ์ | PDx | SDx |
|-----------|-----|-----|
| พบ organ infection + sepsis | Organ infection (เช่น N10, K81.0) | A41.9 Sepsis |
| Hemoculture ขึ้นเชื้อ + ไม่พบ organ | เชื้อที่พบ (เช่น A41.5 E.coli) | — |
| ไม่พบเชื้อ ไม่พบ organ + มีอาการ sepsis | A49.9 / B99 / R50.9 | A41.9 Sepsis |
| ไม่พบเชื้อ + septic shock | **R57.2 Septic shock** | A41.9 Sepsis |
| มี septic shock ร่วม (กรณีอื่น) | ตามข้างบน | R57.2 + A41.9 |

### เกณฑ์ Septic Shock
1. MAP <60 หรือ SBP <90 หรือ SBP ลดจากเดิม 40 mmHg
2. Poor tissue perfusion (เท้าเย็น, เหงื่อแตก, หัวใจเต้นเร็ว, ปัสสาวะน้อย)
3. ไม่ตอบสนอง IV fluid ≥1 ชม. หรือต้องใช้ vasopressor
4. Lactate >2 mmol/L (สนับสนุน ไม่จำเป็นต้องมี)

---

## ข้อ 3: HIV Staging

- ผู้ป่วย admit ด้วยติดเชื้อ/มะเร็ง → ติดเชื้อ/มะเร็ง = PDx, HIV = SDx
- แต่เมื่อให้รหัส HIV associate → HIV = PDx, ติดเชื้อ/มะเร็ง = SDx
- ICD-11: Stage 1-4 mapping (B20-B24 → 1C62.x)

---

## ข้อ 4: Viral Hepatitis

- Cirrhosis/Hepatoma จาก viral hepatitis → **สามารถให้ viral hepatitis เป็นโรคร่วมได้**
- เหตุผล: เข้าเกณฑ์ WHO comorbidity, ต้องกิน antiviral ตลอดชีวิต
- **"ไม่รักษาไม่ให้ลงรหัส" ไม่อยู่ในเกณฑ์ WHO**

---

## ข้อ 5: Cancer Coding (8 กฎ)

1. รับไว้รักษา primary → primary = PDx, secondary = SDx
2. รับไว้รักษา secondary (เช่น brain met) → secondary = PDx, primary = SDx
3. หลาย primary → แพทย์ตัดสินว่าตัวไหนเป็น PDx
4. Primary ผ่าตัดแล้ว ยังรักษาอยู่ (chemo/RT) → ยังใช้ primary code ต่อไป
5. Primary + secondary ตั้งแต่แรก → primary = PDx, secondary = SDx
6. Secondary ตัดออกหมด ไม่กลับเป็น → **ไม่ต้อง code secondary อีก**
7. เคยเป็นมะเร็ง หายแล้ว มา f/u ไม่พบ recurrent → Z08 + Z85.x
8. Primary หายแล้ว มาด้วย new secondary → secondary = PDx, Z85.x = SDx

---

## ข้อ 6-7: Hepatoma / Cholangiocarcinoma

| สถานการณ์ | รหัส |
|-----------|------|
| CT/MRI: arterial enhancement + rapid washout + cirrhosis | C22.0 Hepatocellular carcinoma |
| ก้อนตับ ไม่มีลักษณะเฉพาะ + มี metastasis | C22.9 Malignant neoplasm of liver, unspecified |
| แพทย์แน่ใจว่าเป็นเนื้องอก แต่ไม่มีหลักฐานมะเร็ง | D37.6 Neoplasm of uncertain behavior |
| ยังไม่แน่ใจ (อาจเป็น granuloma/infection) | R93.2 Abnormal finding on diagnostic imaging |
| Cholangiocarcinoma | **ต้องมีผลพยาธิวิทยายืนยัน** → C22.1 |

---

## ข้อ 8-12: Anemia

### Hb Cutoffs (ข้อ 8)
| กลุ่ม | Hb (g/dl) |
|-------|-----------|
| เด็ก 6-23 เดือน | <10.5 |
| เด็ก 24-59 เดือน | <11.0 |
| ผู้ใหญ่ชาย | <13.0 |
| ผู้ใหญ่หญิง (ไม่ตั้งครรภ์) | <12.0 |
| ตั้งครรภ์ trimester 1,3 | <11.0 |
| ตั้งครรภ์ trimester 2 | <10.5 |

### Iron Deficiency Anemia (ข้อ 9)
- Blood smear: hypochromic microcytic, MCV <80 fl
- Serum ferritin <15 ng/ml, Serum iron <30 µg/dl, TIBC >360 µg/dl
- Transferrin saturation <10%

### เกณฑ์เป็นโรคร่วม (ข้อ 11-12)
- วินิจฉัย anemia in chronic disease/malignancy/CKD **เมื่อ severe จนต้องให้เลือด** หรือต้องตรวจเพิ่มเพื่อ DDx เท่านั้น
- Anemia in CKD: ต้องเป็น CKD stage 3 ขึ้นไป

---

## ข้อ 13: Pancytopenia

ให้ 3 รหัส:
- D64.9 Anemia (Hb <12 หญิง, <13 ชาย)
- D70 Agranulocytosis (ANC <1000)
- D69.6 Thrombocytopenia (PLT <100,000)

**ถึงไม่ได้ให้ platelet ก็ลงรหัสได้** เพราะเพิ่มความเสี่ยงติดเชื้อ/เลือดออก = WHO comorbidity

---

## ข้อ 14: DIC

**ISTH Score ≥5 = Overt DIC**

| ตัวชี้วัด | คะแนน |
|-----------|-------|
| PLT >100K / 50-100K / <50K | 0 / 1 / 2 |
| PT <3s / 3-6s / >6s prolonged | 0 / 1 / 2 |
| D-dimer ปกติ / สูงปานกลาง / สูงมาก | 0 / 2 / 3 |
| Fibrinogen >1 g/L / <1 g/L | 0 / 1 |

ถ้าไม่เข้าเกณฑ์ (ISTH <5, ไม่ได้ตรวจ D-dimer/fibrinogen):
→ D69.5 Secondary thrombocytopenia + D68.4 Acquired coagulation factor deficiency

---

## ข้อ 15: DM Complications (เท้า)

| สาเหตุ | PDx | SDx |
|--------|-----|-----|
| Diabetic neuropathy | E11.4† DM with neurologic comp. | G63.2* Diabetic polyneuropathy |
| Peripheral vascular disease | E11.5† DM with peripheral circ. | I79.2* Peripheral angiopathy |
| ทั้ง neuropathy + PVD | E11.7† DM with multiple comp. | G63.2* + I79.2* |
| Charcot's joint | E11.6† DM other specified comp. | M14.6 Neuropathic arthropathy |
| มาด้วยติดเชื้อ (cellulitis, abscess, osteo) | **ติดเชื้อ = PDx** | DM complication = SDx |

### Acute + Chronic DM complication
- Acute (เช่น hyperglycemia coma E11.0) = **PDx**
- Chronic (เช่น nephropathy E11.2†) = SDx

---

## ข้อ 16: Malnutrition

### BMI Criteria
- BMI 17-18.49 → Mild (ระดับ 1)
- BMI 16-16.99 → Moderate (ระดับ 2)
- BMI <16 → Severe (ระดับ 3)

### Marasmus (severe energy malnutrition)
ตรวจพบ ≥2 ข้อ: BMI <16, Albumin ต่ำ (≥2.8), Triceps skin fold <3mm, Mid arm <15cm

### Kwashiorkor (severe protein malnutrition)
Albumin <2.8 g/dL + ผมร่วง, ท้องป่อง, บวม, สีผิวเปลี่ยน

### เกณฑ์เป็นโรคร่วมใน IP
- ≥ Moderate malnutrition + มีการรักษา (high protein diet, enteral/parenteral nutrition)

---

## ข้อ 19: Obesity (Asian BMI)

| เกณฑ์ | WHO | คนเอเชีย |
|-------|-----|----------|
| Underweight | <18.5 | <18.5 |
| Normal | 18.5-24.9 | 18.5-22.9 |
| Overweight | 25-29.9 | **23-24.9** |
| Class I | 30-34.9 | **25-29.9** |
| Class II | 35-39.9 | **30-34.9** |
| Class III | ≥40 | **≥35** |

IP: วินิจฉัย **Class II ที่มี comorbidity** (DM, sleep apnea, HT, fatty liver) หรือ **Class III** เท่านั้น

---

## ข้อ 20: Electrolyte Imbalance

### ไม่ต้องลงรหัส (เป็นอาการของโรค)
- Acute diarrhea + electrolyte imbalance ปกติ
- CKD 4-5 / AKI + hyperkalemia ปกติ
- CKD 5 + volume overload ปกติ

### ต้องลงรหัส (severe)
- Na <120 mEq/L (severe hyponatremia)
- K <2.5 mEq/L (severe hypokalemia)
- Mg <0.5 mmol/L (hypomagnesemia)
- Hyperkalemia + ECG change + ต้อง urgent treatment
- Volume overload ต้อง emergency dialysis / IV diuretics

---

## ข้อ 21: TIA

| แพทย์วินิจฉัย | รหัส |
|---------------|------|
| Vertebro-basilar / posterior circulation | G45.0 |
| Carotid / anterior circulation | G45.1 |
| Multiple/bilateral precerebral | G45.2 |
| Amaurosis fugax | G45.3 |
| Transient global amnesia | G45.4 |
| TIA unspecified | G45.9 |
| Rexpressive stroke (เดิมเป็น stroke, มาใหม่ชั่วคราว, CT ไม่เปลี่ยน) | G45.9 |

---

## ข้อ 22: Vascular Syndromes (G46.*)

| Territory | รหัส | อาการ |
|-----------|------|-------|
| Middle cerebral artery | G46.0 | hemiparesis, ชาครึ่งซีก, aphasia (ซ้าย), แขนอ่อนแรง > ขา |
| Anterior cerebral artery | G46.1 | ขาอ่อนแรง > แขน, cognition change, incontinence |
| Posterior cerebral artery | G46.2 | homonymous hemianopia, ความจำเสีย, เวียนศีรษะ |
| Brain stem | G46.3 | cranial nerve deficit, locked-in, alternating hemiplegia |
| Cerebellar | G46.4 | vertigo, ataxia, คลื่นไส้, nystagmus |
| Pure motor lacunar | G46.5 | motor weakness hemiparesis เท่านั้น |
| Pure sensory lacunar | G46.6 | สูญเสียความรู้สึกข้างเดียว |
| Ataxic hemiparesis / dysarthria-clumsy hand | G46.7 | อ่อนแรง + ataxia หรือ พูดไม่ชัด + clumsy hand |

---

## ข้อ 24: Hypertensive Heart/Renal Disease

| แพทย์วินิจฉัย | รหัส |
|---------------|------|
| Hypertensive heart disease WITH heart failure | I11.0 |
| Hypertensive heart disease WITHOUT heart failure | I11.9 |
| Hypertensive renal disease WITH renal failure | I12.0 |
| Hypertensive renal disease WITHOUT renal failure | I12.9 |

**ต้องแพทย์วินิจฉัยว่าเป็น hypertensive heart/renal disease เท่านั้น** — ห้าม coder สรุปเอง

---

## ข้อ 25: Acute Coronary Syndrome (สำคัญมากสำหรับ Cath Lab)

| Diagnosis | รหัส | เกณฑ์ |
|-----------|------|-------|
| Unstable angina | **I20.0** | Rest pain >20 min / severe / crescendo |
| Stable angina | I20.8 | Exertional, relieved by rest/NTG |
| **STEMI** anterior/inferior/other/unspecified | **I21.0 - I21.3** | New ST elevation + Troponin >99th percentile |
| **NSTEMI** | **I21.4** | Troponin elevated + NO ST elevation |
| AMI unspecified | I21.9 | ไม่ระบุรายละเอียด |
| **Subsequent MI** (ภายใน 28 วัน) | **I22.-** | MI ใหม่หลัง MI เดิม ภายใน 4 สัปดาห์ |
| Coronary thrombosis NOT resulting in MI | I24.0 | พบ thrombus แต่ไม่อุดตัน |
| Acute ischemic heart disease unspecified | I24.9 | — |

### ST Elevation Criteria
- ชาย >40 ปี: >0.2 mV ที่ J point
- ชาย <40 ปี: >0.25 mV
- หญิง: >0.15 mV

### AMI = Troponin rise/fall >99th percentile + ≥1 ข้อ:
1. อาการ myocardial ischemia
2. New ST-T change / new LBBB
3. New pathologic Q wave
4. Loss of viable myocardium / new wall motion abnormality
5. Intracoronary thrombus จาก angiography

---

## ข้อ 26: Atherosclerotic Heart Disease

| Diagnosis | รหัส | เกณฑ์ |
|-----------|------|-------|
| Atherosclerotic HD | I25.1 | Stenosis >70% (LM >50%) จาก CAG/CTA/MRI |
| Old MI | I25.2 | ประวัติ MI + ปัจจุบันไม่มีอาการ |
| Ischemic cardiomyopathy | **I25.5** | LVEF <40% + (Hx MI หรือ LM/LAD >75% หรือ ≥2 vessels >75%) |

---

## ข้อ 27-28: PE / Pulmonary Hypertension

- Acute PE: I26.0 (CT angiogram พบ emboli)
- Chronic PE: I26.9 (≥3 เดือน, mPAP ≥25)
- Primary PAH: I27.0
- PH due to left heart: I27.2
- Cor pulmonale: I27.9

---

## ข้อ 30: Cardiac Arrest

- **ให้รหัสสาเหตุเป็น PDx** (เช่น VF I49.0, Complete AVB I44.2, MI I21.-)
- I46.0 Cardiac arrest with successful resuscitation = **SDx**
- ไม่ทราบสาเหตุ + admit ดูหลัง arrest → I46.0 = PDx
- Sudden cardiac death → I46.1
- Resuscitation ไม่สำเร็จ → **ไม่ต้องลงรหัส**

---

## ข้อ 31: Atrial Fibrillation

| ชนิด | รหัส | เกณฑ์ |
|------|------|-------|
| Paroxysmal | I48.0 | กลับเป็นซ้ำ ≥2 ครั้ง หยุดเอง ≤7 วัน |
| Persistent | I48.1 | >7 วัน หรือต้อง cardioversion |
| Permanent | I48.2 | Persistent >1 ปี ไม่ทำ rhythm control อีก |
| Typical flutter | I48.3 | Sawtooth pattern, 250-350 bpm |
| Atypical flutter | I48.4 | หลังผ่าตัด/ablation |

---

## ข้อ 32: Heart Failure

| ชนิด | รหัส | เกณฑ์ |
|------|------|-------|
| CHF / RV failure / Biventricular | I50.0 | — |
| LV failure unspecified | I50.1 | — |
| HF unspecified | I50.9 | — |

### EF Classification (ต้องระบุ)
- **HFpEF**: LVEF >50%
- **HFmrEF**: LVEF 41-49.9%
- **HFrEF**: LVEF <40%

### กฎสำคัญ
- De novo HF → **สาเหตุ = PDx**, HF = SDx
- Known HF + CHF exacerbation → **HF = PDx**, underlying heart disease = SDx
- EF <50% อย่างเดียว **ไม่ = HF** ต้องมีอาการ+อาการแสดง

---

## ข้อ 33: CVA/Stroke

### ห้ามใช้ I64 (unspecified) ถ้าเลี่ยงได้ → ต้องระบุ:
- I60 Subarachnoid haemorrhage
- I61 Intracerebral haemorrhage
- I62 Other nontraumatic intracranial haemorrhage
- **I63 Cerebral infarction** (ต้องระบุ embolism/thrombosis + cerebral/precerebral)

### Embolism vs Thrombosis
| ลักษณะ | Embolism | Thrombosis |
|--------|----------|------------|
| สาเหตุ | AF, valvular, cardiomyopathy | Atherosclerosis, HT, DM, DLP |
| อาการ | เกิดทันทีขณะทำกิจกรรม | ค่อยเป็น, อาจเกิดขณะหลับ |
| ประวัติ | โรคหัวใจ | ปัจจัยเสี่ยง atherosclerosis |

### Territory (ใช้อาการ + CT)
- ควรให้ G46.-* เป็น SDx เพื่อระบุ territory

### ระยะเวลา
- I63 ครอบคลุม ~10 วัน (acute phase)
- 10 วัน - 1 เดือน: ยังใช้ cerebral infarction ได้ถ้ายังมี neurodeficit
- >1 เดือน: I69 Sequelae

---

## ข้อ 34: Sequelae of CVA

- หลัง ≥1 เดือน + ยังมี neurodeficit → neurodeficit = PDx, I69.- = SDx
- หลังหาย complete recovery → Z86.7 Personal history

---

## ข้อ 37: Pneumonia

### Organism-specific codes
| เชื้อ | รหัส |
|-------|------|
| Streptococcus pneumoniae | J13 |
| H. influenzae | J14 |
| Klebsiella | J15.0 |
| Pseudomonas | J15.1 |
| Staphylococcus | J15.2 |
| Beta-hemolytic strep | J15.4 |
| Mycoplasma | J15.7 |
| Chlamydophila | J16.0 |
| Bacterial unspecified | J15.9 |
| Aspiration pneumonia | J69.- |
| Lobar pneumonia (organism unknown) | J18.1 |
| Bronchopneumonia (organism unknown) | J18.0 |

- HAP/VAP → เพิ่ม Y95 nosocomial condition

---

## ข้อ 38: COPD

| สถานการณ์ | รหัส |
|-----------|------|
| COPD + acute exacerbation | **J44.1** (= MCC ใน DRG!) |
| COPD + acute lower tract infection | J44.0 + pneumonia code |
| COPD เฉยๆ | J44.9 |

ต้องมี spirometry ยืนยัน: FEV1/FVC <70%

---

## ข้อ 42: Respiratory Failure

| ชนิด | รหัส ICD-10 | สาเหตุ |
|------|-------------|--------|
| Acute Type I (hypoxemic) | J96.00 | PE, pneumonia, ARDS |
| Acute Type II (hypercapnic) | J96.01 | COPD, neuromuscular, drug |
| Acute Type III/IV/unspecified | J96.09 | Atelectasis, shock |
| Chronic Type I | J96.10 | — |
| Chronic Type II | J96.11 | — |
| Chronic unspecified | J96.19 | — |

**สามารถวินิจฉัย respiratory failure ได้แม้ O2 sat ยังปกติ** — ถ้าแพทย์ตัดสินใจ intubate ตามอาการ

---

## ข้อ 43: Gastritis

- ต้อง endoscopy ยืนยัน → ถ้าไม่ได้ scope → วินิจฉัย **dyspepsia** (ไม่ใช่ gastritis)
- เลือดออก + ไม่ได้ scope → วินิจฉัย **haematemesis / melaena** (ไม่ใช่ hemorrhagic gastritis)
- Acute vs Chronic: ดูระยะเวลา (<1 เดือน = acute) หรือผลพยาธิวิทยา

---

## ข้อ 45: Appendicitis

| แพทย์วินิจฉัย | รหัส |
|---------------|------|
| Acute appendicitis + generalized peritonitis | K35.2 |
| Acute appendicitis + localized peritonitis/abscess | K35.3 |
| Acute appendicitis without peritonitis | K35.8 |
| Chronic appendicitis | K36 |

---

## ข้อ 48: GI Bleeding

| แพทย์วินิจฉัย | รหัส |
|---------------|------|
| Haematemesis (อาเจียนเป็นเลือด) | K92.0 |
| Melaena (ถ่ายดำ) | K92.1 |
| GI bleeding unspecified | K92.2 |
| Lower GI bleeding | K92.3 |
| ทั้ง haematemesis + melaena → ใช้ | K92.0 (รุนแรงกว่า) |

- ถ้าส่องกล้อง → ลงรหัสตามผลส่องกล้อง (เช่น K29.0 Acute hemorrhagic gastritis)

---

## ข้อ 51: AKI (Acute Kidney Injury)

### KDIGO Criteria
- Cr เพิ่ม >0.3 mg/dL ภายใน 48 ชม.
- หรือ Cr เพิ่ม ≥50% ของ baseline ภายใน 7 วัน
- หรือ UO <0.5 mL/kg/hr นาน >6 ชม.

| สาเหตุ | รหัส |
|--------|------|
| Prerenal (shock, hypovolemia) | **R39.2** Extrarenal uraemia (ไม่ใช่ N17!) |
| Renal (ATN, cortical/medullary necrosis) | N17.- |
| Postrenal (obstruction) | N17.8 + N13.- |

**ข้อควรจำ:** Prerenal failure ที่ดีขึ้นใน 1-3 วันหลังให้น้ำ → R39.2 ไม่ใช่ N17

---

## ข้อ 52: CKD

| Stage | GFR (mL/min/1.73m²) | การลงรหัส |
|-------|---------------------|----------|
| 1 | >90 | ลงเฉพาะชื่อโรคไต ไม่ต้องระบุ stage |
| 2 | 60-89 | เช่นเดียวกัน |
| 3a | 45-59 | เช่นเดียวกัน |
| 3b | 30-44 | เช่นเดียวกัน |
| 4 | 15-29 | **บังคับลงรหัส N18.4 ทุกกรณี IP** (= MCC!) |
| 5 | <15 | **บังคับลงรหัส N18.5 ทุกกรณี IP** |

---

## ข้อ 53: Unspecified Kidney Failure

**ไม่ควรใช้รหัสนี้** — ปัจจุบันแยก acute/chronic ได้จาก: urine flow, anemia, BUN/Cr ratio, kidney size
