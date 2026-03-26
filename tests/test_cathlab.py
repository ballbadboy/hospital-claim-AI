"""Tests for Cath Lab module — using real deny case AN 69-03556."""

from datetime import datetime

from core.cathlab_models import CathLabClaim
from core.cathlab_validator import validate_cathlab_claim
from core.deny_analyzer import analyze_deny
from core.drg_calculator import lookup_drg, calculate_payment


# ═══════════════════════════════════════════════
# Real test case from e-Claim export
# Hospital: 11855 รพ.พญาไทศรีราชา
# ═══════════════════════════════════════════════

REAL_DENY_CASE = CathLabClaim(
    rep_no="690300013",
    tran_id="761883134",
    hn="69-09349",
    an="69-03556",
    pid="2411300021503",
    patient_name="นาง ลังกา เทยณี",
    patient_type="IP",
    admit_date=datetime(2026, 2, 27, 11, 44),
    discharge_date=datetime(2026, 3, 1, 13, 0),
    principal_dx="I21.0",  # STEMI anterior wall
    secondary_dx=["I10", "E11.9"],
    procedures=["36.06", "37.22", "88.56"],  # PCI + cath + angio
    drg="05290",
    rw=8.6544,
    charge_amount=31517.00,
    expected_payment=71322.00,
    fund="UCS",
    deny_codes=["HC09", "IP01", "HC13"],
    denied_items=["CLOPIDOGREL_DRUG", "INST", "IPINRGR"],
    inst_amount=31490.00,
)


class TestDRGCalculator:

    def test_lookup_05290(self):
        info = lookup_drg("05290")
        assert info is not None
        assert info.drg == "05290"
        assert info.rw == 8.6544
        assert info.description == "Acute MI w single vessel PTCA wo sig CCC"
        assert info.payment_estimate_in_zone == round(8.6544 * 8350, 2)

    def test_lookup_05291_with_cc(self):
        info = lookup_drg("05291")
        assert info is not None
        assert info.rw == 11.4820
        assert info.rw > lookup_drg("05290").rw  # CC version has higher RW

    def test_lookup_nonexistent(self):
        assert lookup_drg("99999") is None

    def test_payment_calculation(self):
        result = calculate_payment(rw=8.6544, los=2, drg_code="05290", in_zone=True)
        assert result["payment"] == round(8.6544 * 8350, 2)
        assert result["base_rate"] == 8350

    def test_short_stay_uses_rw0d(self):
        result = calculate_payment(rw=8.6544, los=1, drg_code="05290", in_zone=True)
        assert result["adj_rw"] == 7.8755  # RW0d from table
        assert result["los_adjustment"] == "short_stay (RW0d)"


class TestCathLabValidator:

    def test_real_case_validation(self):
        result = validate_cathlab_claim(REAL_DENY_CASE)
        assert result.an == "69-03556"
        assert result.score > 0
        assert len(result.checkpoints) == 8

    def test_checkpoint_1_basic_data_passes(self):
        result = validate_cathlab_claim(REAL_DENY_CASE)
        cp1 = result.checkpoints[0]
        assert cp1.checkpoint == 1
        assert cp1.status == "pass"

    def test_checkpoint_2_dx_proc_match_passes(self):
        """STEMI (I21.0) + PCI (36.06) + Cath (37.22) should pass."""
        result = validate_cathlab_claim(REAL_DENY_CASE)
        cp2 = result.checkpoints[1]
        assert cp2.checkpoint == 2
        assert cp2.status == "pass"

    def test_checkpoint_3_device_flags_missing_info(self):
        """No device details provided but inst_amount > 0 → should flag."""
        result = validate_cathlab_claim(REAL_DENY_CASE)
        cp3 = result.checkpoints[2]
        assert cp3.checkpoint == 3
        assert cp3.status in ("warning", "critical")

    def test_checkpoint_6_ccmcc_suggests_dm_upgrade(self):
        """E11.9 (unspecified) should suggest upgrade to E11.65."""
        result = validate_cathlab_claim(REAL_DENY_CASE)
        assert len(result.optimizations) > 0
        dm_opt = [o for o in result.optimizations if o.current_code == "E11.9"]
        assert len(dm_opt) > 0
        assert dm_opt[0].suggested_code == "E11.65"

    def test_checkpoint_7_drg_verified(self):
        result = validate_cathlab_claim(REAL_DENY_CASE)
        cp7 = result.checkpoints[6]
        assert cp7.checkpoint == 7
        assert "05290" in cp7.message

    def test_checkpoint_8_flags_clopidogrel(self):
        """Clopidogrel in denied_items should be flagged."""
        result = validate_cathlab_claim(REAL_DENY_CASE)
        cp8 = result.checkpoints[7]
        assert cp8.checkpoint == 8
        assert "Clopidogrel" in cp8.message

    def test_stemi_without_pci_flags_critical(self):
        """STEMI PDx without PCI procedure should flag critical."""
        claim = REAL_DENY_CASE.model_copy(update={"procedures": []})
        result = validate_cathlab_claim(claim)
        cp2 = result.checkpoints[1]
        assert cp2.status == "critical"
        assert "medical MI" in cp2.message.lower() or "RW ต่ำ" in cp2.message


class TestDenyAnalyzer:

    def test_real_deny_analysis(self):
        result = analyze_deny(REAL_DENY_CASE)
        assert result.an == "69-03556"
        assert result.category == "device_documentation"
        assert result.severity == "high"
        assert result.recovery_chance > 0.7
        assert result.estimated_recovery > 50000

    def test_deny_codes_explained(self):
        result = analyze_deny(REAL_DENY_CASE)
        codes = {e.code for e in result.deny_codes_explained}
        assert "HC09" in codes
        assert "IP01" in codes
        assert "HC13" in codes

    def test_fix_steps_exist(self):
        result = analyze_deny(REAL_DENY_CASE)
        assert len(result.fix_steps) > 0
        assert any("stent" in step.lower() or "ADP" in step for step in result.fix_steps)

    def test_clopidogrel_mentioned_in_fix(self):
        result = analyze_deny(REAL_DENY_CASE)
        all_text = " ".join(result.fix_steps) + " " + result.root_cause
        assert "Clopidogrel" in all_text or "clopidogrel" in all_text.lower()

    def test_recommended_action_is_auto_fix(self):
        """HC09 with high recovery chance should recommend auto_fix."""
        result = analyze_deny(REAL_DENY_CASE)
        assert result.recommended_action == "auto_fix"

    def test_confidence_is_reasonable(self):
        result = analyze_deny(REAL_DENY_CASE)
        assert 0.5 <= result.confidence <= 1.0

    def test_appeal_draft_generated_when_needed(self):
        """Test appeal draft for a case that needs appeal."""
        claim = REAL_DENY_CASE.model_copy(update={
            "deny_codes": ["D06"],  # Late submission — lower recovery
        })
        result = analyze_deny(claim)
        # D06 has low recovery, might suggest escalate → appeal draft
        assert result.recommended_action in ("appeal", "escalate", "write_off")
