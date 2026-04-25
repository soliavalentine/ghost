from pydantic import BaseModel, Field
from typing import Literal, Any


class GhostSignal(BaseModel):
    text: str
    classification: Literal["optional", "load-bearing"]
    signal_type: str
    mechanism: str


class GhostReport(BaseModel):
    detected_signals: list[GhostSignal]
    recommendations: list[str]
    bridge_line: str


class VariantScore(BaseModel):
    variant_label: Literal["actual", "white_coded", "black_coded"]
    variant_name: str
    name_coding: str  # "white_coded", "black_coded", or "neutral"

    # Identical for all three variants — honest: same resume content
    keyword_score: float = Field(..., description="JD keyword match 0-100, same for all variants")
    ats_compatibility_score: float = Field(..., description="Format + section score 0-100, same for all variants")

    # Research-backed callback simulation — differs by variant
    simulated_callback_score: float = Field(..., description="Simulated callback probability 0-100, incorporates B&M 2004 name bias factor")
    proxy_signals_detected: list[str]


class BiasGap(BaseModel):
    gap_score: float
    gap_percentage: float
    explanation: str
    driving_signals: list[str]
    research_grounding: str
    system_accountability: str


class AuditResponse(BaseModel):
    actual: VariantScore
    white_coded: VariantScore
    black_coded: VariantScore
    bias_gap: BiasGap
    ghost_report: GhostReport
    overall_ats_score: float
    ats_breakdown: dict[str, Any]
    llm_bias_analysis: dict[str, Any]
    methodology_note: str


class DisparityMapResponse(BaseModel):
    companies: list[dict]
    sector_benchmarks: dict
    citations: list[dict]
    community_submissions: list[dict]
    methodology_note: str
