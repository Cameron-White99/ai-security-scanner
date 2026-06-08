"""
Detection engine — orchestrates the full pipeline:
  rules → heuristics → classifier → (optional LLM fallback) → scorer
"""
from dataclasses import dataclass
from core.detection.rules.registry import RuleRegistry
from core.detection.heuristics.analyzer import HeuristicAnalyzer
from core.classification.classifier import Classifier, DetectionResult
from core.classification.llm_fallback import LLMFallbackClassifier
from core.scoring.scorer import RiskScorer, ScoreResult
from config.settings import get_settings

settings = get_settings()


@dataclass
class ScanResult:
    detections: list[DetectionResult]
    score: ScoreResult
    llm_fallback_used: bool


class DetectionEngine:

    def __init__(self):
        self._rules = RuleRegistry()
        self._heuristics = HeuristicAnalyzer()
        self._classifier = Classifier(llm_fallback_threshold=settings.llm_fallback_threshold)
        self._llm = LLMFallbackClassifier()
        self._scorer = RiskScorer()

    async def scan(self, text: str) -> ScanResult:
        # Stage 1: rule matching
        rule_matches = self._rules.evaluate(text)

        # Stage 2: heuristic analysis
        heuristic_results = self._heuristics.analyze(text)

        # Stage 3: classify and decide on LLM fallback
        detections, needs_llm = self._classifier.classify(rule_matches, heuristic_results)

        llm_used = False

        # Stage 4: LLM fallback (only if warranted and API key configured)
        if needs_llm and settings.anthropic_api_key and len(text.strip()) > 50:
            llm_result = await self._llm.classify(text)
            if llm_result:
                detections.append(llm_result)
            llm_used = True

        # Stage 5: score
        score = self._scorer.score(detections)

        return ScanResult(
            detections=detections,
            score=score,
            llm_fallback_used=llm_used,
        )
