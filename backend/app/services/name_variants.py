"""
Name variant generator.
Replaces the applicant's name in the resume text with white-coded
and Black-coded alternatives drawn from the B&M 2004 name lists.
Replacement is deterministic (seeded by original name) so the same
input always produces the same variants.
"""
import re

from app.data.names import detect_name_coding, select_variant_names


def _replace_name(text: str, original: str, replacement: str) -> str:
    """
    Case-aware name replacement.
    Handles full name, first-only, and last-only occurrences.
    Preserves surrounding whitespace and punctuation.
    """
    if not original or not replacement:
        return text

    orig_parts = original.split()
    repl_parts = replacement.split()

    result = text

    # Full name (most specific — do first to avoid double-replacing parts)
    result = re.sub(
        r"\b" + re.escape(original) + r"\b",
        replacement,
        result,
        flags=re.IGNORECASE,
    )

    # First name
    if orig_parts and repl_parts:
        result = re.sub(
            r"\b" + re.escape(orig_parts[0]) + r"\b",
            repl_parts[0],
            result,
            flags=re.IGNORECASE,
        )

    # Last name
    if len(orig_parts) >= 2 and len(repl_parts) >= 2:
        result = re.sub(
            r"\b" + re.escape(orig_parts[-1]) + r"\b",
            repl_parts[-1],
            result,
            flags=re.IGNORECASE,
        )

    return result


def generate_name_variants(
    original_name: str,
    resume_text: str,
    gender: str,
) -> dict:
    """
    Generate all three name variants.

    Returns:
        {
            "original":    {name, text, coding},
            "white_coded": {name, text, coding},
            "black_coded": {name, text, coding},
        }
    """
    white_name, black_name = select_variant_names(original_name, gender)

    return {
        "original": {
            "name": original_name,
            "text": resume_text,
            "coding": detect_name_coding(original_name),
        },
        "white_coded": {
            "name": white_name,
            "text": _replace_name(resume_text, original_name, white_name),
            "coding": "white_coded",
        },
        "black_coded": {
            "name": black_name,
            "text": _replace_name(resume_text, original_name, black_name),
            "coding": "black_coded",
        },
    }
