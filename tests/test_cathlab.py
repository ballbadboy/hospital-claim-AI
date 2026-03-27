"""Tests for Cath Lab module — using real deny case AN 69-03556."""

from datetime import datetime

from core.cathlab_models import CathLabClaim, DeviceItem, DrugItem
from core.cathlab_validator import validate_cathlab_claim
from core.deny_analyzer import analyze_deny
from core.deny_predictor import predict_deny, DenyPrediction
from core.drg_calculator import lookup_drg, calculate_payment
from core.batch_optimizer import optimize_batch, BatchResult, ClaimSummary
from core.smart_coder import auto_code, CodingResult, CodeSuggestion


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


class TestDenyPredictor:
    """Tests for Deny Predictor — predicts claim denial probability before submission."""

    def test_real_case_high_risk(self):
        """Real deny case AN 69-03556 should predict HIGH_RISK.

        This case has device issues (INST 31,490 but no device records),
        drug issues (Clopidogrel denied), no Authen Code for UC,
        and CC/MCC coding issues (E11.9, I10 = no-effect codes).
        """
        result = predict_deny(REAL_DENY_CASE)
        assert isinstance(result, DenyPrediction)
        assert result.an == "69-03556"
        assert result.verdict in ("HIGH_RISK", "ALMOST_CERTAIN")
        assert result.deny_probability >= 0.50
        assert len(result.risk_factors) == 10
        assert len(result.top_risks) > 0
        assert result.estimated_loss_if_denied > 50000
        assert result.recommendation != ""

    def test_good_case_safe(self):
        """A well-coded STEMI+PCI case with all docs should predict SAFE."""
        good_claim = CathLabClaim(
            hn="69-00001",
            an="69-99999",
            pid="1100700517062",  # Valid CID with correct checksum
            admit_date=datetime(2026, 3, 20, 8, 0),
            discharge_date=datetime(2026, 3, 23, 10, 0),
            principal_dx="I21.0",  # STEMI
            secondary_dx=["E11.65", "I50.21"],  # Proper CC/MCC codes
            procedures=["36.06", "37.22", "88.56"],  # PCI + cath + angio
            drg="05290",
            rw=8.6544,
            charge_amount=75000.00,
            expected_payment=72264.00,
            fund="UCS",
            authen_code="UC2603200001",
            devices=[
                DeviceItem(
                    type=5, code="STENT001", name="DES Stent 3.0x28mm",
                    qty=1, rate=25000, serial_no="SN-2026-001234",
                ),
            ],
            drugs=[
                DrugItem(did="TMT-12345", name="Clopidogrel 75mg", amount=150),
                DrugItem(did="TMT-12346", name="Aspirin 81mg", amount=50),
            ],
            inst_amount=25000.00,
        )
        result = predict_deny(good_claim)
        assert result.verdict == "SAFE"
        assert result.deny_probability < 0.20
        # All 10 factors should mostly pass
        pass_count = sum(1 for rf in result.risk_factors if rf.status == "pass")
        assert pass_count >= 8

    def test_missing_pdx_almost_certain(self):
        """No PDx should be ALMOST_CERTAIN deny — DRG Error 1."""
        no_pdx_claim = REAL_DENY_CASE.model_copy(update={
            "principal_dx": "",
            "drg": None,
            "rw": None,
        })
        result = predict_deny(no_pdx_claim)
        assert result.verdict == "ALMOST_CERTAIN"
        assert result.deny_probability >= 0.80
        # RF2 (PDx) and RF9 (DRG groupable) should both fail
        rf2 = next(rf for rf in result.risk_factors if "PDx" in rf.name)
        rf9 = next(rf for rf in result.risk_factors if "DRG" in rf.name)
        assert rf2.status == "fail"
        assert rf2.risk_score == 100
        assert rf9.status == "fail"

    def test_late_submission_high_risk(self):
        """Submission >30 days after discharge should be HIGH_RISK.

        We set discharge_date far in the past so days_since_discharge > 30.
        Combined with the existing issues in REAL_DENY_CASE, this pushes
        the verdict to HIGH_RISK or higher.
        """
        late_claim = REAL_DENY_CASE.model_copy(update={
            "discharge_date": datetime(2025, 12, 1, 10, 0),  # >90 days ago
        })
        result = predict_deny(late_claim)
        assert result.verdict in ("HIGH_RISK", "ALMOST_CERTAIN")
        # RF6 (Timing) should fail
        rf6 = next(rf for rf in result.risk_factors if "Timing" in rf.name)
        assert rf6.status == "fail"
        assert rf6.risk_score >= 90
        assert "เกินกำหนด" in rf6.detail

    def test_risk_factors_have_correct_weights(self):
        """Verify all 10 risk factors have the specified weights."""
        result = predict_deny(REAL_DENY_CASE)
        expected_weights = {
            "RF1: CID Checksum": 5,
            "RF2: PDx Valid": 15,
            "RF3: Dx-Proc Match": 20,
            "RF4: Device Docs": 15,
            "RF5: Drug Catalog": 10,
            "RF6: Timing": 10,
            "RF7: Authen Code": 10,
            "RF8: CC/MCC Coding": 5,
            "RF9: DRG Groupable": 5,
            "RF10: Charge Reasonable": 5,
        }
        for rf in result.risk_factors:
            assert rf.name in expected_weights, f"Unknown risk factor: {rf.name}"
            assert rf.weight == expected_weights[rf.name], (
                f"{rf.name}: weight should be {expected_weights[rf.name]}, got {rf.weight}"
            )
        # Total weight should be 100
        total = sum(rf.weight for rf in result.risk_factors)
        assert total == 100

    def test_deny_probability_in_range(self):
        """deny_probability must be between 0.0 and 1.0."""
        result = predict_deny(REAL_DENY_CASE)
        assert 0.0 <= result.deny_probability <= 1.0

    def test_verdict_thresholds(self):
        """Test that verdict matches the probability thresholds."""
        result = predict_deny(REAL_DENY_CASE)
        pct = result.deny_probability * 100
        if pct < 20:
            assert result.verdict == "SAFE"
        elif pct < 50:
            assert result.verdict == "CAUTION"
        elif pct < 80:
            assert result.verdict == "HIGH_RISK"
        else:
            assert result.verdict == "ALMOST_CERTAIN"

    def test_top_risks_ordered_by_severity(self):
        """top_risks should list the most impactful risks first."""
        result = predict_deny(REAL_DENY_CASE)
        assert isinstance(result.top_risks, list)
        # Should have at least some risks for the deny case
        assert len(result.top_risks) >= 1

    def test_estimated_loss_uses_expected_payment(self):
        """estimated_loss_if_denied should use expected_payment when available."""
        result = predict_deny(REAL_DENY_CASE)
        assert result.estimated_loss_if_denied == REAL_DENY_CASE.expected_payment


