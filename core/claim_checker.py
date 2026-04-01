"""
Claim Checker — Main orchestrator.
Combines rule engine + AI engine + department routing.
"""

import asyncio
import logging

from core.models import (
    ClaimInput, ClaimCheckResponse, CheckResult, Severity, Department
)
from core.rule_engine import run_rule_engine, detect_department, calculate_score
from core.ai_engine import analyze_claim

logger = logging.getLogger(__name__)


async def check_claim(claim: ClaimInput) -> ClaimCheckResponse:
    """Full claim validation pipeline."""

    # Step 1: Detect department
    department = detect_department(claim)

    # Step 2: Run deterministic rules
    rule_results = run_rule_engine(claim)

    # Step 3: Run AI analysis (advisory only — does not affect score)
    ai_result = await analyze_claim(claim, department, rule_results)

    # Step 4: Score is based on deterministic rules only.
    # AI analysis is stored as advisory text for human review.
    all_results = rule_results

    # Step 5: Calculate score
    score, ready = calculate_score(all_results)

    # Step 6: Count by severity
    critical_count = sum(1 for r in all_results if r.severity == Severity.CRITICAL)
    warning_count = sum(1 for r in all_results if r.severity == Severity.WARNING)
    passed_count = sum(1 for r in all_results if r.severity == Severity.PASSED)
    optimization_count = sum(1 for r in all_results if r.severity == Severity.OPTIMIZATION)

    return ClaimCheckResponse(
        hn=claim.hn,
        an=claim.an,
        department=department,
        fund=claim.fund,
        principal_dx=claim.principal_dx,
        procedures=claim.procedures,
        results=all_results,
        score=score,
        ready_to_submit=ready,
        critical_count=critical_count,
        warning_count=warning_count,
        passed_count=passed_count,
        optimization_count=optimization_count,
        ai_analysis=ai_result.get("raw_analysis"),
    )


async def check_batch(claims: list[ClaimInput]) -> list[ClaimCheckResponse]:
    """Check multiple claims concurrently with bounded parallelism."""
    semaphore = asyncio.Semaphore(10)

    async def _check_with_limit(claim: ClaimInput) -> ClaimCheckResponse | None:
        async with semaphore:
            try:
                return await check_claim(claim)
            except Exception:
                logger.exception("Failed to check claim HN=%s", claim.hn)
                return None

    raw_results = await asyncio.gather(
        *(_check_with_limit(c) for c in claims)
    )
    results = [r for r in raw_results if r is not None]

    # Sort: critical issues first, then by estimated claim amount
    results.sort(key=lambda r: (r.ready_to_submit, -r.critical_count))
    return results
