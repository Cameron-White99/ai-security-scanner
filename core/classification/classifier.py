from collections import defaultdict
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
    detection_method: str  # rule / heuristic / llm / rule+heuristic
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
        detections: list[DetectionResult] = []

        for match in rule_matches:
            detections.append(
                DetectionResult(
                    attack_type=match.rule.attack_type,
                    description=match.rule.description,
                    confidence=match.confidence,
                    severity=match.rule.severity,
                    detection_method="rule",
                    matched_pattern=match.matched_text[:200],
                )
            )

        for result in heuristic_results:
            detections.append(
                DetectionResult(
                    attack_type=result.attack_type,
                    description=result.description,
                    confidence=result.confidence,
                    severity=result.severity,
                    detection_method="heuristic",
                    matched_pattern=None,
                )
            )

        detections = self._merge_detections(detections)
        needs_llm = self._needs_llm_fallback(detections)

        return detections, needs_llm

    def _merge_detections(self, detections: list[DetectionResult]) -> list[DetectionResult]:
        """
        When rule and heuristic both fire on the same attack_type, merge into one
        result and boost confidence — corroborating signals increase certainty.
        """
        groups: defaultdict[str, list[DetectionResult]] = defaultdict(list)
        for d in detections:
            groups[d.attack_type].append(d)

        merged: list[DetectionResult] = []
        for attack_type, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
                continue

            best = max(group, key=lambda d: d.confidence)
            # Each additional corroborating signal adds 0.05, capped at 0.15
            boost = min(0.05 * (len(group) - 1), 0.15)
            highest_severity = max(group, key=lambda d: SEVERITY_ORDER[d.severity]).severity
            methods = "+".join(sorted({d.detection_method for d in group}))

            merged.append(
                DetectionResult(
                    attack_type=attack_type,
                    description=best.description,
                    confidence=min(best.confidence + boost, 0.97),
                    severity=highest_severity,
                    detection_method=methods,
                    matched_pattern=best.matched_pattern,
                )
            )

        return merged

    def _needs_llm_fallback(self, detections: list[DetectionResult]) -> bool:
        if not detections:
            return True

        has_rule_match = any("rule" in d.detection_method for d in detections)
        max_confidence = max(d.confidence for d in detections)

        # Heuristic-only signals are less reliable — apply a stricter threshold
        # so borderline cases still get reviewed by the LLM.
        if not has_rule_match:
            return max_confidence < min(self.llm_fallback_threshold + 0.15, 0.85)

        return max_confidence < self.llm_fallback_threshold
