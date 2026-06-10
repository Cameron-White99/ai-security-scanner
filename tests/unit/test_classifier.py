from core.classification.classifier import Classifier
from core.detection.rules.registry import RuleMatch
from core.detection.heuristics.analyzer import HeuristicResult
from core.detection.rules.patterns import RULES


def make_rule_match(confidence=0.9):
    return RuleMatch(rule=RULES[0], matched_text="ignore all previous instructions", confidence=confidence)


def make_heuristic_result(confidence=0.6):
    return HeuristicResult(
        triggered=True,
        attack_type="direct_injection",
        description="High instruction density",
        confidence=confidence,
        severity="MEDIUM",
    )


class TestClassifier:
    def setup_method(self):
        self.classifier = Classifier(llm_fallback_threshold=0.6)

    def test_no_detections_needs_llm(self):
        detections, needs_llm = self.classifier.classify([], [])
        assert detections == []
        assert needs_llm is True

    def test_high_confidence_no_llm_needed(self):
        _, needs_llm = self.classifier.classify([make_rule_match(confidence=0.95)], [])
        assert needs_llm is False

    def test_all_low_confidence_needs_llm(self):
        _, needs_llm = self.classifier.classify([make_rule_match(confidence=0.4)], [])
        assert needs_llm is True

    def test_one_high_confidence_skips_llm(self):
        matches = [make_rule_match(confidence=0.4), make_rule_match(confidence=0.9)]
        _, needs_llm = self.classifier.classify(matches, [])
        assert needs_llm is False

    def test_rule_and_heuristic_combined(self):
        detections, _ = self.classifier.classify(
            [make_rule_match(confidence=0.9)],
            [make_heuristic_result(confidence=0.6)],
        )
        assert len(detections) == 2
        assert any(d.detection_method == "rule" for d in detections)
        assert any(d.detection_method == "heuristic" for d in detections)

    def test_rule_detection_method(self):
        detections, _ = self.classifier.classify([make_rule_match()], [])
        assert detections[0].detection_method == "rule"

    def test_heuristic_detection_method(self):
        detections, _ = self.classifier.classify([], [make_heuristic_result(confidence=0.9)])
        assert detections[0].detection_method == "heuristic"

    def test_matched_pattern_truncated_at_200(self):
        long_match = RuleMatch(rule=RULES[0], matched_text="x" * 300, confidence=0.9)
        detections, _ = self.classifier.classify([long_match], [])
        assert len(detections[0].matched_pattern) == 200

    def test_heuristic_matched_pattern_is_none(self):
        detections, _ = self.classifier.classify([], [make_heuristic_result(confidence=0.9)])
        assert detections[0].matched_pattern is None
