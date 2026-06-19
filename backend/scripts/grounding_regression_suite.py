"""Grounding regression suite for production stabilization mandate."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.schemas import GenerateRequest
from app.orchestration.workflow import orchestrator
from app.services.evidence_utils import (
    detect_template_architecture,
    normalize_url,
)


def _collect_all_source_urls(obj: Any) -> list[str]:
    urls: list[str] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in ("source_url", "url") and isinstance(val, str) and val.startswith("http"):
                urls.append(val)
            else:
                urls.extend(_collect_all_source_urls(val))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(_collect_all_source_urls(item))
    return urls


def _fabricated_urls(payload: dict) -> list[str]:
    allowed = {
        normalize_url(entry["source_url"])
        for entry in payload.get("claim_lineage", [])
        if entry.get("source_url")
    }
    fabricated = []
    for url in _collect_all_source_urls(payload):
        normalized = normalize_url(url)
        if normalized and normalized not in allowed:
            fabricated.append(normalized)
    return fabricated

BENCHMARK_IDEAS = [
    "AI placement preparation platform for college students",
    "Helios Grid: AI-powered smart energy optimization platform",
    "Brain-computer cloud for collective intelligence and cognitive augmentation",
]


def _collect_competitor_names(blueprint: dict) -> list[str]:
    comp = blueprint.get("competitor_analysis", {}).get("content", {}).get("competitors", {})
    names: list[str] = []
    if isinstance(comp, dict):
        for entries in comp.values():
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and entry.get("name"):
                        names.append(entry["name"])
    return names


def _collect_verified_claims(blueprint: dict) -> list[dict]:
    validation = blueprint.get("validation", {}).get("content", {})
    report = validation.get("evidence_quality_report", {})
    return report.get("verified_claims", [])


async def run_suite() -> dict:
    results = []
    for idea in BENCHMARK_IDEAS:
        case = {"idea": idea, "checks": {}, "metrics": {}}
        try:
            blueprint = await orchestrator.generate(GenerateRequest(idea=idea))
            payload = blueprint.model_dump()

            diagnostics_path = os.path.join(os.path.dirname(__file__), "..", "audit_diagnostics.json")
            diagnostics = []
            if os.path.exists(diagnostics_path):
                with open(diagnostics_path, "r", encoding="utf-8") as handle:
                    diagnostics = json.load(handle)

            fallbacks = [d for d in diagnostics if d.get("execution_mode") == "fallback_demo"]
            json_failures = [d for d in diagnostics if d.get("json_parse_success") is False and d.get("execution_mode") == "nvidia_live"]
            case["metrics"]["agent_runs"] = len(diagnostics)
            case["metrics"]["fallback_count"] = len(fallbacks)
            case["metrics"]["json_parse_failures"] = len(json_failures)
            case["metrics"]["claim_lineage_count"] = len(payload.get("claim_lineage", []))

            fabricated_urls = _fabricated_urls(payload)

            ta_content = payload.get("technical_architecture", {}).get("content", {})
            template_hits = detect_template_architecture(ta_content)

            verified = _collect_verified_claims(payload)
            false_verifications = [
                c for c in verified
                if c.get("status") == "verified" and (
                    not c.get("sources") or c.get("source") in ("No Source", None, "")
                )
            ]

            competitors = _collect_competitor_names(payload)
            suspicious_competitors = [
                name for name in competitors
                if any(token in name.lower() for token in ["incumbent leader", "startup challenger", "fake", "mock"])
            ]

            case["checks"] = {
                "ten_agents_ran": len(diagnostics) == 10,
                "no_fallbacks": len(fallbacks) == 0,
                "no_json_parse_failures": len(json_failures) == 0,
                "no_template_architecture": len(template_hits) == 0,
                "no_false_verifications": len(false_verifications) == 0,
                "no_fabricated_urls": len(fabricated_urls) == 0,
                "no_suspicious_competitors": len(suspicious_competitors) == 0,
                "claim_lineage_present": case["metrics"]["claim_lineage_count"] > 0,
            }
            case["competitors"] = competitors
            case["fabricated_urls"] = fabricated_urls
            case["false_verifications"] = false_verifications
            case["template_hits"] = template_hits
            case["suspicious_competitors"] = suspicious_competitors
            case["status"] = "pass" if all(case["checks"].values()) else "fail"
        except Exception as exc:
            case["status"] = "error"
            case["error"] = str(exc)

        results.append(case)

    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "passed": sum(1 for r in results if r.get("status") == "pass"),
        "failed": sum(1 for r in results if r.get("status") == "fail"),
        "errors": sum(1 for r in results if r.get("status") == "error"),
        "cases": results,
    }

    out_path = os.path.join(os.path.dirname(__file__), "..", "grounding_regression_report.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    asyncio.run(run_suite())
