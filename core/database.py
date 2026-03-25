from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Enum as SAEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone

from core.config import get_settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ClaimRecord(Base):
    __tablename__ = "claim_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hn = Column(String, index=True)
    an = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    fund = Column(String, index=True)

    principal_dx = Column(String)
    secondary_dx = Column(JSON, default=list)
    procedures = Column(JSON, default=list)

    admit_date = Column(DateTime(timezone=True))
    discharge_date = Column(DateTime(timezone=True))
    submit_date = Column(DateTime(timezone=True))
    los_days = Column(Integer)

    expected_drg = Column(String)
    actual_drg = Column(String)
    estimated_rw = Column(Float)
    claim_amount = Column(Float)

    check_score = Column(Integer, default=0)
    check_results = Column(JSON, default=list)
    ready_to_submit = Column(Boolean, default=False)
    ai_analysis = Column(String)

    fdh_status = Column(String, default="pending")  # pending, submitted, approved, denied
    deny_reason = Column(String)
    appeal_status = Column(String)  # none, drafted, submitted, approved, rejected
    appeal_text = Column(String)

    revenue_recovered = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    an = Column(String, index=True)
    action = Column(String)  # check, submit, appeal, status_update
    details = Column(JSON)
    user = Column(String, default="system")
    created_at = Column(DateTime(timezone=True), default=_utcnow)


def get_engine():
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=settings.app_env == "development")


def get_session_factory():
    engine = get_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
