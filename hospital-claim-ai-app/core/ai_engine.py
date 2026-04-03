"""
AI Engine — Claude API integration for clinical logic validation.
Handles checks that require medical reasoning beyond deterministic rules.
"""

import logging
from functools import lru_cache

import anthropic
from anthropic import APIError, APITimeoutError, RateLimitError
from pathlib import Path
from core.config import get_settings
from core.models import ClaimInput, Department

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Return a singleton Anthropic client (reuses connection pool)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def _call_llm(system: str, user: str, max_tokens: int) -> str:
    """Unified LLM call — Anthropic หรือ Ollama ตาม ai_provider ใน .env"""
    settings = get_settings()

    if settings.ai_provider == "ollama":
        import litellm
        resp = await litellm.acompletion(
            model=f"ollama/{settings.ollama_model}",
            api_base=settings.ollama_base_url,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    # default: Anthropic
    client = _get_client()
    msg = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text if msg.content else ""


@lru_cache(maxsize=16)
def load_knowledge(department: Department) -> str:
    """Load relevant knowledge files for the department (cached)."""
    files_to_load = ["core-rules.md"]

    dept_map = {
        Department.CATH_LAB: "cath-lab.md",
        Department.OR_SURGERY: "or-surgery.md",
        Department.CHEMO: "chemo.md",
        Department.DIALYSIS: "dialysis.md",
        Department.ICU_NICU: "icu-nicu.md",
        Department.ER_UCEP: "er-ucep.md",
        Department.ODS_MIS: "ods-mis.md",
        Department.OPD_NCD: "opd-ncd.md",
        Department.REHAB: "rehab-palliative.md",
    }

    if department in dept_map:
        files_to_load.append(dept_map[department])

    knowledge_text = ""
    for fname in files_to_load:
        fpath = KNOWLEDGE_DIR / fname
        if fpath.exists():
            knowledge_text += f"\n\n--- {fname} ---\n{fpath.read_text()}"

    return knowledge_text


def build_prompt(claim: ClaimInput, department: Department, rule_results: list) -> str:
    """Build the prompt for Claude API."""

    rule_summary = "\n".join(
        f"- [{r.severity.value}] {r.checkpoint}: {r.message}"
        for r in rule_results
    )

    return f"""You are Hospital Claim AI — an expert in Thai DRG coding, NHSO claim submission, and clinical documentation for {department.value}.

Analyze this case and provide additional clinical validation beyond the deterministic rule checks already performed.

## Case Data
- HN: {claim.hn}
- Principal Diagnosis: {claim.principal_dx}
- Secondary Diagnoses: {', '.join(claim.secondary_dx) or 'None'}
- Procedures: {', '.join(claim.procedures) or 'None'}
- Fund: {claim.fund.value}
- Ward: {claim.ward or 'Not specified'}
- Devices: {claim.devices or 'None'}
- Clinical Docs: {claim.clinical_docs or 'Not specified'}
- Admit: {claim.admit_date}
- Discharge: {claim.discharge_date}

## Rule Engine Results (already checked)
{rule_summary}

## Your Tasks
1. **Dx-Proc Clinical Match**: Does the principal diagnosis clinically match the procedures? Flag mismatches.
2. **Clinical Documentation Gaps**: What documentation is missing for this specific diagnosis?
3. **DRG Optimization**: What is the expected DRG group? Are there CC/MCC opportunities missed?
4. **Red Flags**: Any coding patterns that commonly cause denials for this type of case?

## Output Format
Respond in Thai (medical terms in English). Be concise and actionable.
Structure as:
- expected_drg: [DRG group name]
- estimated_rw: [number]
- issues: [list of new issues not already caught by rule engine]
- optimizations: [list of ways to increase DRG weight]
- summary: [1-2 sentence summary]"""


async def analyze_claim(
    claim: ClaimInput,
    department: Department,
    rule_results: list
) -> dict:
    """Send claim to Claude API for clinical analysis."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        return {
            "expected_drg": None,
            "estimated_rw": None,
            "issues": [],
            "optimizations": [],
            "summary": "AI analysis skipped — no API key configured"
        }

    knowledge = load_knowledge(department)
    prompt = build_prompt(claim, department, rule_results)

    try:
        response_text = await _call_llm(
            system=f"You are a Thai hospital claim validation AI. Use this knowledge base:\n{knowledge}",
            user=prompt,
            max_tokens=settings.anthropic_max_tokens,
        )
    except RateLimitError:
        logger.warning("API rate limited — skipping AI analysis")
        return {"raw_analysis": "AI analysis unavailable: rate limited"}
    except (APIError, APITimeoutError, Exception) as e:
        logger.error("LLM error: %s", e)
        return {"raw_analysis": f"AI analysis unavailable: {e}"}

    model_used = (
        f"ollama/{settings.ollama_model}"
        if settings.ai_provider == "ollama"
        else settings.anthropic_model
    )
    return {"raw_analysis": response_text, "model": model_used}


async def generate_appeal(
    claim_data: dict,
    deny_reason: str,
    department: Department
) -> str:
    """Generate appeal letter using Claude API."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        return "Appeal generation skipped — no API key configured"

    knowledge = load_knowledge(department)

    try:
        return await _call_llm(
            system=f"You are an expert in Thai hospital claim appeals. Knowledge:\n{knowledge}",
            user=f"""ร่างหนังสืออุทธรณ์สำหรับเคสนี้:
- HN: {claim_data.get('hn')}
- AN: {claim_data.get('an')}
- Diagnosis: {claim_data.get('principal_dx')}
- Procedures: {claim_data.get('procedures')}
- Deny reason: {deny_reason}
- Department: {department.value}

ใช้ format อุทธรณ์มาตรฐาน ระบุเหตุผลทางคลินิกที่สนับสนุน พร้อมอ้างอิง guidelines""",
            max_tokens=settings.anthropic_max_tokens,
        )
    except RateLimitError:
        logger.warning("API rate limited — appeal generation failed")
        return "Appeal generation failed: rate limited. Please try again later."
    except (APIError, APITimeoutError, Exception) as e:
        logger.error("LLM error during appeal: %s", e)
        return "Appeal generation failed: API error. Please try again later."
