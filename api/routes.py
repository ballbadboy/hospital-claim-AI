import logging

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import func, select

from core.models import (
    ClaimInput, ClaimCheckResponse, AppealRequest, AppealResponse,
    BatchCheckRequest, DashboardStats, AppealStatus
)
from core.claim_checker import check_claim, check_batch
from core.ai_engine import generate_appeal
from core.rule_engine import detect_department
from core.database import ClaimRecord
from core.repositories import ClaimRepository, AuditRepository
from api.auth.middleware import get_current_user, require_role
from api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["claims"])

MAX_CSV_SIZE = 5 * 1024 * 1024


@router.post("/check", response_model=ClaimCheckResponse)
async def check_single_claim(
    claim: ClaimInput,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """ตรวจสอบเคสเดี่ยว ก่อนส่งเบิก"""
    result = await check_claim(claim)
    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    await claim_repo.save_check_result(claim, result)
    await audit_repo.log_action(
        an=claim.an or "", action="check",
        details={"score": result.score, "critical": result.critical_count},
        user=user["sub"],
    )
    return result


@router.post("/check/batch", response_model=list[ClaimCheckResponse])
async def check_batch_claims(
    request: BatchCheckRequest,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """ตรวจสอบหลายเคสพร้อมกัน"""
    if len(request.claims) > 500:
        raise HTTPException(400, "Maximum 500 claims per batch")
    results = await check_batch(request.claims)
    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    for claim, result in zip(request.claims, results):
        await claim_repo.save_check_result(claim, result)
        await audit_repo.log_action(
            an=claim.an or "", action="check",
            details={"score": result.score, "critical": result.critical_count},
            user=user["sub"],
        )
    return results


@router.post("/check/csv")
async def check_csv_upload(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
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
    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    for claim, result in zip(claims, results):
        await claim_repo.save_check_result(claim, result)
        await audit_repo.log_action(
            an=claim.an or "", action="check_csv",
            details={"score": result.score, "critical": result.critical_count},
            user=user["sub"],
        )

    summary = {
        "total": len(results),
        "ready": sum(1 for r in results if r.ready_to_submit),
        "issues": sum(1 for r in results if not r.ready_to_submit),
        "critical_total": sum(r.critical_count for r in results),
        "results": results,
    }
    return summary


@router.post("/appeal", response_model=AppealResponse)
async def generate_appeal_letter(
    request: AppealRequest,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
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

    claim_repo = ClaimRepository(session)
    audit_repo = AuditRepository(session)
    record = await claim_repo.get_by_an(request.an)
    if record and record.appeal_status in (AppealStatus.NONE, AppealStatus.NONE.value, None):
        await claim_repo.update_appeal_status(request.an, AppealStatus.DRAFTED)
        record.appeal_text = letter

    await audit_repo.log_action(
        an=request.an, action="appeal_draft",
        details={"deny_reason": request.deny_reason},
        user=user["sub"],
    )

    return AppealResponse(
        letter_text=letter,
        supporting_docs=["สำเนาเวชระเบียน", "รายงานผลหัตถการ", "ผล Lab ที่เกี่ยวข้อง"],
    )


@router.get("/status/{an}")
async def get_claim_status(
    an: str,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """ดูสถานะเคสตาม AN"""
    claim_repo = ClaimRepository(session)
    record = await claim_repo.get_by_an(an)
    if record is None:
        raise HTTPException(404, f"Claim {an} not found")
    audit_repo = AuditRepository(session)
    trail = await audit_repo.get_audit_trail(an)
    return {
        "an": record.an, "hn": record.hn, "department": record.department,
        "fdh_status": record.fdh_status, "appeal_status": record.appeal_status,
        "score": record.check_score, "ready_to_submit": record.ready_to_submit,
        "created_at": record.created_at, "updated_at": record.updated_at,
        "audit_trail": [
            {"action": a.action, "details": a.details, "user": a.user, "at": a.created_at}
            for a in trail
        ],
    }


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """KPI Dashboard data — queries actual DB"""
    total = (await session.execute(select(func.count(ClaimRecord.id)))).scalar() or 0
    denied = (await session.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.fdh_status == "denied")
    )).scalar() or 0
    deny_rate = (denied / total * 100) if total > 0 else 0.0
    avg_score = (await session.execute(
        select(func.avg(ClaimRecord.check_score))
    )).scalar() or 0.0
    revenue_at_risk = (await session.execute(
        select(func.coalesce(func.sum(ClaimRecord.claim_amount), 0.0))
        .where(ClaimRecord.fdh_status == "denied")
    )).scalar() or 0.0
    revenue_recovered = (await session.execute(
        select(func.coalesce(func.sum(ClaimRecord.revenue_recovered), 0.0))
    )).scalar() or 0.0

    return DashboardStats(
        total_claims=total, denied_claims=denied, deny_rate=round(deny_rate, 2),
        revenue_at_risk=revenue_at_risk, revenue_recovered=revenue_recovered,
        avg_score=round(float(avg_score), 1),
    )


@router.get("/health")
async def health_check():
    from core.config import get_settings
    settings = get_settings()
    return {
        "status": "ok", "version": settings.app_version,
        "services": {
            "database": "configured" if settings.database_url else "not_configured",
            "ai_engine": "configured" if settings.anthropic_api_key else "not_configured",
            "line": "configured" if settings.line_channel_token else "not_configured",
            "fdh": "configured" if settings.fdh_api_key else "not_configured",
            "his_connectors": settings.his_connectors,
        },
    }
