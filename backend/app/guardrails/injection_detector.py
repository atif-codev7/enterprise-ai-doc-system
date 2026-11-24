import re
from typing import List, Tuple
from app.models.schemas import GuardrailCheckResult
from app.config import settings

class PromptInjectionGuardrail:
    """
    Multi-layer prompt-injection guardrail engine.
    Detects instruction override attacks, delimiter manipulation,
    jailbreak attempts, privilege escalation, and credential theft vectors.
    """

    # Comprehensive heuristic patterns for prompt injection & jailbreak
    INJECTION_PATTERNS = [
        # Instruction Overrides
        (r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|directives|rules)\b", "INSTRUCTION_OVERRIDE"),
        (r"(?i)\bdisregard\s+(all\s+)?(previous|prior|above)\b", "DISREGARD_DIRECTIVES"),
        (r"(?i)\bforget\s+(everything|all)\s+you\s+(were|have\s+been)\s+told\b", "CONTEXT_PURGE"),
        
        # System & Delimiter Spoofing
        (r"(?i)<\s*(system|admin|developer|instruction)\s*>", "XML_SYSTEM_TAG_INJECTION"),
        (r"(?i)\[\s*(system|instruction|developer)\s*\]", "BRACKET_SYSTEM_TAG_INJECTION"),
        (r"(?i)```\s*(system|instruct)", "MARKDOWN_SYSTEM_INJECTION"),
        (r"(?i)(human|assistant|system):\s*", "ROLE_PLAY_DELIMITER_SPOOF"),

        # Jailbreak Personas & DAN Variants
        (r"(?i)\byou\s+are\s+now\s+(dan|an\s+unrestricted\s+ai|evil|jailbroken)\b", "JAILBREAK_PERSONA"),
        (r"(?i)\bdo\s+anything\s+now\b", "DAN_ATTACK"),
        (r"(?i)\bbypass\s+(all\s+)?(safety|ethical|content|security)\s+(filters|guidelines|policies)\b", "FILTER_BYPASS_ATTEMPT"),
        
        # Privilege Escalation & Hostile Exploitation
        (r"(?i)\b(act\s+as\s+root|sudo|superuser|elevate\s+privileges)\b", "PRIVILEGE_ESCALATION"),
        (r"(?i)\b(reveal|print|dump|output)\s+(your\s+)?(system\s+prompt|developer\s+prompt|initial\s+instructions|api\s*key|secret)\b", "CREDENTIAL_LEAK_PROBE"),
        (r"(?i)\b(drop\s+table|delete\s+from|truncate\s+table|;\s*drop\b)", "SQL_INJECTION_PROBE")
    ]

    def __init__(self, threshold: float = settings.GUARDRAIL_CONFIDENCE_THRESHOLD):
        self.threshold = threshold
        self._compiled_patterns = [
            (re.compile(pat), label) for pat, label in self.INJECTION_PATTERNS
        ]

    def scan(self, text: str) -> GuardrailCheckResult:
        """
        Scans input prompt against known adversarial injection signatures and suspicious syntax.
        """
        if not text or not text.strip():
            return GuardrailCheckResult(is_safe=True, risk_score=0.0, violated_rules=[])

        violated_rules: List[str] = []
        flagged_snippet: str = None
        accumulated_risk = 0.0

        for pattern, label in self._compiled_patterns:
            match = pattern.search(text)
            if match:
                violated_rules.append(label)
                if not flagged_snippet:
                    flagged_snippet = match.group(0)
                # Severe rules add high risk
                if label in ("INSTRUCTION_OVERRIDE", "JAILBREAK_PERSONA", "CREDENTIAL_LEAK_PROBE", "SQL_INJECTION_PROBE"):
                    accumulated_risk += 0.85
                else:
                    accumulated_risk += 0.50

        # Check for abnormal repetition or high control character density
        control_chars = len(re.findall(r"[\x00-\x1f\x7f-\x9f]", text))
        if control_chars > 3:
            violated_rules.append("SUSPICIOUS_CONTROL_CHARS")
            accumulated_risk += 0.3

        risk_score = round(min(1.0, accumulated_risk), 2)
        is_safe = (risk_score < self.threshold) and (len(violated_rules) == 0)

        return GuardrailCheckResult(
            is_safe=is_safe,
            risk_score=risk_score,
            violated_rules=violated_rules,
            sanitization_applied=not is_safe,
            flagged_snippet=flagged_snippet
        )

    def sanitize_output(self, text: str) -> str:
        """
        Scans output text to redact accidental leakage of secrets, internal tokens, or credentials.
        """
        # Redact OpenAI / Anthropic key patterns
        sanitized = re.sub(r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_API_KEY]", text)
        sanitized = re.sub(r"claude-[a-zA-Z0-9]{20,}", "[REDACTED_API_KEY]", sanitized)
        # Redact connection strings
        sanitized = re.sub(r"postgres://[^\s@]+@[^\s/]+/\w+", "[REDACTED_DATABASE_URL]", sanitized)
        return sanitized

guardrail_service = PromptInjectionGuardrail()
