import logging

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.models import (
    ClaimInput, ClaimCheckResponse, AppealRequest, AppealResponse,
    BatchCheckRequest, DashboardStats
)
from core.claim_checker import check_claim, check_batch
from core.ai_engine import generate_appeal
from core.rule_engine import detect_department

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["claims"])

MAX_CSV_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/check", response_model=ClaimCheckResponse)
async def check_single_claim(claim: ClaimInput):
    """ตรวจสอบเคสเดี่ยว ก่อนส่งเบิก"""
    return await check_claim(claim)


@router.post("/check/batch", response_model=list[ClaimCheckResponse])
async def check_batch_claims(request: BatchCheckRequest):
    """ตรวจสอบหลายเคสพร้อมกัน"""
    if len(request.claims) > 500:
        raise HTTPException(400, "Maximum 500 claims per batch")
    return await check_batch(request.claims)


@router.post("/check/csv")
async def check_csv_upload(file: UploadFile = File(...)):
    """Upload CSV จาก FDH Dashboard แล้วตรวจทุกเคส"""
    import io

    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "application/octet-stream"):
        raise HTTPException(400, "Only CSV files are accepted")

    content = await file.read()
    if len(content) > MAX_CSV_SIZE:
        raise HTTPException(413, f"File too large. Maximum {MAX_CSV_SIZE // 1024 // 1024} MB")

    df = pd.read_csv(io.BytesIO(content))

    if len(df) > 500:
        raise HTTPException(400, "Maximum 500 rows per CSV upload")

    claims = []
    for _, row in df.iterrows():
        sdx_raw = row.get("SDx")
        sdx = str(sdx_raw).split(",") if pd.notna(sdx_raw) and sdx_raw else []
        proc_raw = row.get("Procedures")
        procs = str(proc_raw).split(",") if pd.notna(proc_raw) and proc_raw else []

        claim = ClaimInput(
            hn=str(row.get("HN", "")),
            an=str(row.get("AN", "")),
            principal_dx=str(row.get("PDx", row.get("Primary Diagnosis", ""))),
            secondary_dx=sdx,
            procedures=procs,
        )
        claims.append(claim)

    results = await check_batch(claims)
    summary = {
        "total": len(results),
        "ready": sum(1 for r in results if r.ready_to_submit),
        "issues": sum(1 for r in results if not r.ready_to_submit),
        "critical_total": sum(r.critical_count for r in results),
        "results": results,
    }
    return summary


@router.post("/appeal", response_model=AppealResponse)
async def generate_appeal_letter(request: AppealRequest):
    """สร้างหนังสืออุทธรณ์สำหรับเคสที่ถูก deny"""
    claim_data = {
        "hn": request.hn,
        "an": request.an,
        "principal_dx": request.principal_dx or "",
        "procedures": request.procedures,
    }

    letter = await generate_appeal(
        claim_data, request.deny_reason, request.department
    )

    return AppealResponse(
        letter_text=letter,
        supporting_docs=[
            "สำเนาเวชระเบียน",
            "รายงานผลหัตถการ",
            "ผล Lab ที่เกี่ยวข้อง",
        ],
    )


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """KPI Dashboard data"""
    # TODO: Query from database
    return DashboardStats(
        total_claims=0,
        denied_claims=0,
        deny_rate=0.0,
        revenue_at_risk=0.0,
        revenue_recovered=0.0,
        avg_score=0.0,
    )


@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
