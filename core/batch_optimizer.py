"""Batch Claim Optimizer — Process multiple Cath Lab claims, optimize CC/MCC, prioritize by revenue impact."""

from pydantic import BaseModel, Field

from core.cathlab_models import CathLabClaim, CheckResult, DenyAnalysis
from core.cathlab_validator import validate_cathlab_claim
from core.deny_analyzer import analyze_deny
from core.drg_calculator import BASE_RATE_IN_ZONE


# ═══════════════════════════════════════════════
# Output Models
# ═══════════════════════════════════════════════

class ClaimSummary(BaseModel):
    an: str
    hn: str | None = None
    drg: str | None = None
    rw: float | None = None
    charge: float
    score: int
    status: str = Field(description="denied/at_risk/optimizable/ready")
    issues: list[str]
    optimization_potential: float = Field(default=0, description="Extra money possible from CC/MCC")
    priority: int = Field(default=999, description="1=highest priority")


class BatchResult(BaseModel):
    total_claims: int
    summary: dict = Field(description="Counts per status bucket")
    total_charge: float
    total_denied: float
    total_recoverable: float
    total_optimization: float
    claims: list[ClaimSummary] = Field(description="Sorted by priority (1=highest)")
    action_plan: list[str] = Field(description="Prioritized actionable steps")


# ═══════════════════════════════════════════════
# Core Logic
# ═══════════════════════════════════════════════

def _categorize_claim(
    claim: CathLabClaim,
    check: CheckResult,
    deny_analysis: DenyAnalysis | None,
) -> ClaimSummary:
    """Categorize a single claim into a status bucket and compute optimization potential."""

    issues: list[str] = []
    optimization_potential: float = 0

    # Collect issues from checkpoints
    issues.extend(check.errors)
    issues.extend(check.warnings)

    # CC/MCC optimization potential
    if check.optimizations:
        # Use the best single optimization for money_impact (conservative)
        optimization_potential = sum(opt.money_impact for opt in check.optimizations)

    # Check for high-risk indicators beyond just score
    has_critical = any(cp.status == "critical" for cp in check.checkpoints)
    # Missing PDx or missing procedures are fundamental data issues
    has_fundamental_issue = (
        not claim.principal_dx
        or (not claim.procedures and claim.charge_amount > 0)
    )
    warning_count = sum(1 for cp in check.checkpoints if cp.status == "warning")

    # Determine status bucket
    if claim.deny_codes and deny_analysis:
        status = "denied"
    elif check.score < 70 or has_critical or has_fundamental_issue or warning_count >= 4:
        status = "at_risk"
    elif check.optimizations and optimization_potential > 0:
        status = "optimizable"
    else:
        status = "ready"

    return ClaimSummary(
        an=claim.an,
        hn=claim.hn,
        drg=claim.drg,
        rw=claim.rw,
        charge=claim.charge_amount,
        score=check.score,
        status=status,
        issues=issues,
        optimization_potential=optimization_potential,
    )


def _assign_priorities(summaries: list[ClaimSummary], deny_analyses: dict[str, DenyAnalysis]) -> list[ClaimSummary]:
    """Assign priority numbers: denied (by recovery DESC) > at_risk > optimizable > ready."""

    denied = [s for s in summaries if s.status == "denied"]
    at_risk = [s for s in summaries if s.status == "at_risk"]
    optimizable = [s for s in summaries if s.status == "optimizable"]
    ready = [s for s in summaries if s.status == "ready"]

    # Sort denied by estimated_recovery DESC
    denied.sort(
        key=lambda s: deny_analyses[s.an].estimated_recovery if s.an in deny_analyses else 0,
        reverse=True,
    )

    # Sort at_risk by charge DESC (proxy for expected_payment)
    at_risk.sort(key=lambda s: s.charge, reverse=True)

    # Sort optimizable by optimization_potential DESC
    optimizable.sort(key=lambda s: s.optimization_potential, reverse=True)

    # Sort ready by charge DESC
    ready.sort(key=lambda s: s.charge, reverse=True)

    # Assign priorities
    priority = 1
    ordered: list[ClaimSummary] = []
    for group in [denied, at_risk, optimizable, ready]:
        for s in group:
            s.priority = priority
            ordered.append(s)
            priority += 1

    return ordered


