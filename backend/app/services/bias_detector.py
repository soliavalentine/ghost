"""
LLM-powered bias signal detector using Groq (llama-3.3-70b-versatile).
Adds semantic understanding that rule-based detection misses:
language register, cultural reference density, implicit affiliation signals.

All output is framed as system failure, not candidate flaw.
"""
import json
import logging

from groq import AsyncGroq

from app.config import settings

logger = logging.getLogger(__name__)

_BIAS_SIGNAL_PROMPT = """\
You are an expert in labor economics and algorithmic hiring discrimination.
Your task is to analyze a resume for proxy signals that published research
shows correlate with demographic filtering in automated hiring systems.

Resume text (truncated to 3000 chars):
---
{resume_text}
---

Job description (truncated to 1500 chars):
---
{job_description}
---

Analyze for the following proxy signal categories:
1. ZIP/location data enabling geographic redlining
2. School prestige tier and HBCU attendance markers
3. Cultural or racial organization affiliations (Greek-letter, professional associations)
4. Language register and cultural reference density (signals in-group membership)
5. Graduation years that compound with age/era discrimination
6. Volunteer or civic affiliations that function as demographic markers
7. Any other signals documented in hiring bias literature

For EVERY signal found, describe:
- What exactly appears in the resume
- The specific mechanism by which it triggers bias in ATS or human screening
- Frame it as a system failure, not a candidate flaw

Respond ONLY with valid JSON in exactly this shape:
{{
  "detected_signals": [
    {{
      "signal_type": "zip_code | school_prestige | hbcu | cultural_org | graduation_year | language_style | civic_affiliation | other",
      "description": "what appears in the resume",
      "mechanism": "how this triggers demographic filtering",
      "severity": "high | medium | low",
      "system_failure_framing": "one sentence describing this as a system failure"
    }}
  ],
  "overall_vulnerability_score": 0,
  "narrative_explanation": "2-3 sentence plain-English summary of total bias exposure",
  "driving_signals": ["top signal 1", "top signal 2", "top signal 3"]
}}

If no signals are found, return an empty detected_signals array.
Do not include markdown, code fences, or any text outside the JSON object.\
"""

_GAP_EXPLANATION_PROMPT = """\
You are communicating hiring bias audit results to a job seeker.
Tone: serious, clinical, factual. Never sensational. Never suggest the
candidate hide their identity or change who they are.

Frame ALL findings as: "The system does X to you" — never "You should do Y."

Audit data:
- White-coded name variant simulated callback score: {white_score}/100
- Black-coded name variant simulated callback score: {black_score}/100
- Raw gap: {gap} points ({gap_pct}% lower for Black-coded variant)
- Detected proxy signals in resume:
{proxy_signals_text}
- Research baseline: Bertrand & Mullainathan (2004) documented that white-coded
  names receive 50% more callbacks than Black-coded names on identical resumes.
  Kline, Rose & Walters (2022) replicated this across 108 Fortune 500 firms.

Write a 3-4 sentence explanation of WHY this gap exists — be specific about
mechanisms, cite the research, name the system failure.

Respond ONLY with valid JSON in exactly this shape:
{{
  "explanation": "3-4 sentence explanation citing mechanisms and research",
  "key_mechanisms": ["mechanism 1", "mechanism 2", "mechanism 3"],
  "system_accountability_statement": "one sentence naming the class of system failure"
}}

Do not include markdown, code fences, or any text outside the JSON object.\
"""


async def detect_bias_signals(resume_text: str, job_description: str) -> dict:
    """
    Use Groq LLM to detect semantic bias proxy signals.
    Falls back to a minimal safe response on any API failure.
    """
    client = AsyncGroq(api_key=settings.groq_api_key)

    prompt = _BIAS_SIGNAL_PROMPT.format(
        resume_text=resume_text[:3000],
        job_description=job_description[:1500],
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1800,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)

    except Exception as exc:
        logger.warning("Groq bias detection failed: %s", exc)
        return {
            "detected_signals": [],
            "overall_vulnerability_score": 50,
            "narrative_explanation": (
                "Automated semantic analysis unavailable. Rule-based signals above "
                "were still detected and are included in the bias gap calculation."
            ),
            "driving_signals": [],
        }


async def generate_gap_explanation(
    white_score: float,
    black_score: float,
    all_proxy_signals: list[str],
) -> dict:
    """
    Generate a plain-English explanation of the bias gap grounded in research.
    Falls back to a hardcoded research-grounded explanation on API failure.
    """
    client = AsyncGroq(api_key=settings.groq_api_key)

    gap = round(white_score - black_score, 1)
    gap_pct = round((gap / white_score * 100) if white_score > 0 else 0.0, 1)

    signals_text = (
        "\n".join(f"  - {s}" for s in all_proxy_signals)
        if all_proxy_signals
        else "  None detected beyond name-based scoring"
    )

    prompt = _GAP_EXPLANATION_PROMPT.format(
        white_score=white_score,
        black_score=black_score,
        gap=gap,
        gap_pct=gap_pct,
        proxy_signals_text=signals_text,
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)

    except Exception as exc:
        logger.warning("Groq gap explanation failed: %s", exc)
        return {
            "explanation": (
                f"Bertrand & Mullainathan (2004) documented that white-coded names receive "
                f"50% more callbacks than Black-coded names on otherwise identical resumes — "
                f"a gap replicated by Kline, Rose & Walters (2022) across 108 Fortune 500 firms. "
                f"The {gap}-point gap shown here ({gap_pct}%) reflects that documented callback "
                f"rate differential applied to this resume's base ATS score. "
                f"This is not a flaw in the resume; it is a measurable output of discriminatory systems."
            ),
            "key_mechanisms": [
                "Name-based statistical discrimination (callback rate disparity documented across 20+ years of audit studies)",
                "Proxy signal amplification (race-correlated resume features compound with name-based bias)",
                "Structural screener bias (ATS systems trained on historically filtered applicant pools)",
            ],
            "system_accountability_statement": (
                "This gap is a system failure: identical qualifications are being evaluated "
                "differently based on perceived demographic identity inferred from a name."
            ),
        }
