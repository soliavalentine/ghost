from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.data.disparity_data import (
    INDUSTRY_DISPARITY_DATA,
    RESEARCH_CITATIONS,
    SECTOR_BENCHMARKS,
)
from app.services.scorer import run_full_audit

router = APIRouter(prefix="/api", tags=["audit"])

_ALLOWED_GENDERS = {"male", "female", "nonbinary"}
_MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/audit")
async def audit_resume(
    resume: UploadFile = File(..., description="PDF resume"),
    job_description: str = Form(...),
    applicant_name: str = Form(...),
    gender: str = Form(default="male"),
):
    """
    Run a full three-way bias audit.

    Returns keyword score, ATS compatibility score, and simulated callback score
    for the actual name, a white-coded variant, and a Black-coded variant,
    plus a bias gap analysis grounded in B&M 2004 and Kline et al. 2022.
    """
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        if resume.content_type not in ("application/pdf", "application/octet-stream"):
            raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    if gender not in _ALLOWED_GENDERS:
        raise HTTPException(
            status_code=400,
            detail=f"gender must be one of: {', '.join(sorted(_ALLOWED_GENDERS))}",
        )

    if len(job_description.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description is too short.")

    name_parts = applicant_name.strip().split()
    if len(name_parts) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please provide your full name (first and last).",
        )

    pdf_bytes = await resume.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(pdf_bytes) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="Resume file exceeds 10 MB limit.")

    try:
        result = await run_full_audit(
            resume_bytes=pdf_bytes,
            job_description=job_description.strip(),
            applicant_name=applicant_name.strip(),
            gender=gender,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Audit pipeline failed: {exc}") from exc

    return result


@router.get("/disparity-map")
async def get_disparity_map():
    """
    Return the seeded disparity map data for visualization.

    Seeded from Kline, Rose & Walters (2022) Fortune 500 audit study.
    Community submissions layer starts empty and fills as users run audits.
    """
    return {
        "companies": INDUSTRY_DISPARITY_DATA,
        "sector_benchmarks": SECTOR_BENCHMARKS,
        "citations": RESEARCH_CITATIONS,
        "community_submissions": [],
        "methodology_note": (
            "Data shown is raw reported outcomes from published audit studies — "
            "not causally adjusted. Self-selection effects apply: audit studies "
            "send identical applications, so selection bias is controlled at the "
            "study level. Community submissions are self-reported and unverified; "
            "treat them as directional signal, not causal evidence."
        ),
    }


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ghost-bias-audit-api"}
