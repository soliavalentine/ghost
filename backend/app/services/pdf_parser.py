"""
PDF resume parser using PyMuPDF (fitz).
Extracts structured content: full text, section map, contact info,
school names, skills, and formatting metadata for ATS analysis.
"""
import re
from typing import Optional

import fitz  # PyMuPDF


SECTION_PATTERNS: dict[str, str] = {
    "experience": r"\b(work\s+)?experience\b|(employment\s+history)\b|(professional\s+experience)\b|(work\s+history)\b",
    "education": r"\beducation\b|(academic\s+background)\b|(academic\s+history)\b",
    "skills": r"\b(technical\s+)?skills?\b|(core\s+competencies)\b|(areas\s+of\s+expertise)\b|(technologies)\b",
    "summary": r"\b(professional\s+)?summary\b|\bobjective\b|(career\s+(summary|profile))\b|\bprofile\b",
    "certifications": r"\bcertifications?\b|\blicenses?\b|(professional\s+development)\b",
    "projects": r"\bprojects?\b|\bportfolio\b",
    "awards": r"\bawards?\b|\bachievements?\b|\bhonors?\b|(recognition)\b",
    "volunteer": r"\bvolunteer\b|(community\s+service)\b|\bleadership\b|(civic)\b",
}


def parse_resume_pdf(pdf_bytes: bytes) -> dict:
    """
    Parse a PDF resume and return structured content.

    Returns:
        text: full extracted text
        name: best-guess candidate name (first non-empty line)
        email, phone, zip_code: extracted contact fields
        schools: list of detected institution names
        sections: dict of found section headers
        skills: list of extracted skill tokens
        formatting: dict of ATS-relevant formatting metadata
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    full_text = ""
    has_images = False
    has_tables = False
    font_families: set[str] = set()
    max_x_spread = 0.0

    for page in doc:
        page_text = page.get_text()
        full_text += page_text + "\n"

        if page.get_images():
            has_images = True

        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if b.get("type") == 0]

        if text_blocks:
            x_positions = [b["bbox"][0] for b in text_blocks]
            spread = max(x_positions) - min(x_positions)
            max_x_spread = max(max_x_spread, spread)

        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font = span.get("font", "")
                    if font:
                        # Strip variant suffixes (Bold, Italic, etc.) for family grouping
                        family = re.split(r"[-,]", font)[0]
                        font_families.add(family)

    doc.close()

    column_count = 2 if max_x_spread > 200 else 1

    return {
        "text": full_text,
        "name": _extract_name(full_text),
        "email": _extract_email(full_text),
        "phone": _extract_phone(full_text),
        "zip_code": _extract_zip_code(full_text),
        "schools": _extract_schools(full_text),
        "sections": _extract_sections(full_text),
        "skills": _extract_skills(full_text),
        "formatting": {
            "has_images": has_images,
            "has_tables": has_tables,
            "column_count": column_count,
            "font_families": sorted(font_families),
            "font_variety": len(font_families),
        },
    }


# ── Contact extraction ────────────────────────────────────────────────────────

def _extract_name(text: str) -> Optional[str]:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return None
    first = lines[0]
    # Heuristic: name is short, mixed-case, no @, no digits dominating
    if len(first) <= 60 and "@" not in first and re.search(r"[A-Z][a-z]", first):
        return first
    return None


def _extract_email(text: str) -> Optional[str]:
    m = re.search(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", text[:600])
    return m.group(0) if m else None


def _extract_phone(text: str) -> Optional[str]:
    m = re.search(
        r"(\+?1?\s*[-.]?\s*\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})",
        text[:600],
    )
    return m.group(0).strip() if m else None


def _extract_zip_code(text: str) -> Optional[str]:
    # Only look in first ~600 chars where contact info lives
    matches = re.findall(r"\b(\d{5}(?:-\d{4})?)\b", text[:600])
    return matches[0] if matches else None


# ── Section detection ─────────────────────────────────────────────────────────

def _extract_sections(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in text.split("\n"):
        stripped = line.strip()
        if len(stripped) < 3 or len(stripped) > 55:
            continue
        lower = stripped.lower()
        for section, pattern in SECTION_PATTERNS.items():
            if section not in found and re.search(pattern, lower):
                found[section] = stripped
    return found


# ── School extraction ─────────────────────────────────────────────────────────

_SCHOOL_RE = re.compile(
    r"(?:"
    r"(?:university|college|institute|school)\s+of\s+[\w\s,&]{2,40}"
    r"|[\w\s,&]{2,40}(?:university|college|institute|polytechnic)"
    r")",
    re.IGNORECASE,
)


def _extract_schools(text: str) -> list[str]:
    matches = _SCHOOL_RE.findall(text)
    seen: set[str] = set()
    unique: list[str] = []
    for m in matches:
        key = m.strip().lower()
        if key not in seen and len(key) > 6:
            seen.add(key)
            unique.append(m.strip())
    return unique[:6]


# ── Skills extraction ─────────────────────────────────────────────────────────

def _extract_skills(text: str) -> list[str]:
    skills: list[str] = []
    in_skills = False

    for line in text.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()

        # Detect skills section header
        if re.search(SECTION_PATTERNS["skills"], lower) and len(stripped) < 40:
            in_skills = True
            continue

        if in_skills:
            # Stop when another section starts
            if any(
                re.search(p, lower) and len(stripped) < 40
                for p in SECTION_PATTERNS.values()
            ):
                in_skills = False
                continue
            if stripped:
                items = re.split(r"[,•|·\t]+", stripped)
                skills.extend(i.strip() for i in items if i.strip() and len(i.strip()) > 1)

    return skills[:60]
