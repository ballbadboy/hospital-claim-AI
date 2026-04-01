import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from core.report_engine import ReportEngine


class TestReportEngine:
    def test_generate_monthly_summary_excel(self):
        """Test that monthly summary generates valid Excel bytes."""
        stats = {
            "total_claims": 150,
            "denied_claims": 12,
            "deny_rate": 8.0,
            "revenue_at_risk": 500000.0,
            "revenue_recovered": 350000.0,
            "avg_score": 82.5,
            "by_department": {
                "cath_lab": {"total": 50, "denied": 4, "deny_rate": 8.0},
                "or_surgery": {"total": 30, "denied": 2, "deny_rate": 6.7},
            },
            "by_deny_reason": {
                "C-438": 5,
                "Late submission": 3,
                "Data incomplete": 4,
            },
            "period": "2026-02",
        }
        result = ReportEngine.generate_monthly_summary(stats)
        assert isinstance(result, bytes)
        assert len(result) > 0
        # Verify it's a valid xlsx by checking magic bytes
        assert result[:2] == b'PK'  # xlsx is a zip file

    def test_generate_claim_audit_trail(self):
        """Test audit trail Excel generation."""
        trail = [
            {"an": "AN001", "action": "check", "details": {"score": 85}, "user": "admin", "at": "2026-02-14T10:00:00"},
            {"an": "AN001", "action": "submit", "details": {}, "user": "admin", "at": "2026-02-14T11:00:00"},
        ]
        result = ReportEngine.generate_audit_trail(trail, an="AN001")
        assert isinstance(result, bytes)
        assert result[:2] == b'PK'

    def test_generate_department_detail(self):
        """Test department detail report."""
        dept_data = {
            "department": "cath_lab",
            "period": "2026-02",
            "total": 50,
            "denied": 4,
            "deny_rate": 8.0,
            "avg_score": 85.2,
            "top_deny_reasons": [("C-438", 3), ("Late submission", 1)],
        }
        result = ReportEngine.generate_department_detail(dept_data)
        assert isinstance(result, bytes)
        assert result[:2] == b'PK'
