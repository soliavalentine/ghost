"""
Three-way scorer and bias gap calculator.

Scoring model:
  base_ats_score  — rule-based ATS pipeline; IDENTICAL for all three variants
                    because the resume content is identical
  name_bias_factor — research-backed callback rate multiplier from B&M 2004
                    white_coded: 1.000  (baseline)
                    black_coded: 0.679  (6.45/9.5 — documented callback ratio)
                    neutral:     0.850  (conservative interpolation)
  proxy_penalty   — additional penalty when race-correlated signals compound
                    with a Black-coded name (applies to black_coded only)

bias_gap = white_coded_final - black_coded_final

The gap is NOT a model's opinion. It is the arithmetically computed delta
between two pipeline runs that differ only in the name applied, calibrated
to published callback rate data.
"""
import logging

from app.data.names import detect_name_coding
from app.models import AuditResponse, BiasGap, GhostReport, GhostSignal, VariantScore
from app.services.ats_emulator import run_ats_score
from app.services.bias_detector import detect_bias_signals, generate_gap_explanation
from app.services.name_variants import generate_name_variants
from app.services.pdf_parser import parse_resume_pdf

logger = logging.getLogger(__name__)

# B&M 2004 callback rate ratio: white=9.5%, Black=6.45% → 6.45/9.5 ≈ 0.679
_NAME_BIAS_FACTOR: dict[str, float] = {
    "white_coded": 1.000,
    "black_coded": 0.679,
    "neutral": 0.850,
}

_SIGNAL_CLASSIFICATION: dict[str, str] = {
    "zip_code": "optional",
    "graduation_year": "optional",
    "language_register": "optional",
    "volunteer_civic": "optional",
    "hbcu": "load-bearing",
    "cultural_org": "load-bearing",
    "school_prestige": "load-bearing",
}

_SIGNAL_RECOMMENDATIONS: dict[str, str] = {
    "zip_code": (
        "The system reads ZIP codes as neighborhood proxies for race. "
        "City, State is sufficient for ATS parsing and removes a geographic sorting signal."
    ),
    "hbcu": (
        "The system applies prestige-tier penalties to HBCUs independent of academic rigor. "
        "Adding accreditation context — 'SACSCOC Accredited' — provides academic signals "
        "the system recognizes alongside the institutional name."
    ),
    "cultural_org": (
        "The system reads NPHC and Black professional organization names as demographic markers. "
        "Supplementing memberships with the skills and leadership roles they represent creates "
        "keyword matches the system reads as technical qualifications."
    ),
    "graduation_year": (
        "The system compounds name-based signals with graduation year to estimate age. "
        "Year-only formatting (not month/year) reduces the precision of this compounding signal."
    ),
    "language_register": (
        "The system's keyword matching scores standardized industry terminology higher. "
        "Technical sections that mirror job description language directly produce stronger "
        "ATS keyword matches."
    ),
    "school_prestige": (
        "The system applies a fixed prestige-tier score to institutions. Adding program-specific "
        "credentials, rankings, or accreditations where accurate can shift how the system "
        "categorizes the institution."
    ),
    "volunteer_civic": (
        "The system reads community organization names as cultural and geographic signals. "
        "Whether to include them depends on their relevance to the role and how the "
        "organization name reads to automated systems."
    ),
}

_GHOST_BRIDGE_LINE = (
    "You can't fix the system. But you can understand exactly where it's reading you."
)


def build_ghost_report(llm_analysis: dict) -> GhostReport:
    raw_signals = llm_analysis.get("detected_signals", [])
    ghost_signals: list[GhostSignal] = []
    recommendations: list[str] = []
    seen_types: set[str] = set()

    for s in raw_signals:
        signal_type = s.get("signal_type", "other")
        classification = _SIGNAL_CLASSIFICATION.get(signal_type, "optional")
        description = s.get("description", "")
        mechanism = s.get("system_failure_framing") or s.get("mechanism", "")

        if description:
            ghost_signals.append(GhostSignal(
                text=description,
                classification=classification,
                signal_type=signal_type,
                mechanism=mechanism,
            ))

        if signal_type not in seen_types and signal_type in _SIGNAL_RECOMMENDATIONS:
            recommendations.append(_SIGNAL_RECOMMENDATIONS[signal_type])
            seen_types.add(signal_type)

    return GhostReport(
        detected_signals=ghost_signals,
        recommendations=recommendations[:5],
        bridge_line=_GHOST_BRIDGE_LINE,
    )


_METHODOLOGY_NOTE = (
    "Keyword match and ATS compatibility scores are identical across all three variants "
    "because the resume content is identical — only the name differs. "
    "The simulated callback score incorporates the callback rate ratio documented by "
    "Bertrand & Mullainathan (2004): white-coded names receive 50% more callbacks than "
    "Black-coded names on otherwise identical resumes (9.5% vs 6.45% callback rate). "
    "Proxy signal penalties are applied additively to the Black-coded variant based on "
    "published evidence that race-correlated signals compound with name-based discrimination. "
    "This tool measures what systems do, not what candidates should change."
)


def _compute_final_score(
    base_ats: float,
    name_coding: str,
    proxy_count: int,
    apply_proxy_penalty: bool,
) -> float:
    """
    Final simulated callback score for one variant.

    apply_proxy_penalty=True  → Black-coded variant (signals compound)
    apply_proxy_penalty=False → White-coded variant (name buffers signals)
    """
    factor = _NAME_BIAS_FACTOR.get(name_coding, 0.850)
    # Each proxy signal represents a documented additional screening friction.
    # Cap at 15 points to avoid scores going meaninglessly negative.
    proxy_penalty = min(proxy_count * 2.5, 15.0) if apply_proxy_penalty else 0.0
    score = (base_ats * factor) - proxy_penalty
    return round(max(0.0, min(100.0, score)), 1)


