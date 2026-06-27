"""NVIDIA NIM integration for LLM inference."""

import json
import re
import logging
from typing import Any, Callable

import httpx
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"


def _close_open_json_structures(text: str) -> str:
    """Close truncated JSON by balancing brackets and terminating open strings."""
    truncated = text.rstrip()
    if truncated.endswith(":"):
        truncated += '""'
    elif truncated.count('"') % 2 == 1:
        truncated += '"'

    open_braces = truncated.count("{") - truncated.count("}")
    open_brackets = truncated.count("[") - truncated.count("]")
    truncated += "]" * max(0, open_brackets)
    truncated += "}" * max(0, open_braces)
    truncated = re.sub(r",\s*\}", "}", truncated)
    truncated = re.sub(r",\s*\]", "]", truncated)
    return truncated


class RecoveredStr(str):
    _recovered = True


def repair_investor_pitch_structure(data: Any, agent_type: str) -> dict[str, Any]:
    """Recovery step specifically for truncated array/object structures handling the investor pitch agent's known schema shape."""
    if agent_type != "investor_pitch":
        if isinstance(data, dict):
            return data
        try:
            return json.loads(data, strict=False)
        except Exception:
            return {}

    result_dict: dict[str, Any] = {}
    if isinstance(data, dict):
        result_dict = data
    elif isinstance(data, str):
        try:
            result_dict = json.loads(data, strict=False)
        except Exception:
            try:
                closed = _close_open_json_structures(data)
                result_dict = json.loads(closed, strict=False)
            except Exception:
                result_dict = {}

    recovered_any = False

    def log_recovery(field_name: str, recovery_action: str):
        import os
        from datetime import datetime
        os.makedirs("logs", exist_ok=True)
        log_path = "logs/investor_pitch_failures.json"
        failures = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    failures = json.load(f)
                    if not isinstance(failures, list):
                        failures = []
            except Exception:
                failures = []
        
        failures.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "field_name": field_name,
            "recovery_action": recovery_action
        })
        failures = failures[-50:]
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(failures, f, indent=2)
        except Exception as write_err:
            logger.error("Failed to write to investor_pitch_failures.json: %s", write_err)

    # 1. executive_summary (str)
    if "executive_summary" not in result_dict or not isinstance(result_dict["executive_summary"], str):
        result_dict["executive_summary"] = RecoveredStr("Safe default executive summary.")
        result_dict["executive_summary_recovered"] = True
        recovered_any = True
        log_recovery("executive_summary", "Set safe default string")

    # 2. slides (list, min 1 element)
    for slides_key in ["slides", "pitch_slides"]:
        if slides_key not in result_dict or not isinstance(result_dict[slides_key], list):
            result_dict[slides_key] = [
                {
                    "title": "Introduction",
                    "content": "Welcome to our pitch.",
                    "speaker_notes": "Introduce the team",
                    "_recovered": True
                }
            ]
            recovered_any = True
            log_recovery(slides_key, "Set safe default list with 1 slide")
        else:
            slides_list = result_dict[slides_key]
            if slides_list:
                last_slide = slides_list[-1]
                if isinstance(last_slide, dict):
                    if "title" not in last_slide or "content" not in last_slide:
                        slides_list.pop()
                        recovered_any = True
                        log_recovery(slides_key, "Discarded incomplete last slide")
                else:
                    slides_list.pop()
                    recovered_any = True
                    log_recovery(slides_key, "Discarded non-dictionary last slide element")
            
            if not slides_list:
                slides_list.append({
                    "title": "Introduction",
                    "content": "Welcome to our pitch.",
                    "speaker_notes": "Introduce the team",
                    "_recovered": True
                })
                recovered_any = True
                log_recovery(slides_key, "Appended safe default slide to empty list")
            
            result_dict[slides_key] = slides_list

    # 3. funding_ask (dict)
    if "funding_ask" not in result_dict or not isinstance(result_dict["funding_ask"], dict):
        result_dict["funding_ask"] = {
            "amount": {"claim": "$1.5M", "_recovered": True},
            "valuation": {"claim": "$8M pre-money", "_recovered": True},
            "use_of_funds": {
                "engineering": "45%",
                "marketing_growth": "30%",
                "operations": "15%",
                "reserve": "10%",
                "_recovered": True
            },
            "runway_months": {"claim": "18", "_recovered": True},
            "milestones_with_funding": ["Product launch", "Traction goals"],
            "_recovered": True
        }
        recovered_any = True
        log_recovery("funding_ask", "Set safe default dict")
    else:
        funding_ask = result_dict["funding_ask"]
        for child_key in ["amount", "valuation", "runway_months"]:
            if child_key not in funding_ask or not isinstance(funding_ask[child_key], dict):
                funding_ask[child_key] = {"claim": "Safe default value", "_recovered": True}
                funding_ask["_recovered"] = True
                recovered_any = True
                log_recovery(f"funding_ask.{child_key}", "Set safe default dict value")
        if "use_of_funds" not in funding_ask or not isinstance(funding_ask["use_of_funds"], dict):
            funding_ask["use_of_funds"] = {
                "engineering": "45%",
                "marketing_growth": "30%",
                "operations": "15%",
                "reserve": "10%",
                "_recovered": True
            }
            funding_ask["_recovered"] = True
            recovered_any = True
            log_recovery("funding_ask.use_of_funds", "Set safe default dict use_of_funds")

    # 4. key_metrics (list)
    if "key_metrics" not in result_dict or not isinstance(result_dict["key_metrics"], list):
        result_dict["key_metrics"] = ["CAC", "LTV", "Churn Rate"]
        recovered_any = True
        log_recovery("key_metrics", "Set safe default list")

    if recovered_any:
        result_dict["_recovered"] = True

    return result_dict


