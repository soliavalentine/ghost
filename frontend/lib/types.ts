export interface GhostSignal {
  text: string;
  classification: "optional" | "load-bearing";
  signal_type: string;
  mechanism: string;
}

export interface GhostReport {
  detected_signals: GhostSignal[];
  recommendations: string[];
  bridge_line: string;
}

export interface VariantScore {
  variant_label: "actual" | "white_coded" | "black_coded";
  variant_name: string;
  name_coding: string;
  keyword_score: number;
  ats_compatibility_score: number;
  simulated_callback_score: number;
  proxy_signals_detected: string[];
}

export interface BiasGap {
  gap_score: number;
  gap_percentage: number;
  explanation: string;
  driving_signals: string[];
  research_grounding: string;
  system_accountability: string;
}

export interface AuditResponse {
  actual: VariantScore;
  white_coded: VariantScore;
  black_coded: VariantScore;
  bias_gap: BiasGap;
  ghost_report: GhostReport;
  overall_ats_score: number;
  ats_breakdown: Record<string, unknown>;
  llm_bias_analysis: Record<string, unknown>;
  methodology_note: string;
}
