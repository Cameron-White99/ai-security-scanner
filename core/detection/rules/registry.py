from dataclasses import dataclass
from core.detection.rules.patterns import RULES, Rule


@dataclass
class RuleMatch:
    rule: Rule
    matched_text: str
    confidence: float


class RuleRegistry:
    """Evaluates all rules against input text and returns matches."""

    def __init__(self):
        self._rules = RULES

    def evaluate(self, text: str) -> list[RuleMatch]:
        matches = []
        for rule in self._rules:
            m = rule.match(text)
            if m:
                matches.append(
                    RuleMatch(
                        rule=rule,
                        matched_text=m.group(0),
                        confidence=rule.confidence,
                    )
                )
        return matches