def _generate_action_plan(
    summaries: list[ClaimSummary],
    deny_analyses: dict[str, DenyAnalysis],
    check_results: dict[str, CheckResult],
) -> list[str]:
    """Generate prioritized action list in Thai."""

    actions: list[str] = []

    for s in summaries:
        if s.status == "denied" and s.an in deny_analyses:
            da = deny_analyses[s.an]
            chance_pct = int(da.recovery_chance * 100)
            actions.append(
                f"Fix AN {s.an} first — recover {da.estimated_recovery:,.0f} บาท ({chance_pct}% chance)"
            )

        elif s.status == "at_risk":
            top_issue = s.issues[0] if s.issues else "score ต่ำ"
            actions.append(
                f"Review AN {s.an} — score {s.score}/100, at risk: {top_issue}"
            )

        elif s.status == "optimizable" and s.an in check_results:
            cr = check_results[s.an]
            for opt in cr.optimizations:
                actions.append(
                    f"Add {opt.suggested_code} to AN {s.an} — gain {opt.money_impact:,.0f} บาท"
                )

    return actions


# ═══════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════

def optimize_batch(claims: list[CathLabClaim]) -> BatchResult:
    """Process multiple claims: validate, analyze denials, optimize CC/MCC, prioritize by revenue.

    For each claim:
    1. Run validate_cathlab_claim() -> CheckResult
    2. If deny_codes present -> analyze_deny() -> DenyAnalysis
    3. Calculate optimization potential (CC/MCC gaps)

    Returns BatchResult with claims sorted by priority and actionable plan.
    """

    summaries: list[ClaimSummary] = []
    deny_analyses: dict[str, DenyAnalysis] = {}
    check_results: dict[str, CheckResult] = {}

    for claim in claims:
        # Step 1: Validate
        check = validate_cathlab_claim(claim)
        check_results[claim.an] = check

        # Step 2: Deny analysis if applicable
        deny_analysis: DenyAnalysis | None = None
        if claim.deny_codes:
            deny_analysis = analyze_deny(claim)
            deny_analyses[claim.an] = deny_analysis

        # Step 3: Categorize
        summary = _categorize_claim(claim, check, deny_analysis)
        summaries.append(summary)

    # Assign priorities and sort
    ordered = _assign_priorities(summaries, deny_analyses)

    # Generate action plan
    action_plan = _generate_action_plan(ordered, deny_analyses, check_results)

    # Calculate totals
    total_charge = sum(s.charge for s in ordered)
    denied_claims = [s for s in ordered if s.status == "denied"]
    at_risk_claims = [s for s in ordered if s.status == "at_risk"]
    optimizable_claims = [s for s in ordered if s.status == "optimizable"]
    ready_claims = [s for s in ordered if s.status == "ready"]

    total_denied = sum(s.charge for s in denied_claims)
    total_recoverable = sum(
        deny_analyses[s.an].estimated_recovery
        for s in denied_claims
        if s.an in deny_analyses
    )
    total_optimization = sum(s.optimization_potential for s in optimizable_claims)

    summary_counts = {
        "denied": {
            "count": len(denied_claims),
            "amount": round(total_denied, 2),
        },
        "at_risk": {
            "count": len(at_risk_claims),
            "amount": round(sum(s.charge for s in at_risk_claims), 2),
        },
        "optimizable": {
            "count": len(optimizable_claims),
            "amount": round(sum(s.charge for s in optimizable_claims), 2),
            "optimization_potential": round(total_optimization, 2),
        },
        "ready": {
            "count": len(ready_claims),
            "amount": round(sum(s.charge for s in ready_claims), 2),
        },
    }

    return BatchResult(
        total_claims=len(ordered),
        summary=summary_counts,
        total_charge=round(total_charge, 2),
        total_denied=round(total_denied, 2),
        total_recoverable=round(total_recoverable, 2),
        total_optimization=round(total_optimization, 2),
        claims=ordered,
        action_plan=action_plan,
    )
