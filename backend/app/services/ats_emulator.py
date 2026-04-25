"""
Rule-based ATS emulation pipeline.

Every scoring decision is deterministic and auditable.
No ML model — pure rules so the gap is always explainable.

Pipeline:
  1. Keyword match      — JD keyword coverage in resume (45% weight)
  2. Section detection  — standard ATS section headers present (25%)
  3. Formatting         — known ATS parsing failure modes (20%)
  4. School tier        — prestige signal + HBCU proxy flag (10%)

Proxy signal detection runs in parallel and feeds the bias gap
calculation (not the ATS score itself — they're separate outputs).
"""
import re
from collections import Counter

from app.data.school_tiers import get_school_tier


# ── Stop words ────────────────────────────────────────────────────────────────

_STOP = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "must",
    "that", "this", "these", "those", "it", "its", "we", "you", "our",
    "your", "they", "their", "he", "she", "his", "her", "us", "them",
    "i", "me", "my", "not", "no", "nor", "so", "yet", "both", "either",
    "neither", "such", "than", "too", "very", "just", "also", "more",
    "most", "other", "into", "through", "during", "before", "after",
    "above", "below", "between", "each", "about", "up", "down", "out",
    "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "few",
    "more", "some", "such", "own", "same", "than", "who", "whom",
})

# NPHC organizations (historically Black Greek-letter orgs)
_NPHC_ORGS = frozenset({
    "nphc", "alpha kappa alpha", "alpha phi alpha", "delta sigma theta",
    "iota phi theta", "kappa alpha psi", "omega psi phi", "phi beta sigma",
    "sigma gamma rho", "zeta phi beta",
})

# Organizations historically associated with Black professionals
_RACE_PROXY_ORGS = frozenset({
    "nbmbaa", "nsbe", "uncf", "nabj", "nbpa", "urban league", "naacp",
    "national society of black engineers", "national black mba",
    "national association of black journalists",
    "100 black men",
})

# Standard ATS section headers
_SECTION_PATTERNS: dict[str, str] = {
    "experience": r"\b(work\s+)?experience\b|(employment\s+history)\b|(professional\s+experience)\b|(work\s+history)\b",
    "education": r"\beducation\b|(academic\s+(background|history))\b",
    "skills": r"\b(technical\s+)?skills?\b|(core\s+competencies)\b|(areas\s+of\s+expertise)\b|(technologies)\b",
    "summary": r"\b(professional\s+)?summary\b|\bobjective\b|(career\s+(summary|profile))\b|\bprofile\b",
    "certifications": r"\bcertifications?\b|\blicenses?\b|(professional\s+development)\b",
    "projects": r"\bprojects?\b|\bportfolio\b",
}


# ── Tokenizer ─────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s+#]", " ", text)  # keep + and # for C++, C#, etc.
    return [t for t in text.split() if t not in _STOP and len(t) > 1]


def _keyword_freq(text: str, top_n: int = 120) -> dict[str, int]:
    return dict(Counter(_tokenize(text)).most_common(top_n))


# ── 1. Keyword match ──────────────────────────────────────────────────────────

def score_keyword_match(job_description: str, resume_text: str) -> dict:
    jd_kw = _keyword_freq(job_description)
    resume_kw = _keyword_freq(resume_text)

    if not jd_kw:
        return {
            "score": 0.0,
            "matched_keywords": [],
            "missing_keywords": [],
            "total_jd_keywords": 0,
            "matched_count": 0,
        }

    matched = [kw for kw in jd_kw if kw in resume_kw]
    missing = [kw for kw in jd_kw if kw not in resume_kw]

    base_score = len(matched) / len(jd_kw) * 100

    # Bonus: JD terms appearing ≥2x are high-signal requirements
    high_freq = [kw for kw, f in jd_kw.items() if f >= 2]
    high_freq_matched = [kw for kw in high_freq if kw in resume_kw]
    bonus = (len(high_freq_matched) / len(high_freq) * 10) if high_freq else 0

    return {
        "score": round(min(100, base_score + bonus), 1),
        "matched_keywords": matched[:25],
        "missing_keywords": missing[:25],
        "total_jd_keywords": len(jd_kw),
        "matched_count": len(matched),
    }


# ── 2. Section detection ──────────────────────────────────────────────────────

def score_sections(sections: dict) -> dict:
    critical = ["experience", "education", "skills"]
    supplemental = ["summary", "certifications", "projects"]

    critical_found = [s for s in critical if s in sections]
    supp_found = [s for s in supplemental if s in sections]
    missing_critical = [s for s in critical if s not in sections]

    score = (len(critical_found) / len(critical)) * 70
    score += (len(supp_found) / len(supplemental)) * 30

    return {
        "score": round(score, 1),
        "found_sections": list(sections.keys()),
        "missing_critical": missing_critical,
        "missing_supplemental": [s for s in supplemental if s not in sections],
    }


# ── 3. Formatting ─────────────────────────────────────────────────────────────