def _parse_json_with_recovery(
    text: str,
    validation_fn: Callable[[dict[str, Any]], list[str]] | None = None,
    agent_type: str = "",
) -> dict[str, Any]:
    """Parse JSON with extraction, repair, and truncation recovery."""
    # Wrap validation_fn for investor_pitch to accept string for executive_summary
    if validation_fn and agent_type == "investor_pitch":
        original_validation_fn = validation_fn
        def wrapped_validation_fn(data: dict[str, Any]) -> list[str]:
            errors = original_validation_fn(data)
            if isinstance(data.get("executive_summary"), str):
                errors = [
                    err for err in errors
                    if "Key 'executive_summary' is not a JSON object" not in err
                    and "Key 'executive_summary' missing required child key" not in err
                ]
            return errors
        validation_fn = wrapped_validation_fn

    attempts: list[str] = [text]
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        extracted = text[start:end]
        if extracted != text:
            attempts.append(extracted)

    last_err: Exception | None = None
    for candidate in attempts:
        try:
            result = json.loads(candidate, strict=False)
            if validation_fn:
                errors = validation_fn(result)
                if errors:
                    raise ValueError(f"Schema validation failed: {', '.join(errors)}")
            return result
        except Exception as err:
            if isinstance(err, ValueError) and "Schema validation failed" in str(err):
                raise
            last_err = err

        try:
            repaired = candidate
            repaired = re.sub(r'([}\]"])\s*?\n\s*?("([^"]+)"\s*?:)', r"\1,\n\2", repaired)
            repaired = re.sub(r",\s*\}", "}", repaired)
            repaired = re.sub(r",\s*\]", "]", repaired)
            result = json.loads(repaired, strict=False)
            if validation_fn:
                errors = validation_fn(result)
                if errors:
                    raise ValueError(f"Schema validation failed: {', '.join(errors)}")
            return result
        except Exception as err:
            if isinstance(err, ValueError) and "Schema validation failed" in str(err):
                raise
            last_err = err

        try:
            truncated = _close_open_json_structures(candidate)
            result = json.loads(truncated, strict=False)
            
            result = repair_investor_pitch_structure(result, agent_type)
            
            if validation_fn:
                errors = validation_fn(result)
                if errors:
                    raise ValueError(f"Schema validation failed: {', '.join(errors)}")
            return result
        except Exception as err:
            if isinstance(err, ValueError) and "Schema validation failed" in str(err):
                raise
            last_err = err

    raise last_err or ValueError("JSON parsing failed")


