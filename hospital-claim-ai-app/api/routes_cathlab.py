"""Cath Lab API Routes — Pre-submission check + Post-denial analysis + Smart Coder."""

import logging

from fastapi import APIRouter, Body, UploadFile, File, HTTPException, Depends

from core.cathlab_models import CathLabClaim, CathLabCheckResult, DenyAnalysis, DRGInfo
from core.cathlab_validator import validate_cathlab_claim
from core.deny_analyzer import analyze_deny
from core.deny_predictor import DenyPrediction, predict_deny
from core.drg_calculator import lookup_drg
from core.eclaim_parser import parse_eclaim_csv
from core.batch_optimizer import optimize_batch, BatchResult
from core.smart_coder import auto_code, CodingResult
from api.auth.middleware import get_current_user

logger = logging.getLogger(__name__)

MAX_ECLAIM_CSV_SIZE = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/api/v1/cathlab", tags=["Cath Lab"])


@router.post("/check", response_model=CathLabCheckResult)
async def check_claim(
    claim: CathLabClaim,
    user: dict = Depends(get_current_user),
):
    """Pre-submission validation: ตรวจ 8 checkpoints + CC/MCC optimization."""
    result = validate_cathlab_claim(claim)
    return result


@router.post("/analyze-deny", response_model=DenyAnalysis)
async def analyze_deny_claim(
    claim: CathLabClaim,
    user: dict = Depends(get_current_user),
):
    """Post-denial analysis: วิเคราะห์สาเหตุ deny + แนะนำวิธีแก้ + draft appeal."""
    if not claim.deny_codes:
        raise HTTPException(status_code=400, detail="ต้องระบุ deny_codes อย่างน้อย 1 รหัส")
    result = analyze_deny(claim)
    return result


@router.post("/parse-eclaim")
async def parse_eclaim_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Parse e-Claim CSV export → structured CathLabClaim objects."""
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
    """Lookup DRG info: RW, WtLOS, OT, payment estimate."""
    info = lookup_drg(drg_code)
    if not info:
        raise HTTPException(status_code=404, detail=f"ไม่พบ DRG {drg_code} ใน cardiac RW table")
    return info


@router.post("/batch-optimize", response_model=BatchResult)
async def batch_optimize_endpoint(
    claims: list[CathLabClaim],
    user: dict = Depends(get_current_user),
):
    """Batch Claim Optimizer: ส่ง claims หลายเคส → วิเคราะห์ทั้งล็อต เรียงตาม priority."""
    if not claims:
        raise HTTPException(status_code=400, detail="ต้องส่ง claims อย่างน้อย 1 เคส")
    result = optimize_batch(claims)
    return result


@router.post("/predict-deny", response_model=DenyPrediction)
async def predict_deny_endpoint(
    claim: CathLabClaim,
    user: dict = Depends(get_current_user),
):
    """Deny Predictor: ทำนายว่า claim จะถูก deny หรือไม่ ก่อนส่งเบิก."""
    result = predict_deny(claim)
    return result


@router.post("/smart-code", response_model=CodingResult)
async def smart_code_endpoint(
    clinical_text: str = Body(..., embed=True),
    user: dict = Depends(get_current_user),
):
    """Smart Coder: แปลง clinical notes ภาษาไทย/อังกฤษ → ICD-10 + ICD-9-CM อัตโนมัติ."""
    if not clinical_text or not clinical_text.strip():
        raise HTTPException(status_code=400, detail="กรุณาใส่ clinical notes")
    result = auto_code(clinical_text.strip())
    return result
