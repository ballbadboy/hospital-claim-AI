"""Cath Lab API Routes — Pre-submission check + Post-denial analysis."""

import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from core.cathlab_models import CathLabClaim, CathLabCheckResult, DenyAnalysis, DRGInfo
from core.cathlab_validator import validate_cathlab_claim
from core.deny_analyzer import analyze_deny
from core.drg_calculator import lookup_drg
from core.eclaim_parser import parse_eclaim_csv
from api.auth.middleware import get_current_user

logger = logging.getLogger(__name__)

MAX_ECLAIM_CSV_SIZE = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/api/v1/cathlab", tags=["Cath Lab"])


@router.post("/check", response_model=CathLabCheckResult)
async def check_claim(
    claim: CathLabClaim,
    user: dict = Depends(get_current_user),
):
    """Pre-submission validation: ตรวจ 8 checkpoints + CC/MCC optimization.

    ส่ง claim data มา → ได้ score + issues + optimization suggestions กลับ
    """
    result = validate_cathlab_claim(claim)
    return result


@router.post("/analyze-deny", response_model=DenyAnalysis)
async def analyze_deny_claim(
    claim: CathLabClaim,
    user: dict = Depends(get_current_user),
):
    """Post-denial analysis: วิเคราะห์สาเหตุ deny + แนะนำวิธีแก้ + draft appeal.

    ส่ง denied claim data มา (ต้องมี deny_codes) → ได้ root cause + fix steps + appeal draft
    """
    if not claim.deny_codes:
        raise HTTPException(status_code=400, detail="ต้องระบุ deny_codes อย่างน้อย 1 รหัส")
    result = analyze_deny(claim)
    return result


@router.post("/parse-eclaim")
async def parse_eclaim_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Parse e-Claim CSV export → structured CathLabClaim objects.

    Upload ไฟล์ CSV จาก e-Claim export → ได้ list ของ claims พร้อม validate
    """
    if not file.filename.endswith((".csv", ".CSV")):
        raise HTTPException(status_code=400, detail="รองรับเฉพาะไฟล์ .csv")

    content = await file.read()
    if len(content) > MAX_ECLAIM_CSV_SIZE:
        raise HTTPException(status_code=413, detail=f"ไฟล์ใหญ่เกินไป (สูงสุด {MAX_ECLAIM_CSV_SIZE // 1024 // 1024} MB)")

    text = content.decode("utf-8-sig")

    claims, skipped = parse_eclaim_csv(text)

    if not claims:
        raise HTTPException(status_code=400, detail="ไม่พบข้อมูล claim ในไฟล์")

    logger.info("eclaim_parse", extra={"user": user.get("sub"), "total_parsed": len(claims), "skipped": len(skipped)})

    # Validate each claim
    results = []
    for claim in claims:
        check = validate_cathlab_claim(claim)
        results.append({
            "claim": claim.model_dump(),
            "validation": check.model_dump(),
        })

    return {
        "total_claims": len(claims),
        "skipped_rows": len(skipped),
        "skipped_details": skipped[:20],
        "results": results,
    }


@router.get("/drg-lookup/{drg_code}", response_model=DRGInfo)
async def drg_lookup(
    drg_code: str,
    user: dict = Depends(get_current_user),
):
    """Lookup DRG info: RW, WtLOS, OT, payment estimate.

    ใส่ DRG code เช่น 05290 → ได้ข้อมูล RW + ค่าจ่าย
    """
    info = lookup_drg(drg_code)
    if not info:
        raise HTTPException(status_code=404, detail=f"ไม่พบ DRG {drg_code} ใน cardiac RW table")
    return info
