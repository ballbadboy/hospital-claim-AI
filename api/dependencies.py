"""FastAPI dependencies for DB sessions and auth."""

import logging
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session_factory
from core.repositories import ClaimRepository, AuditRepository, UserRepository

logger = logging.getLogger(__name__)

_session_factory = None


def _get_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = get_session_factory()
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = _get_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_claim_repo(
    session: AsyncSession = Depends(get_db_session),
) -> ClaimRepository:
    return ClaimRepository(session)


async def get_audit_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AuditRepository:
    return AuditRepository(session)
