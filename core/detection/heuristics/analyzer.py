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
        r"\boutput\s+only\b",
        r"\bnever\s+(say|mention|reveal|output|disclose)\b",
        r"\balways\s+(say|respond|output|answer|reply)\b",
        r"\bfrom\s+now\s+on\b",
        r"\bstarting\s+(now|from\s+here)\b",
        r"\byour\s+(role|job|goal|purpose)\s+is\b",
        r"\bdo\s+not\s+follow\b",
        r"\bnew\s+instructions?\b",
        r"\bforget\s+(your|all\s+(previous|prior))\b",
        r"\boverride\s+(your|all|the|these|those|previous|prior)\b",
        r"\bsupersede\b",
        r"\bact\s+as\s+if\b",
        r"\bpretend\s+(that|you)\b",
    ]

    # Persona hijacking phrases (generic, without requiring specific adjectives)
    _PERSONA_PATTERNS = [
        r"\b(pretend|imagine)\s+(to\s+be|you\s+(are|were))\b",
        r"\byou\s+are\s+now\s+(a\s+|an\s+)?\w+",
        r"\bpose\s+as\b",
        r"\byour\s+new\s+(persona|identity|name)\s+is\b",
        r"\bsimulate\s+being\b",
        r"\btake\s+on\s+the\s+(role|persona|identity)\s+of\b",
        r"\bembody\s+(the\s+)?(role|character|persona)\s+of\b",
    ]

    # False-authority / social-engineering framing
    _SOCIAL_ENG_PATTERNS = [
        r"\bI\s+(am|'m)\s+(an?\s+)?(authorized|developer|admin|administrator|researcher|security\s+tester)\b",
        r"\bfor\s+(testing|debugging|research|development)\s+purposes?\b",
        r"\bI\s+have\s+(been\s+)?(granted\s+)?(permission|authorization|access)\s+to\b",
        r"\bthis\s+is\s+(an?\s+)?(authorized|official|legitimate)\s+(test|request|query|audit)\b",
        r"\bI('m|\s+am)\s+(allowed|permitted|authorized)\s+to\b",
        r"\bas\s+(the\s+)?(developer|admin|administrator|owner|creator)\b",
    ]

    def __init__(self):
        self._persona_compiled = [
            re.compile(p, re.IGNORECASE) for p in self._PERSONA_PATTERNS
        ]
        self._social_eng_compiled = [
            re.compile(p, re.IGNORECASE) for p in self._SOCIAL_ENG_PATTERNS
        ]

    def analyze(self, text: str) -> list[HeuristicResult]:
        results = []

        for check in (
            self._check_instruction_density,
            self._check_unusual_delimiters,
            self._check_encoding_obfuscation,
            self._check_persona_hijacking,
            self._check_social_engineering,
        ):
            r = check(text)
            if r.triggered:
                results.append(r)

        return results

    def _check_instruction_density(self, text: str) -> HeuristicResult:
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
        delimiter_patterns = [r"={3,}", r"-{3,}", r"\*{3,}", r"#{3,}", r"_{3,}"]
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

    def _check_persona_hijacking(self, text: str) -> HeuristicResult:
        """Catch generic persona/role substitution not covered by the jailbreak rule."""
        for compiled in self._persona_compiled:
            m = compiled.search(text)
            if m:
                return HeuristicResult(
                    triggered=True,
                    attack_type="jailbreak",
                    description=f"Persona hijacking detected — attempt to substitute model identity: '{m.group(0)}'",
                    confidence=0.60,
                    severity="MEDIUM",
                )
        return HeuristicResult(
            triggered=False, attack_type="", description="", confidence=0.0, severity="LOW"
        )

    def _check_social_engineering(self, text: str) -> HeuristicResult:
        """Catch false-authority framing used to lower the model's guard."""
        hits = []
        for compiled in self._social_eng_compiled:
            m = compiled.search(text)
            if m:
                hits.append(m.group(0))

        if hits:
            confidence = min(0.50 + 0.07 * len(hits), 0.75)
            return HeuristicResult(
                triggered=True,
                attack_type="direct_injection",
                description=f"Social engineering / false-authority framing detected: {hits}",
                confidence=confidence,
                severity="MEDIUM" if len(hits) > 1 else "LOW",
            )
        return HeuristicResult(
            triggered=False, attack_type="", description="", confidence=0.0, severity="LOW"
        )
