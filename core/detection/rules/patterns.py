"""
Rule-based prompt injection patterns.
Each rule defines: id, attack_type, severity, description, and a list of regex patterns.
Rules are evaluated in order; first match wins for that rule.
"""
import re
from dataclasses import dataclass, field


@dataclass
class Rule:
    id: str
    attack_type: str
    severity: str  # LOW / MEDIUM / HIGH / CRITICAL
    description: str
    patterns: list[str]
    confidence: float = 0.9  # default confidence when rule fires

    def __post_init__(self):
        self._compiled = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in self.patterns]

    def match(self, text: str) -> re.Match | None:
        for compiled in self._compiled:
            m = compiled.search(text)
            if m:
                return m
        return None


RULES: list[Rule] = [
    Rule(
        id="role_override",
        attack_type="direct_injection",
        severity="HIGH",
        description="Attempt to override the model's role or system instructions",
        patterns=[
            r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|directives?|context)",
            r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|directives?)",
            r"forget\s+(everything|all)\s+(you.ve\s+been|i.ve\s+told|above)",
            r"you\s+are\s+now\s+(a\s+)?(different|new|another|unrestricted)",
            r"(act|behave|pretend|roleplay)\s+as\s+(if\s+you\s+(are|were)\s+)?(an?\s+)?(different|unrestricted|evil|jailbroken|unfiltered)",
            r"your\s+(new\s+)?(role|persona|identity|instructions?)\s+(is|are)\s+to",
            r"from\s+now\s+on\s+(you\s+are|act\s+as|respond\s+as)",
        ],
        confidence=0.95,
    ),
    Rule(
        id="system_prompt_leak",
        attack_type="data_exfiltration",
        severity="HIGH",
        description="Attempt to extract the system prompt or internal instructions",
        patterns=[
            r"(print|output|reveal|show|display|repeat|tell\s+me|what\s+is)\s+(your\s+)?(system\s+prompt|initial\s+instructions?|base\s+prompt|original\s+prompt)",
            r"what\s+(were\s+you|are\s+you)\s+(told|instructed|prompted|asked)\s+to",
            r"(summarize|describe|explain)\s+your\s+(system\s+)?instructions?",
        ],
        confidence=0.9,
    ),
    Rule(
        id="delimiter_injection",
        attack_type="direct_injection",
        severity="MEDIUM",
        description="Use of delimiters to break out of context boundaries",
        patterns=[
            r"(###|---|\*\*\*|===)\s*(system|user|assistant|human|ai|instruction)",
            r"<\s*(system|instruction|prompt|context)\s*>",
            r"\[INST\]|\[\/INST\]|<\|im_start\|>|<\|im_end\|>",
            r"```\s*(system|instruction)",
        ],
        confidence=0.85,
    ),
    Rule(
        id="jailbreak_attempt",
        attack_type="jailbreak",
        severity="HIGH",
        description="Known jailbreak patterns (DAN, developer mode, etc.)",
        patterns=[
            r"\bDAN\b.*mode",
            r"developer\s+mode\s+(enabled|on|activated)",
            r"jailbreak(ed)?",
            r"do\s+anything\s+now",
            r"without\s+(any\s+)?(restrictions?|limitations?|filters?|guidelines?|ethical)",
            r"(bypass|circumvent|override|ignore)\s+(your\s+)?(safety|ethical|content|policy|restrictions?|guidelines?|filters?)",
        ],
        confidence=0.95,
    ),
    Rule(
        id="indirect_injection",
        attack_type="indirect_injection",
        severity="CRITICAL",
        description="Instructions embedded in external content intended to hijack agent behaviour",
        patterns=[
            r"(this\s+document|the\s+following|note\s+to\s+(ai|assistant|llm|model))\s*:\s*(ignore|disregard|instead)",
            r"<\s*hidden\s*>.*<\s*/\s*hidden\s*>",
            r"\[.*hidden\s+instruction.*\]",
            r"note\s+to\s+(the\s+)?(ai|assistant|model|llm)\s*:",
        ],
        confidence=0.9,
    ),
    Rule(
        id="prompt_leakage_probe",
        attack_type="data_exfiltration",
        severity="MEDIUM",
        description="Probing for sensitive data or context window contents",
        patterns=[
            r"(what|show\s+me|tell\s+me)\s+(is\s+in\s+)?(your\s+)?(context|memory|conversation\s+history|previous\s+messages?)",
            r"(repeat|output|print)\s+(everything|all)\s+(above|before|in\s+your\s+context)",
        ],
        confidence=0.8,
    ),
]
