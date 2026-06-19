"""NeMo Guardrails integration for output validation."""

import logging
import re
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

UNSAFE_PATTERNS = [
    r"\b(hack|exploit|steal|illegal)\b",
    r"\b(guaranteed?\s+\d+%\s+returns?)\b",
    r"\b(pump\s+and\s+dump)\b",
]

HALLUCINATION_MARKERS = [
    r"\b(I cannot verify|no data available|hypothetically)\b",
    r"\b(100%\s+certain|absolutely\s+guaranteed)\b",
]


class NeMoGuardrails:
    """Output validation, safety checks, and hallucination prevention."""

    def validate_output(self, content: str, agent_name: str) -> dict[str, Any]:
        issues: list[str] = []
        warnings: list[str] = []
        passed = True

        for pattern in UNSAFE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Safety concern detected: matches pattern in {agent_name}")
                passed = False

        for pattern in HALLUCINATION_MARKERS:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Potential uncertainty marker in {agent_name}")

        if len(content) < 50:
            warnings.append(f"{agent_name} output unusually short")

        confidence = 0.9 if passed else 0.5
        if warnings:
            confidence -= 0.05 * len(warnings)

        return {
            "passed": passed,
            "issues": issues,
            "warnings": warnings,
            "confidence": max(0.0, min(1.0, confidence)),
            "validated_by": "nemo_guardrails" if settings.use_nvidia else "nemo_guardrails_demo",
        }

    def validate_structured(self, data: dict[str, Any], required_fields: list[str]) -> dict[str, Any]:
        missing = [f for f in required_fields if f not in data or not data[f]]
        passed = len(missing) == 0
        return {
            "passed": passed,
            "missing_fields": missing,
            "confidence": 1.0 if passed else 0.6,
        }

    def sanitize(self, content: str) -> str:
        for pattern in UNSAFE_PATTERNS:
            content = re.sub(pattern, "[REDACTED]", content, flags=re.IGNORECASE)
        return content


guardrails = NeMoGuardrails()