async def run_full_audit(
    resume_bytes: bytes,
    job_description: str,
    applicant_name: str,
    gender: str,
) -> AuditResponse:
    """
    Orchestrate the full three-pipeline audit.

    Steps:
      1. Parse PDF
      2. Generate name variants
      3. Run rule-based ATS pipeline (once — results are identical for all variants)
      4. Run LLM bias signal detector (on original resume text)
      5. Merge proxy signals from both detectors
      6. Compute final scores with name bias factor applied per variant
      7. Generate gap explanation via LLM
      8. Assemble AuditResponse
    """
    # ── 1. Parse ──────────────────────────────────────────────────────────────
    parsed_resume = parse_resume_pdf(resume_bytes)

    # Prefer user-supplied name over PDF extraction heuristic
    if applicant_name:
        parsed_resume["name"] = applicant_name

    resume_text = parsed_resume["text"]

    # ── 2. Name variants ──────────────────────────────────────────────────────
    variants = generate_name_variants(applicant_name, resume_text, gender)

    # ── 3. Rule-based ATS (run once) ──────────────────────────────────────────
    base_ats = run_ats_score(resume_text, job_description, parsed_resume)

    # ── 4. LLM bias detection ─────────────────────────────────────────────────
    llm_analysis = await detect_bias_signals(resume_text, job_description)

    # ── 5. Merge proxy signals ────────────────────────────────────────────────
    rule_signals: list[str] = base_ats.get("proxy_signals", [])
    llm_signals: list[str] = [
        s.get("system_failure_framing") or s.get("description", "")
        for s in llm_analysis.get("detected_signals", [])
        if s.get("system_failure_framing") or s.get("description")
    ]
    # Deduplicate while preserving order (rule-based first — they're auditable)
    seen: set[str] = set()
    all_proxy_signals: list[str] = []
    for sig in rule_signals + llm_signals:
        if sig and sig not in seen:
            seen.add(sig)
            all_proxy_signals.append(sig)

    proxy_count = len(all_proxy_signals)
    base_score = base_ats["composite_score"]

    # ── 6. Final scores per variant ───────────────────────────────────────────
    original_coding = detect_name_coding(applicant_name)

    # Original name: apply proxy penalty only if it's Black-coded
    original_apply_proxy = original_coding == "black_coded"
    original_final = _compute_final_score(
        base_score, original_coding, proxy_count, original_apply_proxy
    )
    # White-coded: full factor, no proxy penalty (name buffers signals per research)
    white_final = _compute_final_score(base_score, "white_coded", proxy_count, False)
    # Black-coded: reduced factor, proxy signals compound
    black_final = _compute_final_score(base_score, "black_coded", proxy_count, True)

    # ── 7. Gap explanation ────────────────────────────────────────────────────
    gap_data = await generate_gap_explanation(white_final, black_final, all_proxy_signals)

    # ── 8. Build Ghost Report ─────────────────────────────────────────────────
    ghost_report = build_ghost_report(llm_analysis)

    # ── 9. Assemble response ──────────────────────────────────────────────────
    gap_score = round(white_final - black_final, 1)
    gap_pct = round((gap_score / white_final * 100) if white_final > 0 else 0.0, 1)

    keyword_score = base_ats["keyword_match"]["score"]
    ats_compat_score = round(
        base_ats["section_detection"]["score"] * 0.55
        + base_ats["formatting"]["score"] * 0.45,
        1,
    )

    return AuditResponse(
        actual=VariantScore(
            variant_label="actual",
            variant_name=variants["original"]["name"],
            name_coding=original_coding,
            keyword_score=keyword_score,
            ats_compatibility_score=ats_compat_score,
            simulated_callback_score=original_final,
            proxy_signals_detected=all_proxy_signals[:6],
        ),
        white_coded=VariantScore(
            variant_label="white_coded",
            variant_name=variants["white_coded"]["name"],
            name_coding="white_coded",
            keyword_score=keyword_score,
            ats_compatibility_score=ats_compat_score,
            simulated_callback_score=white_final,
            proxy_signals_detected=[],  # White-coded name buffers these signals
        ),
        black_coded=VariantScore(
            variant_label="black_coded",
            variant_name=variants["black_coded"]["name"],
            name_coding="black_coded",
            keyword_score=keyword_score,
            ats_compatibility_score=ats_compat_score,
            simulated_callback_score=black_final,
            proxy_signals_detected=all_proxy_signals[:6],
        ),
        bias_gap=BiasGap(
            gap_score=gap_score,
            gap_percentage=gap_pct,
            explanation=gap_data.get("explanation", ""),
            driving_signals=gap_data.get("key_mechanisms", []),
            research_grounding=(
                "Bertrand & Mullainathan (2004) AER; Kline, Rose & Walters (2022) QJE"
            ),
            system_accountability=gap_data.get("system_accountability_statement", ""),
        ),
        ghost_report=ghost_report,
        overall_ats_score=base_score,
        ats_breakdown=base_ats,
        llm_bias_analysis=llm_analysis,
        methodology_note=_METHODOLOGY_NOTE,
    )
