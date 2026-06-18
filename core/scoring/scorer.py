"""
Risk scorer.
Aggregates detections into a single 0–100 risk score and risk level label.
"""

from dataclasses import dataclass
from core.classification.classifier import DetectionResult

SEVERITY_WEIGHTS = {
    "LOW": 20,
    "MEDIUM": 45,
    "HIGH": 72,
    "CRITICAL": 95,
}

RISK_LEVELS = [
    (80, "CRITICAL"),
    (55, "HIGH"),
    (30, "MEDIUM"),
    (-1, "LOW"),
]


@dataclass
class ScoreResult:
    score: float  # 0–100
    risk_level: str  # LOW / MEDIUM / HIGH / CRITICAL


class RiskScorer:
    def score(self, detections: list[DetectionResult]) -> ScoreResult:
        if not detections:
            return ScoreResult(score=0.0, risk_level="LOW")

        # Score is anchored to the strongest detection so a weak secondary
        # signal can't drag the overall score below what the worst threat warrants.
        individual_scores = [
            SEVERITY_WEIGHTS.get(d.severity, 20) * d.confidence for d in detections
        ]
        raw_score = max(individual_scores)

        # Each additional detection adds a diminishing bonus (capped at +15).
        if len(detections) > 1:
            secondary_bonus = min(sum(sorted(individual_scores)[:-1]) * 0.15, 15)
            raw_score = min(raw_score + secondary_bonus, 100)

        score = round(min(raw_score, 100), 2)
        risk_level = next(label for threshold, label in RISK_LEVELS if score > threshold)

        return ScoreResult(score=score, risk_level=risk_level)