def score_formatting(parsed_resume: dict) -> dict:
    fmt = parsed_resume.get("formatting", {})
    flags: list[str] = []
    score = 100.0

    if fmt.get("has_images"):
        score -= 15
        flags.append(
            "Images or graphics detected — ATS parsers skip non-text content; "
            "any information inside graphics is invisible to the system"
        )

    if fmt.get("column_count", 1) > 1:
        score -= 10
        flags.append(
            "Multi-column layout detected — most ATS systems read left-to-right "
            "across the full page width, scrambling column-formatted content"
        )

    font_variety = fmt.get("font_variety", 1)
    if font_variety > 4:
        score -= 5
        flags.append(
            f"{font_variety} font families detected — excessive typography can "
            "confuse parsers that infer structure from formatting consistency"
        )

    if fmt.get("has_tables"):
        score -= 10
        flags.append(
            "Table structures detected — ATS systems frequently fail to parse "
            "table content, causing skills and experience rows to be dropped"
        )

    return {
        "score": round(max(0.0, score), 1),
        "flags": flags,
        "ats_optimized": score >= 80,
    }


# ── 4. School tier ────────────────────────────────────────────────────────────

def score_school_tier(schools: list[str]) -> dict:
    if not schools:
        return {"tier_info": [], "proxy_signals": [], "score": 50.0}

    tier_results = [get_school_tier(s) for s in schools]
    proxy_signals: list[str] = []

    for info in tier_results:
        if info.get("is_hbcu"):
            proxy_signals.append(
                f"HBCU attendance ({info['school']}) — Kline et al. (2022) found that "
                "HBCU graduates face additional callback penalties beyond name-based "
                "discrimination in systems with biased training data or screener bias"
            )

    best_tier = min((r["tier"] for r in tier_results), default=4)
    tier_score_map = {1: 100, 2: 85, 3: 70, 4: 55}

    return {
        "tier_info": tier_results,
        "best_tier": best_tier,
        "proxy_signals": proxy_signals,
        "score": float(tier_score_map.get(best_tier, 40)),
    }


# ── Proxy signal detection ────────────────────────────────────────────────────

def detect_proxy_signals(parsed_resume: dict, resume_text: str) -> list[str]:
    """
    Detect non-name demographic proxy signals in the resume.
    These are rule-based and auditable; the LLM layer adds semantic depth.
    """
    signals: list[str] = []
    text_lower = resume_text.lower()

    # ZIP code → geographic redlining vector
    if parsed_resume.get("zip_code"):
        signals.append(
            f"ZIP code present ({parsed_resume['zip_code']}) — geographic data creates "
            "a demographic inference vector. Some hiring systems use zip code proximity "
            "to infer race and socioeconomic background, a documented redlining mechanism "
            "(Quillian et al., 2017)"
        )

    # School proxy signals
    school_result = score_school_tier(parsed_resume.get("schools", []))
    signals.extend(school_result.get("proxy_signals", []))

    # NPHC organizations (Black Greek-letter)
    for org in _NPHC_ORGS:
        if org in text_lower:
            signals.append(
                f"NPHC organization membership detected ('{org}') — historically Black "
                "Greek-letter organizations are recognized demographic proxy signals in "
                "screener systems that penalize cultural affiliation"
            )
            break

    # Other Black professional organizations
    for org in _RACE_PROXY_ORGS:
        if org in text_lower:
            signals.append(
                f"Professional organization '{org.upper()}' detected — affiliation with "
                "organizations historically associated with Black professionals can act as "
                "a demographic proxy signal in biased ATS and human screener contexts"
            )
            break

    # Graduation year — older candidates from majority-HBCU era
    grad_years = re.findall(r"\b(19[6-9]\d|20[0-2]\d)\b", resume_text)
    if grad_years:
        earliest = min(int(y) for y in grad_years)
        if earliest <= 1995:
            signals.append(
                f"Graduation year {earliest} detected — early graduation years can trigger "
                "age discrimination compounded with racial bias in automated systems"
            )

    return signals


# ── Full pipeline ─────────────────────────────────────────────────────────────

def run_ats_score(
    resume_text: str,
    job_description: str,
    parsed_resume: dict,
) -> dict:
    """
    Run the complete rule-based ATS pipeline.
    All weights and decisions are explicit and auditable.
    """
    keyword_result = score_keyword_match(job_description, resume_text)
    section_result = score_sections(parsed_resume.get("sections", {}))
    format_result = score_formatting(parsed_resume)
    school_result = score_school_tier(parsed_resume.get("schools", []))
    proxy_signals = detect_proxy_signals(parsed_resume, resume_text)

    # Weighted composite — mirrors real ATS vendor weightings from published analyses
    composite = (
        keyword_result["score"] * 0.45
        + section_result["score"] * 0.25
        + format_result["score"] * 0.20
        + school_result["score"] * 0.10
    )

    return {
        "composite_score": round(composite, 1),
        "keyword_match": keyword_result,
        "section_detection": section_result,
        "formatting": format_result,
        "school_tier": school_result,
        "proxy_signals": proxy_signals,
        "score_weights": {
            "keyword_match": 0.45,
            "section_detection": 0.25,
            "formatting": 0.20,
            "school_tier": 0.10,
        },
    }
