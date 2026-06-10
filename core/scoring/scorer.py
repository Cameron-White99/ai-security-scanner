"""
Risk scorer.
Aggregates detections into a single 0–100 risk score and risk level label.
"""
from dataclasses import dataclass
from core.classification.classifier import DetectionResult

SEVERITY_WEIGHTS = {
    "LOW": 15,
    "MEDIUM": 35,
    "HIGH": 65,
    "CRITICAL": 90,
}

RISK_LEVELS = [
    (80, "CRITICAL"),
    (55, "HIGH"),
    (30, "MEDIUM"),
    (-1, "LOW"),
]


@dataclass
class ScoreResult:
    score: float        # 0–100
    risk_level: str     # LOW / MEDIUM / HIGH / CRITICAL


class RiskScorer:

    def score(self, detections: list[DetectionResult]) -> ScoreResult:
        if not detections:
            return ScoreResult(score=0.0, risk_level="LOW")

        # Weighted average: higher-severity detections dominate
        total_weight = 0.0
        weighted_score = 0.0

        for d in detections:
            base = SEVERITY_WEIGHTS.get(d.severity, 15)
            adjusted = base * d.confidence
            weight = base  # weight by severity so CRITICAL pulls score up
            weighted_score += adjusted * weight
            total_weight += weight

        raw_score = weighted_score / total_weight if total_weight else 0.0

        # Bonus: multiple independent detections increase score
        if len(detections) > 1:
            raw_score = min(raw_score * (1 + 0.1 * (len(detections) - 1)), 100)

        score = round(min(raw_score, 100), 2)
        risk_level = next(label for threshold, label in RISK_LEVELS if score > threshold)

        return ScoreResult(score=score, risk_level=risk_level)
