"""Report generation and Excel download endpoints."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
import io

from core.config import get_settings
from core.database import ClaimRecord, AuditLog
from core.report_engine import ReportEngine
from core.repositories import ClaimRepository, AuditRepository
from api.auth.middleware import get_current_user, require_role
from api.dependencies import get_db_session

logger = logging.getLogger(__name__)

reports_router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@reports_router.get("/monthly")
async def monthly_summary_report(
    year: int = None,
    month: int = None,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """Generate and download monthly summary Excel report."""
    now = datetime.now(timezone.utc)
    year = year or now.year
    month = month or now.month

    # Query stats from DB
    from sqlalchemy import and_, extract
    date_filter = and_(
        extract("year", ClaimRecord.created_at) == year,
        extract("month", ClaimRecord.created_at) == month,
    )

    total = (await session.execute(
        select(func.count(ClaimRecord.id)).where(date_filter)
    )).scalar() or 0

    denied = (await session.execute(
        select(func.count(ClaimRecord.id)).where(
            and_(date_filter, ClaimRecord.fdh_status == "denied")
        )
    )).scalar() or 0

    deny_rate = (denied / total * 100) if total > 0 else 0.0
    avg_score = (await session.execute(
        select(func.avg(ClaimRecord.check_score)).where(date_filter)
    )).scalar() or 0.0

    revenue_at_risk = (await session.execute(
        select(func.coalesce(func.sum(ClaimRecord.claim_amount), 0.0)).where(
            and_(date_filter, ClaimRecord.fdh_status == "denied")
        )
    )).scalar() or 0.0

    revenue_recovered = (await session.execute(
        select(func.coalesce(func.sum(ClaimRecord.revenue_recovered), 0.0)).where(date_filter)
    )).scalar() or 0.0

    # Department breakdown
    dept_rows = (await session.execute(
        select(
            ClaimRecord.department,
            func.count(ClaimRecord.id).label("total"),
            func.count(ClaimRecord.id).filter(ClaimRecord.fdh_status == "denied").label("denied"),
        ).where(date_filter).group_by(ClaimRecord.department)
    )).all()

    by_department = {}
    for row in dept_rows:
        dept_total = row.total or 0
        dept_denied = row.denied or 0
        by_department[row.department] = {
            "total": dept_total,
            "denied": dept_denied,
            "deny_rate": round((dept_denied / dept_total * 100) if dept_total > 0 else 0, 1),
        }

    # Deny reasons
    deny_rows = (await session.execute(
        select(ClaimRecord.deny_reason, func.count(ClaimRecord.id))
        .where(and_(date_filter, ClaimRecord.fdh_status == "denied", ClaimRecord.deny_reason.isnot(None)))
        .group_by(ClaimRecord.deny_reason)
        .order_by(func.count(ClaimRecord.id).desc())
        .limit(10)
    )).all()

    by_deny_reason = {row[0]: row[1] for row in deny_rows}

    stats = {
        "total_claims": total,
        "denied_claims": denied,
        "deny_rate": round(deny_rate, 2),
        "revenue_at_risk": revenue_at_risk,
        "revenue_recovered": revenue_recovered,
        "avg_score": round(float(avg_score), 1),
        "by_department": by_department,
        "by_deny_reason": by_deny_reason,
        "period": f"{year}-{month:02d}",
    }

    excel_bytes = ReportEngine.generate_monthly_summary(stats)
    filename = f"monthly_summary_{year}_{month:02d}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@reports_router.get("/audit/{an}")
async def audit_trail_report(
    an: str,
    user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
):
    """Download audit trail Excel for a specific claim."""
    audit_repo = AuditRepository(session)
    trail = await audit_repo.get_audit_trail(an)
    if not trail:
        raise HTTPException(404, f"No audit trail found for {an}")

    trail_data = [
        {"action": a.action, "user": a.user, "details": a.details, "at": str(a.created_at)}
        for a in trail
    ]
    excel_bytes = ReportEngine.generate_audit_trail(trail_data, an=an)
    filename = f"audit_trail_{an}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
