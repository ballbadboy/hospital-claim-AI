"""Repository pattern — separates DB operations from route logic."""

import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import ClaimRecord, AuditLog, User
from core.models import (
    ClaimInput, ClaimCheckResponse, FDHStatus, AppealStatus
)
from core.state_machine import validate_fdh_transition, validate_appeal_transition

logger = logging.getLogger(__name__)


class ClaimRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_check_result(
        self, claim: ClaimInput, result: ClaimCheckResponse
    ) -> ClaimRecord:
        record = ClaimRecord(
            hn=claim.hn, an=claim.an,
            department=result.department.value,
            fund=claim.fund.value,
            principal_dx=claim.principal_dx,
            secondary_dx=claim.secondary_dx,
            procedures=claim.procedures,
            admit_date=claim.admit_date,
            discharge_date=claim.discharge_date,
            submit_date=claim.submit_date,
            check_score=result.score,
            check_results=[r.model_dump() for r in result.results],
            ready_to_submit=result.ready_to_submit,
            expected_drg=result.expected_drg,
            estimated_rw=result.estimated_rw,
            claim_amount=result.estimated_claim,
            ai_analysis=result.ai_analysis,
            fdh_status=FDHStatus.CHECKED,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_an(self, an: str) -> ClaimRecord | None:
        result = await self.session.execute(
            select(ClaimRecord).where(ClaimRecord.an == an)
        )
        return result.scalar_one_or_none()

    async def list_claims(self, page: int = 1, size: int = 50,
                          department: str | None = None,
                          fdh_status: str | None = None) -> list[ClaimRecord]:
        query = select(ClaimRecord).order_by(ClaimRecord.created_at.desc())
        if department:
            query = query.where(ClaimRecord.department == department)
        if fdh_status:
            query = query.where(ClaimRecord.fdh_status == fdh_status)
        query = query.offset((page - 1) * size).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_fdh_status(self, an: str, new_status: FDHStatus) -> ClaimRecord:
        record = await self.get_by_an(an)
        if record is None:
            raise ValueError(f"Claim {an} not found")
        validate_fdh_transition(FDHStatus(record.fdh_status), new_status)
        record.fdh_status = new_status.value
        record.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return record

    async def update_appeal_status(self, an: str, new_status: AppealStatus) -> ClaimRecord:
        record = await self.get_by_an(an)
        if record is None:
            raise ValueError(f"Claim {an} not found")
        current = AppealStatus(record.appeal_status or AppealStatus.NONE)
        validate_appeal_transition(current, new_status)
        record.appeal_status = new_status.value
        record.updated_at = datetime.now(timezone.utc)
        if new_status == AppealStatus.APPROVED:
            validate_fdh_transition(FDHStatus(record.fdh_status), FDHStatus.APPROVED)
            record.fdh_status = FDHStatus.APPROVED.value
        await self.session.flush()
        return record


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(self, an: str, action: str, details: dict,
                         user: str = "system") -> AuditLog:
        entry = AuditLog(an=an, action=action, details=details, user=user)
        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

    async def get_audit_trail(self, an: str) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog).where(AuditLog.an == an)
            .order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, username: str, hashed_password: str,
                          role: str = "readonly") -> User:
        user = User(username=username, hashed_password=hashed_password, role=role)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def increment_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 10:
            from datetime import timedelta
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        await self.session.flush()

    async def reset_failed_login(self, user: User) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.flush()