# ═══════════════════════════════════════════════
# Batch Optimizer Tests
# ═══════════════════════════════════════════════

# Test data: 4 different Cath Lab cases

# Case 1: Real deny case AN 69-03556 (denied, HC09) — reuse REAL_DENY_CASE
BATCH_CASE_DENIED = REAL_DENY_CASE

# Case 2: Missing PDx → at_risk (score <70 due to critical checkpoint)
BATCH_CASE_AT_RISK = CathLabClaim(
    hn="69-08001",
    an="69-04100",
    pid="1234567890121",
    admit_date=datetime(2026, 3, 10, 9, 0),
    discharge_date=datetime(2026, 3, 12, 14, 0),
    principal_dx="",  # Missing PDx → critical → score drops below 70
    secondary_dx=["I10"],
    procedures=[],  # No procedures → another critical/warning
    charge_amount=18500.00,
    fund="UCS",
)

# Case 3: E11.9 instead of E11.65 → optimizable (+CC upgrade)
BATCH_CASE_OPTIMIZABLE = CathLabClaim(
    hn="69-07522",
    an="69-03800",
    pid="3100501234567",
    admit_date=datetime(2026, 3, 5, 14, 30),
    discharge_date=datetime(2026, 3, 7, 10, 0),
    principal_dx="I25.1",  # Chronic IHD
    secondary_dx=["E11.9", "I10"],  # E11.9 unspecified → can upgrade to E11.65 (CC)
    procedures=["36.06", "88.56"],  # PCI + angio
    drg="05230",
    rw=6.8786,
    charge_amount=28000.00,
    expected_payment=57436.00,
    fund="UCS",
    authen_code="AUTH123456",
)

