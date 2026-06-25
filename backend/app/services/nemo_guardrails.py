"""NeMo Guardrails integration for output validation."""

import json
import logging
import os
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

COMPLIANCE_PATTERNS = [
    r"\b(no kyc|zero kyc|kyc-free|anonymous lending|without kyc|without verification)\b",
    r"\b(lending (to|for) minors|loans (to|for) minors|micro-lending (to|for) minors|under-age micro-loans|minors with zero kyc|micro-lending app for minors)\b",
]


class NeMoGuardrails:
    """Output validation, safety checks, and hallucination prevention."""

    def _load_colang_examples(self) -> list[str]:
        """Parse disallowed.co for user example inputs."""
        examples = []
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            colang_path = os.path.join(current_dir, "disallowed.co")
            if os.path.exists(colang_path):
                with open(colang_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('"') and line.endswith('"'):
                            examples.append(line.strip('"'))
        except Exception as e:
            logger.warning("Failed to load Colang examples: %s", e)
        return examples

    async def validate_input(self, idea: str) -> dict[str, Any]:
        """Validate startup idea input for safety and compliance policies."""
        issues: list[str] = []
        passed = True

        # Check regex fallback patterns (always active for safety)
        for pattern in UNSAFE_PATTERNS:
            if re.search(pattern, idea, re.IGNORECASE):
                issues.append(f"Safety concern: matches unsafe pattern '{pattern}'")
                passed = False

        for pattern in COMPLIANCE_PATTERNS:
            if re.search(pattern, idea, re.IGNORECASE):
                issues.append("Compliance violation: input matches prohibited financial lending or compliance patterns")
                passed = False

        colang_examples = self._load_colang_examples()

        # If settings.use_nvidia is True and no regex issues yet, perform real NIM LLM safety verification
        if settings.use_nvidia and passed:
            try:
                from app.services.nvidia_nim import nim_service
                
                disallowed_text = "\n".join(f"- {ex}" for ex in colang_examples)
                system_prompt = (
                    "You are the Input Safety and Compliance Rail for Ignivox AI.\n"
                    "Your job is to analyze the user's proposed startup idea and determine if it violates safety or compliance policies.\n"
                    "We block ideas related to financial fraud, bypassing KYC, money laundering, lending to minors, hacking, or other illegal/non-compliant businesses.\n\n"
                    "Disallowed example ideas:\n"
                    f"{disallowed_text}\n\n"
                    "You MUST respond with a JSON object in this format:\n"
                    "{\n"
                    '  "safe": true/false,\n'
                    '  "reason": "explanation of safety or compliance violation"\n'
                    "}"
                )
                user_prompt = f"Analyze this startup idea: '{idea}'"
                
                response_str = await nim_service.complete(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.0,
                    max_tokens=256,
                    json_mode=True,
                )
                
                res = json.loads(response_str)
                if not res.get("safe", True):
                    issues.append(f"Compliance violation: {res.get('reason', 'Policy violation detected')}")
                    passed = False
            except Exception as e:
                logger.warning("NIM safety check failed, fell back to local guardrails: %s", e)

        # Local mock logic if not using nvidia but matches Colang examples semantically
        if not settings.use_nvidia and passed:
            idea_lower = idea.lower()
            for ex in colang_examples:
                if ex.lower() in idea_lower or any(word in idea_lower for word in ["kyc", "minors", "micro-lending", "anonymous"]):
                    # Simple heuristic match for compliance trap in demo mode
                    if "minor" in idea_lower and ("kyc" in idea_lower or "anonymous" in idea_lower or "lending" in idea_lower):
                        issues.append("Compliance violation: prohibited micro-lending concept for minors without KYC")
                        passed = False
                        break

        return {
            "passed": passed,
            "issues": issues,
            "validated_by": "nemo_guardrails" if settings.use_nvidia else "nemo_guardrails_demo",
        }

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

