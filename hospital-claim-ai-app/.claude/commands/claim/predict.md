ทำนายว่า claim จะถูก deny หรือไม่ ก่อนส่งเบิก

Input: $ARGUMENTS (ข้อมูลเคส: AN, PDx, Procedures, stent, drugs, วันที่, สิทธิ)

ใช้ skill deny-predictor วิเคราะห์ 10 Risk Factors:
- RF1: CID Checksum (5%)
- RF2: PDx Valid (15%)
- RF3: Dx-Proc Match (20%)
- RF4: Device Docs (15%)
- RF5: Drug Catalog (10%)
- RF6: Timing (10%)
- RF7: Authen Code (10%)
- RF8: CC/MCC Coding (5%)
- RF9: DRG Groupable (5%)
- RF10: Charge Reasonable (5%)

Output: Deny Probability (0-100%), Verdict (SAFE/CAUTION/HIGH_RISK/ALMOST_CERTAIN)
Top risks + Estimated loss if denied + Recommendation (ส่งได้เลย/แก้ก่อนส่ง/ห้ามส่ง)