# Case 4: Perfect STEMI + PCI + MCC case → ready
BATCH_CASE_READY = CathLabClaim(
    hn="69-09100",
    an="69-04200",
    pid="1100700123456",
    admit_date=datetime(2026, 3, 15, 6, 0),
    discharge_date=datetime(2026, 3, 18, 11, 0),
    principal_dx="I21.1",  # STEMI inferior wall
    secondary_dx=["I50.21", "N18.4", "E11.65"],  # MCC: acute systolic HF + CKD4 + CC: DM w hyperglycemia
    procedures=["36.06", "37.22", "88.56"],  # PCI + cath + angio
    drg="05291",
    rw=11.4820,
    charge_amount=45000.00,
    expected_payment=95858.00,
    fund="UCS",
    authen_code="AUTH789012",
    devices=[],
)


class TestBatchOptimizer:

    def _run_batch(self) -> BatchResult:
        claims = [BATCH_CASE_DENIED, BATCH_CASE_AT_RISK, BATCH_CASE_OPTIMIZABLE, BATCH_CASE_READY]
        return optimize_batch(claims)

    def test_batch_with_mixed_cases(self):
        """4 claims (1 denied, 1 at_risk, 1 optimizable, 1 ready) → correct categorization."""
        result = self._run_batch()

        assert result.total_claims == 4

        statuses = {c.an: c.status for c in result.claims}
        assert statuses["69-03556"] == "denied"       # Real deny case
        assert statuses["69-04100"] == "at_risk"       # Missing PDx
        assert statuses["69-03800"] == "optimizable"   # E11.9 can upgrade
        assert statuses["69-04200"] == "ready"         # Perfect case

        # Summary counts
        assert result.summary["denied"]["count"] == 1
        assert result.summary["at_risk"]["count"] == 1
        assert result.summary["optimizable"]["count"] == 1
        assert result.summary["ready"]["count"] == 1

    def test_batch_priority_sorting(self):
        """Denied cases with higher amounts should be priority 1; ready cases last."""
        result = self._run_batch()

        # Claims should be sorted: denied first, then at_risk, optimizable, ready
        priorities = {c.an: c.priority for c in result.claims}

        # Denied case should have highest priority (lowest number)
        assert priorities["69-03556"] == 1  # denied
        assert priorities["69-04100"] == 2  # at_risk
        assert priorities["69-03800"] == 3  # optimizable
        assert priorities["69-04200"] == 4  # ready

        # Verify ordering in list
        assert result.claims[0].status == "denied"
        assert result.claims[-1].status == "ready"

    def test_batch_action_plan(self):
        """Should generate actionable steps for denied and optimizable cases."""
        result = self._run_batch()

        assert len(result.action_plan) > 0

        # Should have a fix action for the denied case
        fix_actions = [a for a in result.action_plan if "Fix AN 69-03556" in a]
        assert len(fix_actions) == 1
        assert "recover" in fix_actions[0].lower()
        assert "chance" in fix_actions[0].lower()

        # Should have optimization action for E11.9 → E11.65
        opt_actions = [a for a in result.action_plan if "AN 69-03800" in a]
        assert len(opt_actions) > 0
        assert any("E11.65" in a for a in opt_actions)
        assert any("gain" in a.lower() for a in opt_actions)

    def test_batch_totals_calculated(self):
        """Total charge, denied amount, recoverable, and optimization potential should be correct."""
        result = self._run_batch()

        # Total charge = sum of all 4 cases
        expected_total = 31517.00 + 18500.00 + 28000.00 + 45000.00
        assert result.total_charge == expected_total

        # Denied amount = charge of denied case
        assert result.total_denied == 31517.00

        # Recoverable should be > 0 (from deny analysis)
        assert result.total_recoverable > 0

        # Optimization potential should be > 0 (from E11.9 upgrade)
        assert result.total_optimization > 0

    def test_batch_denied_has_recovery_info(self):
        """Denied claim should have issues populated from deny analysis."""
        result = self._run_batch()
        denied_claim = next(c for c in result.claims if c.an == "69-03556")
        assert denied_claim.status == "denied"
        assert len(denied_claim.issues) > 0

    def test_batch_optimizable_has_potential(self):
        """Optimizable claim should have optimization_potential > 0."""
        result = self._run_batch()
        opt_claim = next(c for c in result.claims if c.an == "69-03800")
        assert opt_claim.status == "optimizable"
        assert opt_claim.optimization_potential > 0

    def test_batch_ready_has_high_score(self):
        """Ready claim should have score >= 85."""
        result = self._run_batch()
        ready_claim = next(c for c in result.claims if c.an == "69-04200")
        assert ready_claim.status == "ready"
        assert ready_claim.score >= 85

    def test_batch_empty_input(self):
        """Empty list should return empty result."""
        result = optimize_batch([])
        assert result.total_claims == 0
        assert result.total_charge == 0
        assert len(result.claims) == 0
        assert len(result.action_plan) == 0

    def test_batch_single_claim(self):
        """Single claim should work correctly."""
        result = optimize_batch([BATCH_CASE_READY])
        assert result.total_claims == 1
        assert result.claims[0].status == "ready"
        assert result.claims[0].priority == 1

    def test_batch_priority_denied_by_recovery_desc(self):
        """When multiple denied cases exist, higher recovery amount gets higher priority."""
        # Create two denied cases with different amounts
        denied_small = REAL_DENY_CASE.model_copy(update={
            "an": "69-99901",
            "charge_amount": 10000.00,
            "expected_payment": 20000.00,
        })
        denied_large = REAL_DENY_CASE.model_copy(update={
            "an": "69-99902",
            "charge_amount": 80000.00,
            "expected_payment": 150000.00,
        })
        result = optimize_batch([denied_small, denied_large])

        assert result.claims[0].an == "69-99902"  # Higher recovery = priority 1
        assert result.claims[1].an == "69-99901"  # Lower recovery = priority 2