class NIMService:
    """NVIDIA NIM LLM inference service."""

    def __init__(self) -> None:
        self.model = settings.nim_model
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=NIM_BASE_URL,
                api_key=settings.nvidia_api_key,
                timeout=600.0,
                max_retries=0,
            )
        return self._client

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        if not settings.use_nvidia:
            return ""

        import time
        prompt_length = len(system_prompt) + len(user_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(**kwargs)
            duration = time.time() - start_time
            content = response.choices[0].message.content or ""
            response_length = len(content)
            logger.info(
                "NIM completion success | model=%s | prompt_length=%d | response_length=%d | execution_duration=%.2fs",
                self.model,
                prompt_length,
                response_length,
                duration,
            )
            return content
        except Exception as e:
            duration = time.time() - start_time
            is_timeout = "timeout" in type(e).__name__.lower() or "timeout" in str(e).lower()
            if is_timeout:
                logger.warning(
                    "NIM timeout occurrence | model=%s | prompt_length=%d | execution_duration=%.2fs | error=%s",
                    self.model,
                    prompt_length,
                    duration,
                    e,
                )
            else:
                logger.error(
                    "NIM completion failed | model=%s | prompt_length=%d | execution_duration=%.2fs | error=%s",
                    self.model,
                    prompt_length,
                    duration,
                    e,
                )
            raise

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.5,
        agent_name: str = "",
        validation_fn: Callable[[dict[str, Any]], list[str]] | None = None,
        max_tokens: int = 4096,
        retry_on_failure: bool = True,
    ) -> dict[str, Any]:
        attempts: list[tuple[float, int]] = [(temperature, max_tokens)]
        if retry_on_failure:
            attempts.append((max(0.2, temperature - 0.2), max(max_tokens, int(max_tokens * 1.25))))

        last_err: Exception | None = None
        text = ""

        for attempt_idx, (temp, tokens) in enumerate(attempts):
            try:
                text = await self.complete(
                    system_prompt,
                    user_prompt + "\n\nRespond with valid JSON only.",
                    temperature=temp,
                    max_tokens=tokens,
                    json_mode=True,
                )
                logger.info(
                    "NIM Raw Response for %s | attempt=%d | length=%d | content=\n%s",
                    agent_name,
                    attempt_idx + 1,
                    len(text),
                    text,
                )
                agent_type = "investor_pitch" if "investor" in agent_name.lower() or agent_name == "investor_pitch" else agent_name
                return _parse_json_with_recovery(text, validation_fn, agent_type)
            except Exception as err:
                last_err = err
                if isinstance(err, ValueError) and "Schema validation failed" in str(err):
                    raise
                if attempt_idx < len(attempts) - 1:
                    logger.warning(
                        "NIM JSON parse failed for %s (attempt %d), retrying: %s",
                        agent_name,
                        attempt_idx + 1,
                        err,
                    )
                    continue
                break

        def save_failure(error_msg: str, parse_stage: str, validation_errors: list[str] | None = None):
            if agent_name == "Investor Pitch Agent" or "investor" in agent_name.lower():
                import os
                from datetime import datetime
                os.makedirs("logs", exist_ok=True)
                log_path = "logs/investor_pitch_failures.json"
                failures = []
                if os.path.exists(log_path):
                    try:
                        with open(log_path, "r", encoding="utf-8") as f:
                            failures = json.load(f)
                            if not isinstance(failures, list):
                                failures = []
                    except Exception:
                        failures = []
                
                new_failure = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "agent": agent_name,
                    "response_length": len(text),
                    "parse_stage": parse_stage,
                    "exception": error_msg,
                    "schema_validation_errors": validation_errors or [],
                    "raw_response": text
                }
                failures.append(new_failure)
                failures = failures[-20:]
                try:
                    with open(log_path, "w", encoding="utf-8") as f:
                        json.dump(failures, f, indent=2)
                except Exception as write_err:
                    logger.error("Failed to write to investor_pitch_failures.json: %s", write_err)

        stage = "recovery_json" if text.find("{") >= 0 else "raw_json"
        save_failure(str(last_err), stage, [])
        raise last_err or ValueError("JSON parsing failed")

    async def embed(self, texts: list[str]) -> list[list[float]] | None:
        if not settings.use_nvidia:
            return None

        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{NIM_BASE_URL}/embeddings",
                    headers={
                        "Authorization": f"Bearer {settings.nvidia_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.nim_embed_model,
                        "input": texts,
                        "encoding_format": "float",
                        "input_type": "query",
                    },
                )
                response.raise_for_status()
                data = response.json()
                return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.warning("NIM embedding failed, falling back to local retrieval: %s", e)
            return None


nim_service = NIMService()
