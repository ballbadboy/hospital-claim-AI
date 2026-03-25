import pytest
from datetime import datetime
from core.models import ClaimInput, CheckResult, Department, Fund, Severity
from core.rule_engine import run_rule_engine, detect_department, calculate_score


def make_claim(**kwargs):
    defaults = {
        "hn": "TEST001",
        "principal_dx": "I21.1",
        "procedures": ["37.22", "88.56", "36.07"],
        "fund": Fund.UC,
    }
    defaults.update(kwargs)
    return ClaimInput(**defaults)


class TestDetectDepartment:
    def test_cath_lab(self):
        claim = make_claim(principal_dx="I21.1", procedures=["37.22", "88.56", "36.07"])
        assert detect_department(claim) == Department.CATH_LAB

    def test_dialysis(self):
        claim = make_claim(principal_dx="N18.5", procedures=["39.95"])
        assert detect_department(claim) == Department.DIALYSIS

    def test_icu(self):
        claim = make_claim(principal_dx="J96.00", procedures=["96.72"], ward="ICU")
        assert detect_department(claim) == Department.ICU_NICU

    def test_chemo(self):
        claim = make_claim(principal_dx="C50.9", procedures=[])
        assert detect_department(claim) == Department.CHEMO


class TestRuleEngine:
    def test_no_authen_flagged(self):
        claim = make_claim(authen_code=None, fund=Fund.UC)
        results = run_rule_engine(claim)
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("Authen Code" in r.message for r in critical)

    def test_stent_without_device_data(self):
        claim = make_claim(procedures=["36.07"], devices=[])
        results = run_rule_engine(claim)
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert len(critical) > 0

    def test_mcc_detected(self):
        claim = make_claim(secondary_dx=["A41.9", "N17.0"])
        results = run_rule_engine(claim)
        passed = [r for r in results if r.severity == Severity.PASSED]
        assert any("MCC" in r.message for r in passed)

    def test_no_cc_triggers_optimization(self):
        claim = make_claim(an="AN001", secondary_dx=["I10", "E78.5"])
        results = run_rule_engine(claim)
        opt = [r for r in results if r.severity == Severity.OPTIMIZATION]
        assert any("CC/MCC" in r.message for r in opt)

    def test_fast_track_timing(self):
        claim = make_claim(
            discharge_date=datetime(2026, 2, 14, 10, 0),
            submit_date=datetime(2026, 2, 14, 18, 0)
        )
        results = run_rule_engine(claim)
        passed = [r for r in results if r.severity == Severity.PASSED]
        assert any("Fast Track" in r.message for r in passed)

    def test_late_submission_flagged(self):
        claim = make_claim(
            discharge_date=datetime(2026, 1, 1),
            submit_date=datetime(2026, 3, 1)
        )
        results = run_rule_engine(claim)
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("30" in r.message for r in critical)

    def test_discharge_before_admit(self):
        claim = make_claim(
            admit_date=datetime(2026, 2, 14),
            discharge_date=datetime(2026, 2, 10)
        )
        results = run_rule_engine(claim)
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("discharge" in r.message.lower() and "admit" in r.message.lower()
                    for r in critical)


class TestScoreCalculation:
    def test_all_passed(self):
        results = [
            CheckResult(severity=Severity.PASSED, checkpoint="test", message="ok")
            for _ in range(5)
        ]
        score, ready = calculate_score(results)
        assert score == 100
        assert ready is True

    def test_has_critical(self):
        results = [
            CheckResult(severity=Severity.PASSED, checkpoint="a", message="ok"),
            CheckResult(severity=Severity.CRITICAL, checkpoint="b", message="fail"),
        ]
        score, ready = calculate_score(results)
        assert score == 50
        assert ready is False
