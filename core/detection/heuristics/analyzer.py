"""
Heuristic analysis layer.
Looks for structural anomalies that rules may miss —
unusual instruction density, delimiter abuse, suspicious length patterns, etc.
Returns a confidence score and description when an anomaly is detected.
"""

import re
from dataclasses import dataclass


@dataclass
class HeuristicResult:
    triggered: bool
    attack_type: str
    description: str
    confidence: float
    severity: str


class HeuristicAnalyzer:
    # Instruction-like keywords that inflate suspicion score
    INSTRUCTION_KEYWORDS = [
        r"\bignore\b",
        r"\bdisregard\b",
        r"\binstead\b",
        r"\bnow\s+do\b",
        r"\byour\s+task\s+is\b",
        r"\byou\s+must\b",
        r"\byou\s+will\b",
        r"\brespond\s+only\b",
        r"\bonly\s+respond\b",
        r"\bdo\s+not\s+(say|tell|mention|reveal)\b",
    ]

    def analyze(self, text: str) -> list[HeuristicResult]:
        results = []

        r = self._check_instruction_density(text)
        if r.triggered:
            results.append(r)

        r = self._check_unusual_delimiters(text)
        if r.triggered:
            results.append(r)

        r = self._check_encoding_obfuscation(text)
        if r.triggered:
            results.append(r)

        return results

    def _check_instruction_density(self, text: str) -> HeuristicResult:
        """Flag unusually high density of instruction-like language."""
        word_count = max(len(text.split()), 1)
        keyword_hits = sum(
            len(re.findall(kw, text, re.IGNORECASE)) for kw in self.INSTRUCTION_KEYWORDS
        )
        density = keyword_hits / word_count

        if density > 0.08:
            confidence = min(0.5 + density * 3, 0.85)
            return HeuristicResult(
                triggered=True,
                attack_type="direct_injection",
                description=f"Unusually high instruction keyword density ({keyword_hits} hits in {word_count} words)",
                confidence=confidence,
                severity="MEDIUM",
            )
        return HeuristicResult(
            triggered=False, attack_type="", description="", confidence=0.0, severity="LOW"
        )

    def _check_unusual_delimiters(self, text: str) -> HeuristicResult:
        """Flag inputs containing unusual structural delimiters."""
        delimiter_patterns = [
            r"={3,}",
            r"-{3,}",
            r"\*{3,}",
            r"#{3,}",
            r"_{3,}",
        ]
        hits = sum(len(re.findall(p, text)) for p in delimiter_patterns)

        if hits >= 3:
            return HeuristicResult(
                triggered=True,
                attack_type="direct_injection",
                description=f"Multiple structural delimiters detected ({hits} occurrences) — possible context boundary manipulation",
                confidence=0.6,
                severity="LOW",
            )
        return HeuristicResult(
            triggered=False, attack_type="", description="", confidence=0.0, severity="LOW"
        )

    def _check_encoding_obfuscation(self, text: str) -> HeuristicResult:
        """Detect base64 blobs or heavy unicode that may hide injections."""
        b64_pattern = re.findall(r"[A-Za-z0-9+/]{40,}={0,2}", text)
        unicode_escapes = re.findall(r"\\u[0-9a-fA-F]{4}", text)

        if len(b64_pattern) > 0 or len(unicode_escapes) > 5:
            return HeuristicResult(
                triggered=True,
                attack_type="obfuscation",
                description="Potential encoding obfuscation detected (base64 or unicode escapes)",
                confidence=0.65,
                severity="MEDIUM",
            )
        return HeuristicResult(
            triggered=False, attack_type="", description="", confidence=0.0, severity="LOW"
        )
