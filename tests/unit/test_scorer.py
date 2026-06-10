from core.scoring.scorer import RiskScorer
from core.classification.classifier import DetectionResult


def make_detection(severity="HIGH", confidence=0.9):
    return DetectionResult(
        attack_type="direct_injection",
        description="test detection",
        confidence=confidence,
        severity=severity,
        detection_method="rule",
    )


class TestRiskScorer:
    def setup_method(self):
        self.scorer = RiskScorer()

    def test_empty_detections_returns_zero(self):
        result = self.scorer.score([])
        assert result.score == 0.0
        assert result.risk_level == "LOW"

    def test_single_critical_full_confidence(self):
        result = self.scorer.score([make_detection("CRITICAL", 1.0)])
        assert result.score > 80
        assert result.risk_level == "CRITICAL"

    def test_single_high_severity(self):
        result = self.scorer.score([make_detection("HIGH", 0.9)])
        assert result.risk_level in ("HIGH", "CRITICAL")

    def test_single_low_severity(self):
        result = self.scorer.score([make_detection("LOW", 0.5)])
        assert result.risk_level in ("LOW", "MEDIUM")

    def test_multiple_detections_score_higher_than_single(self):
        single = self.scorer.score([make_detection("HIGH", 0.9)])
        multiple = self.scorer.score([make_detection("HIGH", 0.9), make_detection("HIGH", 0.9)])
        assert multiple.score > single.score

    def test_score_clamped_at_100(self):
        detections = [make_detection("CRITICAL", 1.0)] * 10
        result = self.scorer.score(detections)
        assert result.score <= 100.0

    def test_score_is_rounded_to_two_decimal_places(self):
        result = self.scorer.score([make_detection("MEDIUM", 0.7)])
        assert result.score == round(result.score, 2)

    def test_medium_severity_below_high_threshold(self):
        result = self.scorer.score([make_detection("MEDIUM", 1.0)])
        assert result.risk_level in ("MEDIUM", "HIGH")

    def test_zero_confidence_yields_zero_score(self):
        result = self.scorer.score([make_detection("CRITICAL", 0.0)])
        assert result.score == 0.0
        assert result.risk_level == "LOW"
