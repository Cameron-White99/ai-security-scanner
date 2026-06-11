export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Detection {
  attack_type: string;
  description: string;
  confidence: number;
  severity: RiskLevel;
  detection_method: string;
  matched_pattern: string | null;
}

export interface Scan {
  id: string;
  risk_score: number;
  risk_level: RiskLevel;
  llm_fallback_used: boolean;
  source: string | null;
  detections: Detection[];
  created_at: string;
}

export interface TopRiskItem {
  id: string;
  risk_score: number;
  risk_level: RiskLevel;
  created_at: string;
}

export interface Report {
  id: string;
  from_date: string;
  to_date: string;
  total_scans: number;
  generated_at: string;
  risk_distribution: Record<string, number>;
  attack_type_breakdown: Record<string, number>;
  top_risks: TopRiskItem[];
  mitigations: Record<string, string>;
  summary: string;
}
