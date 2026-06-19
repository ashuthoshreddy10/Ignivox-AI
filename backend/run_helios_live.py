"""
Run Helios Grid with NVIDIA Live Mode enabled.
Captures per-agent diagnostics and produces a structured live run report.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config import settings
from app.models.schemas import GenerateRequest
from app.orchestration.workflow import orchestrator

HELIOS_IDEA = "Helios Grid: AI-powered smart energy optimization platform"


async def main() -> None:
    print("=" * 70)
    print("HELIOS GRID — NVIDIA LIVE RUN")
    print(f"Idea : {HELIOS_IDEA}")
    print(f"use_nvidia : {settings.use_nvidia}")
    print(f"demo_mode  : {settings.demo_mode}")
    print(f"api_key    : {settings.masked_api_key}")
    print("=" * 70)

    if not settings.use_nvidia:
        print("\n[ERROR] settings.use_nvidia is False. Cannot proceed with live run.")
        print(f"  demo_mode = {settings.demo_mode}")
        print(f"  nvidia_api_key set = {bool(settings.nvidia_api_key)}")
        sys.exit(1)

    # Clear audit file before run
    audit_file = os.path.join(os.path.dirname(__file__), "audit_diagnostics.json")
    if os.path.exists(audit_file):
        os.remove(audit_file)
        print("[INFO] Cleared audit_diagnostics.json for fresh run.\n")

    run_start = time.time()
    try:
        blueprint = await orchestrator.generate(GenerateRequest(idea=HELIOS_IDEA))
        run_duration = time.time() - run_start
        print(f"\n[OK] Blueprint generated in {run_duration:.1f}s")
    except Exception as e:
        run_duration = time.time() - run_start
        print(f"\n[ERROR] Pipeline failed after {run_duration:.1f}s: {e}")
        blueprint = None

    # Load the written audit diagnostics
    diagnostics = []
    if os.path.exists(audit_file):
        with open(audit_file, "r", encoding="utf-8") as f:
            diagnostics = json.load(f)

    # Separate agent entries from retrieval_audit entries
    agent_entries = [d for d in diagnostics if "agent" in d]
    retrieval_entries = [d for d in diagnostics if "retrieval_audit" in d]

    # Build per-agent report table
    print("\n" + "=" * 70)
    print("PER-AGENT EXECUTION REPORT")
    print("=" * 70)

    report_agents = []
    for entry in agent_entries:
        row = {
            "agent": entry.get("agent"),
            "execution_mode": entry.get("execution_mode"),
            "nvidia_request_sent": entry.get("nvidia_request_sent"),
            "nvidia_response_received": entry.get("nvidia_response_received"),
            "fallback_reason": entry.get("fallback_reason"),
            "exception": entry.get("exception", ""),
            "response_length_chars": entry.get("response_length", 0),
            "json_parse_success": entry.get("json_parse_success"),
            "schema_validation_success": entry.get("schema_validation_success"),
            "prompt_length_before": entry.get("prompt_length_before"),
            "prompt_length_after": entry.get("prompt_length_after"),
            "compression_ratio": entry.get("compression_ratio"),
            "execution_time_after": entry.get("execution_time_after"),
        }
        report_agents.append(row)

        print(f"\n  Agent: {row['agent']}")
        print(f"    execution_mode          : {row['execution_mode']}")
        print(f"    nvidia_request_sent     : {row['nvidia_request_sent']}")
        print(f"    nvidia_response_received: {row['nvidia_response_received']}")
        print(f"    json_parse_success      : {row['json_parse_success']}")
        print(f"    schema_validation       : {row['schema_validation_success']}")
        print(f"    response_length (chars) : {row['response_length_chars']}")
        print(f"    prompt_length_before    : {row['prompt_length_before']}")
        print(f"    prompt_length_after     : {row['prompt_length_after']}")
        print(f"    compression_ratio       : {row['compression_ratio']}")
        print(f"    execution_time          : {row['execution_time_after']}")
        if row["fallback_reason"] and row["fallback_reason"] not in ("none", None):
            print(f"    fallback_reason         : {row['fallback_reason']}")
        if row["exception"]:
            print(f"    exception               : {row['exception']}")

    # Retrieval audit summary
    print("\n" + "=" * 70)
    print("RAG RETRIEVAL AUDIT SUMMARY")
    print("=" * 70)
    for ra in retrieval_entries:
        r = ra["retrieval_audit"]
        print(f"  total_docs_retrieved : {r.get('total_docs_retrieved')}")
        print(f"  docs_filtered        : {r.get('docs_filtered')}")
        print(f"  docs_used            : {r.get('docs_used')}")
        print(f"  category_distribution: {r.get('category_distribution')}")

    # Save structured report JSON
    report = {
        "run_timestamp": datetime.utcnow().isoformat() + "Z",
        "idea": HELIOS_IDEA,
        "settings": {
            "use_nvidia": settings.use_nvidia,
            "demo_mode": settings.demo_mode,
            "api_key_masked": settings.masked_api_key,
            "nim_model": settings.nim_model,
        },
        "total_run_duration_seconds": round(run_duration, 2),
        "agents": report_agents,
        "retrieval_audits": [ra["retrieval_audit"] for ra in retrieval_entries],
        "blueprint_score": blueprint.score.overall if blueprint and blueprint.score else None,
    }

    # Also capture edtech contamination check on live output
    contamination = []
    EDTECH_PHRASES = [
        "placement co-pilot", "college partnerships", "college ambassadors",
        "adaptive learning", "mock interviews", "campus ambassador",
        "colleges for beta", "edtech", "placement preparation",
        "placement cell", "student", "campus placement",
    ]
    if blueprint:
        payload_str = json.dumps(blueprint.model_dump(mode="json"))
        payload_lower = payload_str.lower()
        for phrase in EDTECH_PHRASES:
            if phrase.lower() in payload_lower:
                contamination.append(phrase)

    report["live_output_contamination"] = {
        "edtech_phrases_found": contamination,
        "contamination_count": len(contamination),
        "clean": len(contamination) == 0,
    }

    report_path = os.path.join(os.path.dirname(__file__), "helios_live_run_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if blueprint:
        bp_path = os.path.join(os.path.dirname(__file__), "helios_blueprint_bc231ccf.json")
        with open(bp_path, "w", encoding="utf-8") as f:
            json.dump(blueprint.model_dump(mode="json"), f, indent=2)
        print(f"[SAVED] Blueprint JSON: {bp_path}")

    print("\n" + "=" * 70)
    print("CONTAMINATION SCAN (NVIDIA live output)")
    print("=" * 70)
    if contamination:
        print(f"  [WARN] Found {len(contamination)} EdTech phrase(s) in live NVIDIA output:")
        for p in contamination:
            print(f"    - '{p}'")
    else:
        print("  [CLEAN] No EdTech phrases found in NVIDIA live output.")

    print(f"\n[SAVED] Full report: {report_path}")
    print(f"[SAVED] Raw diagnostics: {audit_file}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
