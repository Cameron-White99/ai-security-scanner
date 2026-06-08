from dataclasses import dataclass
from core.detection.rules.registry import RuleMatch
from core.detection.heuristics.analyzer import HeuristicResult


SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


@dataclass
class DetectionResult:
    attack_type: str
    description: str
    confidence: float
    severity: str
    detection_method: str  # rule / heuristic / llm
    matched_pattern: str | None = None


class Classifier:
    """
    Aggregates rule matches and heuristic results into structured DetectionResults.
    Also determines whether LLM fallback is needed.
    """

    def __init__(self, llm_fallback_threshold: float = 0.6):
        self.llm_fallback_threshold = llm_fallback_threshold

    def classify(
        self,
        rule_matches: list[RuleMatch],
        heuristic_results: list[HeuristicResult],
    ) -> tuple[list[DetectionResult], bool]:
        """
        Returns:
            detections: list of DetectionResult
            needs_llm_fallback: True if confidence is low and LLM review is warranted
        """
        detections: list[DetectionResult] = []

        for match in rule_matches:
            detections.append(DetectionResult(
                attack_type=match.rule.attack_type,
                description=match.rule.description,
                confidence=match.confidence,
                severity=match.rule.severity,
                detection_method="rule",
                matched_pattern=match.matched_text[:200],
            ))

        for result in heuristic_results:
            detections.append(DetectionResult(
                attack_type=result.attack_type,
                description=result.description,
                confidence=result.confidence,
                severity=result.severity,
                detection_method="heuristic",
                matched_pattern=None,
            ))

        needs_llm = False
        if not detections:
            needs_llm = True
        elif all(d.confidence < self.llm_fallback_threshold for d in detections):
            needs_llm = True

        return detections, needs_llm
