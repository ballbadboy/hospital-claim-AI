import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from core.models import (
    ClaimInput, ClaimCheckResponse, CheckResult, Severity,
    Department, Fund, FDHStatus, AppealStatus
)
from core.repositories import ClaimRepository, AuditRepository


def make_test_claim():
    return ClaimInput(
        hn="TEST001", an="AN001", principal_dx="I21.1",
        procedures=["37.22"], fund=Fund.UC,
    )


def make_test_response():
    return ClaimCheckResponse(
        hn="TEST001", an="AN001", department=Department.CATH_LAB,
        fund=Fund.UC, principal_dx="I21.1", procedures=["37.22"],
        results=[], score=85, ready_to_submit=True,
        critical_count=0, warning_count=0, passed_count=3, optimization_count=1,
    )


class TestClaimRepository:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.execute = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, mock_session):
        return ClaimRepository(mock_session)

    @pytest.mark.asyncio
    async def test_save_check_result_creates_record(self, repo, mock_session):
        claim = make_test_claim()
        response = make_test_response()
        record = await repo.save_check_result(claim, response)
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_check_result_sets_fdh_status_checked(self, repo, mock_session):
        claim = make_test_claim()
        response = make_test_response()
        record = await repo.save_check_result(claim, response)
        assert record.fdh_status == FDHStatus.CHECKED


class TestAuditRepository:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, mock_session):
        return AuditRepository(mock_session)

    @pytest.mark.asyncio
    async def test_log_action_creates_entry(self, repo, mock_session):
        await repo.log_action(an="AN001", action="check", details={"score": 85})
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
