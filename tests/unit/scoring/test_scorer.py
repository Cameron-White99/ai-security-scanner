import pytest
from core.scoring.scorer import RiskScorer
from core.classification.classifier import DetectionResult


@pytest.fixture
def scorer():
    return RiskScorer()


def test_no_detections_returns_zero(scorer):
    result = scorer.score([])
    assert result.score == 0.0
    assert result.risk_level == "LOW"


def test_critical_detection_high_score(scorer):
    detections = [DetectionResult(
        attack_type="indirect_injection",
        description="Test",
        confidence=0.95,
        severity="CRITICAL",
        detection_method="rule",
    )]
    result = scorer.score(detections)
    assert result.score >= 80
    assert result.risk_level == "CRITICAL"


def test_low_severity_low_score(scorer):
    detections = [DetectionResult(
        attack_type="direct_injection",
        description="Test",
        confidence=0.5,
        severity="LOW",
        detection_method="heuristic",
    )]
    result = scorer.score(detections)
    assert result.score < 30


def test_multiple_detections_increase_score(scorer):
    single = [DetectionResult(
        attack_type="direct_injection", description="Test",
        confidence=0.8, severity="MEDIUM", detection_method="rule",
    )]
    multiple = single * 3
    single_result = scorer.score(single)
    multi_result = scorer.score(multiple)
    assert multi_result.score > single_result.score