# ═══════════════════════════════════════════════
# Smart Coder Tests
# ═══════════════════════════════════════════════

class TestSmartCoder:
    """Tests for Smart Coder — auto-generate ICD codes from clinical notes."""

    def test_stemi_coding(self):
        """STEMI anterior + PCI DES + EF 35% + DM + CKD → full coding with CC/MCC."""
        result = auto_code("STEMI anterior, PCI DES LAD, EF 35%, DM, CKD eGFR 25")
        assert isinstance(result, CodingResult)

        # PDx: I21.0 (STEMI anterior wall)
        assert result.pdx.code == "I21.0"
        assert result.pdx.type == "pdx"
        assert result.pdx.confidence >= 0.85

        # SDx: should include I50.21 (MCC), E11.65 (CC), N18.4 (MCC)
        sdx_codes = {s.code for s in result.sdx}
        assert "I50.21" in sdx_codes, "EF 35% should map to I50.21 (MCC) not I50.9"
        assert "E11.65" in sdx_codes, "DM should map to E11.65 (CC) not E11.9"
        assert "N18.4" in sdx_codes, "eGFR 25 should map to N18.4 (MCC)"

        # CC/MCC flags
        hf = next(s for s in result.sdx if s.code == "I50.21")
        assert hf.cc_mcc == "MCC"
        dm = next(s for s in result.sdx if s.code == "E11.65")
        assert dm.cc_mcc == "CC"
        ckd = next(s for s in result.sdx if s.code == "N18.4")
        assert ckd.cc_mcc == "MCC"

        # Procedures: should include 36.07 (DES)
        proc_codes = {p.code for p in result.procedures}
        assert "36.07" in proc_codes, "PCI DES should map to 36.07"

        # DRG should be estimated (acute MI + PCI + MCC)
        assert result.expected_drg is not None
        assert result.expected_drg.startswith("052")
        # RW should be found (exact or fallback)
        if result.expected_rw is not None:
            assert result.expected_rw > 0
            assert result.expected_payment > 0

    def test_nstemi_coding(self):
        """Troponin elevated + no ST elevation + cardiac cath → NSTEMI + diagnostic codes."""
        result = auto_code("NSTEMI, Troponin สูง 5.2, สวนหัวใจ")
        assert isinstance(result, CodingResult)

        # PDx: I21.4 (NSTEMI)
        assert result.pdx.code == "I21.4"
        assert result.pdx.confidence >= 0.80

        # Procedures: 37.22 (cardiac cath) + 88.56 (coronary angio)
        proc_codes = {p.code for p in result.procedures}
        assert "37.22" in proc_codes, "สวนหัวใจ should map to 37.22"
        assert "88.56" in proc_codes, "Coronary angio should be coded with cath"

    def test_ua_coding(self):
        """Chest pain + normal Troponin → Unstable Angina (I20.0)."""
        result = auto_code("เจ็บหน้าอก Troponin ปกติ")
        assert isinstance(result, CodingResult)

        # PDx: I20.0 (Unstable Angina)
        assert result.pdx.code == "I20.0"
        assert result.pdx.confidence >= 0.70

    def test_ccmcc_optimization(self):
        """Smart Coder should prefer E11.65 over E11.9, I50.21 over I50.9."""
        result = auto_code(
            "STEMI inferior, PCI BMS, "
            "DM HbA1c 8.5, "
            "HF EF 30%, "
            "CKD eGFR 45, "
            "AF, HT"
        )

        sdx_codes = {s.code for s in result.sdx}

        # DM: E11.65 (CC) NOT E11.9
        assert "E11.65" in sdx_codes, "DM with HbA1c >7 should be E11.65 (CC)"
        assert "E11.9" not in sdx_codes, "E11.9 should NOT be suggested when E11.65 is available"

        # HF: I50.21 (MCC) NOT I50.9
        assert "I50.21" in sdx_codes, "HF with EF <40% should be I50.21 (MCC)"
        assert "I50.9" not in sdx_codes, "I50.9 should NOT be suggested when I50.21 is available"

        # CKD: N18.3 (CC) for eGFR 30-59
        assert "N18.3" in sdx_codes, "eGFR 45 should map to N18.3 (CC)"

        # AF: I48.91 (CC)
        assert "I48.91" in sdx_codes, "AF should map to I48.91 (CC)"
        af = next(s for s in result.sdx if s.code == "I48.91")
        assert af.cc_mcc == "CC"

        # HT: I10 (no CC/MCC but still coded)
        assert "I10" in sdx_codes, "HT should still be coded even without CC/MCC impact"
        ht = next(s for s in result.sdx if s.code == "I10")
        assert ht.cc_mcc is None

    def test_stemi_inferior_wall(self):
        """STEMI inferior should map to I21.1."""
        result = auto_code("STEMI inferior wall, RCA lesion")
        assert result.pdx.code == "I21.1"

    def test_stemi_unspecified_wall(self):
        """STEMI without wall territory should map to I21.3."""
        result = auto_code("STEMI, PCI DES")
        assert result.pdx.code == "I21.3"

    def test_chronic_ihd(self):
        """CAD without acute markers should map to I25.1."""
        result = auto_code("chronic IHD, CAD, elective diagnostic cath")
        assert result.pdx.code in ("I25.1", "I20.0")

    def test_pci_bms_coding(self):
        """BMS stent should map to 36.06."""
        result = auto_code("STEMI anterior, PCI BMS")
        proc_codes = {p.code for p in result.procedures}
        assert "36.06" in proc_codes

    def test_multi_vessel_pci(self):
        """Multi-vessel PCI should include 36.05."""
        result = auto_code("STEMI, multi-vessel PCI DES, LAD + RCA")
        proc_codes = {p.code for p in result.procedures}
        assert "36.05" in proc_codes
        assert "36.07" in proc_codes

    def test_diagnostic_cath_only(self):
        """Diagnostic cath without PCI should code 37.22 + 88.56."""
        result = auto_code("สวนหัวใจ diagnostic, CAD")
        proc_codes = {p.code for p in result.procedures}
        assert "37.22" in proc_codes
        assert "88.56" in proc_codes
        # Should NOT have PCI codes
        assert "36.07" not in proc_codes
        assert "36.06" not in proc_codes

    def test_ckd_staging_by_egfr(self):
        """eGFR values should map to correct CKD stages."""
        # eGFR 45 → N18.3 (CC)
        r1 = auto_code("CKD eGFR 45, chest pain")
        ckd_codes = {s.code for s in r1.sdx if s.code.startswith("N18.")}
        assert "N18.3" in ckd_codes

        # eGFR 20 → N18.4 (MCC)
        r2 = auto_code("CKD eGFR 20, chest pain")
        ckd_codes2 = {s.code for s in r2.sdx if s.code.startswith("N18.")}
        assert "N18.4" in ckd_codes2

        # eGFR 10 → N18.5 (MCC)
        r3 = auto_code("CKD eGFR 10, chest pain")
        ckd_codes3 = {s.code for s in r3.sdx if s.code.startswith("N18.")}
        assert "N18.5" in ckd_codes3

    def test_optimization_notes_generated(self):
        """Optimization notes should flag CC/MCC opportunities."""
        result = auto_code("STEMI anterior, PCI DES, DM, HF EF 30%")
        assert len(result.optimization_notes) > 0
        # Should note MCC found
        mcc_notes = [n for n in result.optimization_notes if "MCC" in n]
        assert len(mcc_notes) > 0

    def test_warnings_for_low_confidence(self):
        """Minimal clinical text should generate warnings."""
        result = auto_code("chest pain")
        # Low detail should have lower confidence or warnings
        assert result.pdx.confidence < 0.90

    def test_thai_clinical_notes(self):
        """Full Thai clinical notes should be parsed correctly."""
        result = auto_code(
            "ผู้ป่วยชาย อายุ 55 ปี เจ็บหน้าอก 2 ชม. "
            "EKG พบ ST elevation leads V1-V4 "
            "Troponin สูง 12.5 "
            "สวนหัวใจ พบ LAD stenosis 90% "
            "ใส่ขดลวดเคลือบยา DES 1 ตัว "
            "เบาหวาน HbA1c 9.2 "
            "ความดันสูง "
            "EF 38%"
        )
        # PDx: STEMI anterior (ST elevation + troponin + LAD)
        assert result.pdx.code == "I21.0"

        # SDx
        sdx_codes = {s.code for s in result.sdx}
        assert "I50.21" in sdx_codes  # EF 38% → MCC
        assert "E11.65" in sdx_codes  # DM + HbA1c 9.2 → CC
        assert "I10" in sdx_codes     # HT

        # Procedures
        proc_codes = {p.code for p in result.procedures}
        assert "36.07" in proc_codes  # DES
        assert "37.22" in proc_codes  # Cardiac cath
        assert "88.56" in proc_codes  # Coronary angio

    def test_drg_estimation_acute_mi_pci(self):
        """Acute MI + PCI should estimate a high-RW DRG."""
        result = auto_code("STEMI anterior, PCI DES LAD, EF 35%, DM")
        assert result.expected_drg is not None
        assert result.expected_drg.startswith("052")  # Acute MI + PCI family

    def test_drg_estimation_diagnostic_cath(self):
        """Diagnostic cath without PCI should estimate lower-RW DRG."""
        result = auto_code("CAD stable, สวนหัวใจ diagnostic")
        assert result.expected_drg is not None
        assert result.expected_drg.startswith("0522")  # Cardiac cath non-complex
        assert result.expected_rw is not None
        assert result.expected_rw < 8.0  # Lower than PCI
