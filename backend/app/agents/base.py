"""Base agent class for Ignivox AI agents."""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

from app.config import settings
from app.models.schemas import AgentOutput, AgentStatus, AgentType, ExplainableInsight
from app.services.evidence_utils import (
    build_grounding_map,
    detect_template_architecture,
    enforce_competitor_evidence,
    enforce_validation_output,
    fix_template_architecture,
    format_rag_for_prompt,
    merge_cumulative_registry,
    normalize_rag_sources,
    sanitize_grounded_claims,
    sanitize_investor_pitch,
    remove_edtech_contamination,
)
from app.services.nemo_guardrails import guardrails
from app.services.nvidia_nim import nim_service

logger = logging.getLogger(__name__)

EventCallback = Callable[[str, AgentType, AgentStatus, str, float], Awaitable[None]]

GROUNDING_INSTRUCTIONS = """
INSTRUCTIONS FOR EVIDENCE GROUNDING:
For every key metric, TAM/SAM/SOM size, competitor claim, feature timeline, revenue projection, tech stack recommendation, or launch detail you output, you must ground it using the following JSON structure:
{
  "claim": "string representing the fact or claim",
  "sources": [
    {
      "source_url": "URL of the backing source from Context and Research Feeds",
      "source_title": "Title of the source",
      "retrieval_timestamp": "Timestamp",
      "confidence_score": 0.90
    }
  ],
  "confidence": 0.90,
  "retrieval_status": "success",
  "claim_type": "retrieved",
  "verification": "verified",
  "source_count": 1,
  "evidence_strength": "medium",
  "category": "Historical Fact"
}

Explicit claim categories to choose from (always choose the best fit):
- 'Historical Fact' (verifiable historical event or performance)
- 'Retrieved Fact' (verifiable industry/market fact retrieved from research)
- 'Projection' (forward-looking prediction, such as revenue, growth, ARR)
- 'Estimate' (approximate calculation, such as TAM/SAM/SOM, CAC, LTV)
- 'Assumption' (foundational business or user assumption)
- 'Strategy' (strategic decision, business model, pricing structure)
- 'Roadmap' (MVP build timeline, features, sprint roadmap milestones)
- 'Hypothesis' (unproven speculative theory)

RULES FOR RETRIEVAL FAILURE & HALLUCINATION PREVENTION:
1. If the "Context and Research Feeds" above is empty or does NOT contain any relevant or verified backing sources for a claim, DO NOT fabricate or hallucinate any URLs, reports, statistics, competitors, or market sizes. Rely exclusively on historical memory and vector retrieval context. Reduce the confidence score and mark the claim as unverified / partially grounded.
2. In case of retrieval failure or missing evidence, you MUST output the following structure:
{
  "claim": "No verified external sources available",
  "sources": [],
  "confidence": 0.22,
  "retrieval_status": "failed",
  "claim_type": "generated",
  "verification": "unverified",
  "source_count": 0,
  "evidence_strength": "low",
  "category": "Hypothesis"
}
3. For claims derived from external search links, set:
   - "retrieval_status": "success"
   - "claim_type": "retrieved"
   - "verification": "verified" (only if the retrieved source content explicitly supports and validates the claim statement, otherwise "unverified")
   - "source_count": number of sources used (integer)
   - "evidence_strength": "high" (if 3+ high-quality sources), "medium" (if 1-2 sources), or "low" (if 0 sources)
4. For purely analytical reasoning, projections, or recommendations not derived from the web feed, set:
   - "retrieval_status": "success" (as retrieval did not fail, but reasoning is generated)
   - "claim_type": "generated"
   - "verification": "unverified"
   - "source_count": 0
   - "evidence_strength": "low"
"""


class BaseAgent(ABC):
    agent_type: AgentType
    name: str
    description: str

    def __init__(self) -> None:
        self.status = AgentStatus.IDLE

    async def _monitor_agent_time(self) -> None:
        try:
            await asyncio.sleep(30.0)
            logger.warning("WARNING: Agent '%s' execution has exceeded 30 seconds.", self.name)
            await asyncio.sleep(30.0)
            logger.warning("WARNING: Agent '%s' execution has exceeded 60 seconds.", self.name)
            await asyncio.sleep(30.0)
            logger.warning("WARNING: Agent '%s' execution has exceeded 90 seconds.", self.name)
        except asyncio.CancelledError:
            pass

    def _validate_investor_pitch(self, data: dict[str, Any]) -> list[str]:
        errors = []
        if not isinstance(data, dict):
            return ["Root of response is not a JSON object"]
        
        required_keys = ["executive_summary", "pitch_slides", "funding_strategy", "funding_ask", "narrative"]
        for k in required_keys:
            if k not in data:
                errors.append(f"Missing required top-level key: '{k}'")
        
        # Check executive_summary
        exec_sum = data.get("executive_summary")
        if exec_sum is not None:
            if not isinstance(exec_sum, dict):
                errors.append("Key 'executive_summary' is not a JSON object")
            elif "claim" not in exec_sum:
                errors.append("Key 'executive_summary' missing required child key: 'claim'")
                
        # Check pitch_slides
        slides = data.get("pitch_slides")
        if slides is not None:
            if not isinstance(slides, list):
                errors.append("Key 'pitch_slides' is not a JSON array")
            else:
                for idx, slide in enumerate(slides):
                    if not isinstance(slide, dict):
                        errors.append(f"pitch_slides[{idx}] is not a JSON object")
                    else:
                        for skey in ["title", "content", "speaker_notes"]:
                            if skey not in slide:
                                errors.append(f"pitch_slides[{idx}] missing key: '{skey}'")
                                
        # Check funding_strategy
        strategy = data.get("funding_strategy")
        if strategy is not None:
            if not isinstance(strategy, dict):
                errors.append("Key 'funding_strategy' is not a JSON object")
            else:
                for skey in ["stage", "target_investors", "timeline", "key_metrics_for_series_a"]:
                    if skey not in strategy:
                        errors.append(f"funding_strategy missing key: '{skey}'")
                        
        # Check funding_ask
        ask = data.get("funding_ask")
        if ask is not None:
            if not isinstance(ask, dict):
                errors.append("Key 'funding_ask' is not a JSON object")
            else:
                for skey in ["amount", "valuation", "use_of_funds", "runway_months", "milestones_with_funding"]:
                    if skey not in ask:
                        errors.append(f"funding_ask missing key: '{skey}'")
                
                uof = ask.get("use_of_funds")
                if uof is not None and not isinstance(uof, dict):
                    errors.append("funding_ask.use_of_funds is not a JSON object")
                    
        # Check narrative
        narrative = data.get("narrative")
        if narrative is not None:
            if not isinstance(narrative, dict):
                errors.append("Key 'narrative' is not a JSON object")
            elif "claim" not in narrative:
                errors.append("Key 'narrative' missing required child key: 'claim'")
                
        return errors

    @abstractmethod
    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        pass

    @abstractmethod
    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        pass

    async def run(
        self,
        idea: str,
        context: dict[str, Any],
        rag_context: str = "",
        on_event: EventCallback | None = None,
    ) -> AgentOutput:
        start = time.time()
        self.status = AgentStatus.WORKING

        if on_event:
            await on_event("agent_start", self.agent_type, AgentStatus.WORKING, f"{self.name} analyzing...", 0)

        # Initialize temporary diagnostics
        diagnostics = {
            "agent": self.name,
            "execution_mode": "nvidia_live" if settings.use_nvidia else "fallback_demo",
            "nvidia_request_sent": False,
            "nvidia_response_received": False,
            "response_length": 0,
            "json_parse_success": False,
            "schema_validation_success": False,
            "fallback_reason": "none" if settings.use_nvidia else "NVIDIA is disabled",
            "exception": ""
        }

        monitor_task = asyncio.create_task(self._monitor_agent_time())
        try:
            if settings.use_nvidia:
                diagnostics["nvidia_request_sent"] = True
                try:
                    content = await self._run_nvidia(idea, context, rag_context, diagnostics)
                    diagnostics["nvidia_response_received"] = True
                    diagnostics["response_length"] = len(json.dumps(content))
                    diagnostics["json_parse_success"] = True
                    diagnostics["schema_validation_success"] = True
                except Exception as nim_err:
                    is_schema_fail = isinstance(nim_err, ValueError) and "Schema validation failed" in str(nim_err)
                    diagnostics["nvidia_response_received"] = is_schema_fail or ("JSONDecodeError" in type(nim_err).__name__ or "ValueError" in type(nim_err).__name__)
                    diagnostics["json_parse_success"] = is_schema_fail
                    diagnostics["schema_validation_success"] = False
                    diagnostics["fallback_reason"] = f"NVIDIA NIM error: {str(nim_err)}"
                    diagnostics["exception"] = f"{type(nim_err).__name__}: {str(nim_err)}"
                    raise
            else:
                content = self.get_demo_output(idea, context)

            content = self._post_process_output(content, idea, context, rag_context)

            try:
                insights = self.build_insights(content)
            except Exception as insight_err:
                logger.warning("%s build_insights failed, using empty insights: %s", self.name, insight_err)
                insights = []
            content_str = json.dumps(content)
            validation = guardrails.validate_output(content_str, self.name)

            self.status = AgentStatus.COMPLETE
            duration = int((time.time() - start) * 1000)

            # Record and display per-agent metrics
            metrics = {
                "agent": self.name,
                "duration_ms": duration,
                "response_chars": len(content_str) if settings.use_nvidia else 0,
                "fallback_reason": "none"
            }
            logger.info("Agent Metrics:\n%s", json.dumps(metrics, indent=2))

            if on_event:
                await on_event(
                    "agent_complete",
                    self.agent_type,
                    AgentStatus.COMPLETE,
                    f"{self.name} completed analysis",
                    100,
                )

            # Log diagnostic report
            logger.info(
                "NIM Agent Diagnostic Report:\n"
                "  Agent: %s\n"
                "  Response Length: %d chars\n"
                "  JSON Parse Success: %s\n"
                "  Schema Validation Success: %s\n"
                "  Fallback Reason: %s\n"
                "  Exception: %s",
                diagnostics.get("agent"),
                diagnostics.get("response_length"),
                diagnostics.get("json_parse_success"),
                diagnostics.get("schema_validation_success"),
                diagnostics.get("fallback_reason"),
                diagnostics.get("exception"),
            )

            # Write diagnostics to file
            import os
            from app.config import BACKEND_DIR
            try:
                audit_file = os.path.join(BACKEND_DIR, "audit_diagnostics.json")
                data = []
                if os.path.exists(audit_file):
                    try:
                        with open(audit_file, "r") as f:
                            data = json.load(f)
                    except Exception:
                        pass
                data.append(diagnostics)
                with open(audit_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

            return AgentOutput(
                agent=self.agent_type,
                status=AgentStatus.COMPLETE,
                title=self.name,
                content=content,
                insights=insights,
                confidence=validation["confidence"],
                duration_ms=duration,
            )
        except Exception as e:
            logger.error("%s failed: %s", self.name, e)
            self.status = AgentStatus.ERROR

            diagnostics["execution_mode"] = "fallback_demo" if not settings.use_nvidia else "nvidia_live"
            if diagnostics["fallback_reason"] == "none":
                diagnostics["fallback_reason"] = f"Pipeline execution failed: {str(e)}"
            diagnostics["exception"] = f"{type(e).__name__}: {str(e)}"

            duration = int((time.time() - start) * 1000)

            metrics = {
                "agent": self.name,
                "duration_ms": duration,
                "response_chars": 0,
                "fallback_reason": diagnostics["fallback_reason"],
            }
            logger.info("Agent Metrics (FAILED):\n%s", json.dumps(metrics, indent=2))

            logger.info(
                "NIM Agent Diagnostic Report (FAILED):\n"
                "  Agent: %s\n"
                "  Response Length: %d chars\n"
                "  JSON Parse Success: %s\n"
                "  Schema Validation Success: %s\n"
                "  Fallback Reason: %s\n"
                "  Exception: %s",
                diagnostics.get("agent"),
                diagnostics.get("response_length"),
                diagnostics.get("json_parse_success"),
                diagnostics.get("schema_validation_success"),
                diagnostics.get("fallback_reason"),
                diagnostics.get("exception"),
            )

            import os
            from app.config import BACKEND_DIR
            try:
                audit_file = os.path.join(BACKEND_DIR, "audit_diagnostics.json")
                data = []
                if os.path.exists(audit_file):
                    try:
                        with open(audit_file, "r") as f:
                            data = json.load(f)
                    except Exception:
                        pass
                data.append(diagnostics)
                with open(audit_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

            if settings.use_nvidia:
                raise

            content = self.get_demo_output(idea, context)
            content = self._post_process_output(content, idea, context, rag_context)
            return AgentOutput(
                agent=self.agent_type,
                status=AgentStatus.ERROR,
                title=self.name,
                content=content,
                insights=self.build_insights(content),
                confidence=0.5,
                duration_ms=duration,
            )
        finally:
            monitor_task.cancel()

    def _post_process_output(
        self,
        content: dict[str, Any],
        idea: str,
        context: dict[str, Any],
        rag_context: str,
    ) -> dict[str, Any]:
        """Apply code-level grounding enforcement after LLM or demo output."""
        registry = merge_cumulative_registry(
            context.get("evidence_registry"),
            normalize_rag_sources(rag_context),
        )
        content = sanitize_grounded_claims(content, registry, self.agent_type.value)

        if self.agent_type == AgentType.COMPETITOR:
            content = enforce_competitor_evidence(content, registry, idea)

        if self.agent_type == AgentType.TECHNICAL_ARCHITECT:
            if detect_template_architecture(content):
                content = fix_template_architecture(content, idea)

        if self.agent_type == AgentType.INVESTOR_PITCH:
            content = sanitize_investor_pitch(content, context, registry)

        if self.agent_type == AgentType.VALIDATION:
            concise = self._get_concise_context_summary(context, rag_context)
            grounding_map = concise.get("validation_evidence_summary", {}).get("grounding_map", [])
            content = enforce_validation_output(content, grounding_map, registry)

        content = remove_edtech_contamination(content, idea)

        return content

    def _get_concise_context_summary(self, context: dict[str, Any], rag_context_str: str | None = None) -> dict[str, Any]:
        """Extract compressed context while preserving grounding evidence and frontier keys."""
        registry = merge_cumulative_registry(
            context.get("evidence_registry"),
            normalize_rag_sources(rag_context_str or "{}"),
        )

        mr_content = context.get("market_research", {}).get("content", {}) if isinstance(context.get("market_research"), dict) else {}
        
        # Build market opportunity while preserving sources
        mr_opp_val = mr_content.get("tam")
        if isinstance(mr_opp_val, dict):
            market_opp = {
                "claim": f"TAM: {mr_opp_val.get('claim', 'N/A')}",
                "sources": [
                    {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                    for s in mr_opp_val.get("sources", []) if isinstance(s, dict)
                ]
            }
        else:
            market_opp = {"claim": f"TAM: {mr_opp_val or 'N/A'}", "sources": []}

        market = {
            "target_audience": mr_content.get("target_audience") or "N/A",
            "problem": mr_content.get("problem_statement") or "N/A",
            "market_opportunity": market_opp,
            "pain_points": [
                {
                    "claim": p.get("claim") if isinstance(p, dict) else str(p),
                    "sources": [
                        {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                        for s in p.get("sources", []) if isinstance(s, dict)
                    ] if isinstance(p, dict) else []
                }
                for p in mr_content.get("pain_points", [])[:4]
            ],
        }

        # Build competitors, differentiation, market gaps preserving sources
        comp_content = context.get("competitor", {}).get("content", {}) if isinstance(context.get("competitor"), dict) else {}
        
        preserved_competitors = {}
        raw_competitors = comp_content.get("competitors", {})
        if isinstance(raw_competitors, dict):
            categories = ["direct_competitors", "indirect_competitors", "alternative_solutions", "research_alternatives", "enabling_technologies"]
            for category in categories:
                preserved_competitors[category] = []
                for c in raw_competitors.get(category, []):
                    if isinstance(c, dict):
                        comp_entry = {
                            "name": c.get("name"),
                            "strengths": c.get("strengths", []),
                            "weaknesses": c.get("weaknesses", []),
                        }
                        for field in ("pricing", "market_share"):
                            field_val = c.get(field)
                            if isinstance(field_val, dict):
                                comp_entry[field] = {
                                    "claim": field_val.get("claim"),
                                    "sources": [
                                        {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                                        for s in field_val.get("sources", []) if isinstance(s, dict)
                                    ]
                                }
                            else:
                                comp_entry[field] = {"claim": str(field_val) if field_val else "N/A", "sources": []}
                        preserved_competitors[category].append(comp_entry)

        differentiation = []
        for d in comp_content.get("differentiation", []):
            if isinstance(d, dict):
                differentiation.append({
                    "claim": d.get("claim"),
                    "sources": [
                        {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                        for s in d.get("sources", []) if isinstance(s, dict)
                    ]
                })
            elif isinstance(d, str):
                differentiation.append({"claim": d, "sources": []})

        market_gaps = []
        for g in comp_content.get("market_gaps", []):
            if isinstance(g, dict):
                market_gaps.append({
                    "claim": g.get("claim"),
                    "sources": [
                        {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                        for s in g.get("sources", []) if isinstance(s, dict)
                    ]
                })
            elif isinstance(g, str):
                market_gaps.append({"claim": g, "sources": []})

        competitors = {
            "competitors": preserved_competitors,
            "differentiation": differentiation,
            "market_gaps": market_gaps,
        }

        # Build product strategy features and personas
        ps_content = context.get("product_strategy", {}).get("content", {}) if isinstance(context.get("product_strategy"), dict) else {}
        mvp_features = []
        for f in ps_content.get("mvp_definition", {}).get("features", []):
            if isinstance(f, dict):
                mvp_features.append({
                    "claim": f.get("claim"),
                    "sources": [
                        {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                        for s in f.get("sources", []) if isinstance(s, dict)
                    ]
                })
            else:
                mvp_features.append({"claim": str(f), "sources": []})

        roadmap_list = []
        for phase_info in ps_content.get("feature_roadmap", []):
            if isinstance(phase_info, dict):
                phase = phase_info.get("phase", "")
                feats = phase_info.get("features", [])
                roadmap_list.append(f"{phase}: {', '.join(feats)}")
            elif isinstance(phase_info, str):
                roadmap_list.append(phase_info)

        product = {
            "vision": {
                "claim": ps_content.get("product_vision", {}).get("claim") if isinstance(ps_content.get("product_vision"), dict) else ps_content.get("product_vision") or "N/A",
                "sources": [
                    {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                    for s in ps_content.get("product_vision", {}).get("sources", []) if isinstance(s, dict)
                ] if isinstance(ps_content.get("product_vision"), dict) else []
            },
            "mvp_features": mvp_features,
            "roadmap_summary": roadmap_list,
            "user_personas": ps_content.get("user_personas", [])[:4],
        }

        # Build business pricing and projections with sources
        bs_content = context.get("business_strategy", {}).get("content", {}) if isinstance(context.get("business_strategy"), dict) else {}
        pricing_strategy = bs_content.get("pricing_strategy", {})

        arr3_val = bs_content.get("projected_arr_year3")
        if isinstance(arr3_val, dict):
            arr3 = {
                "claim": f"Year 3 ARR: {arr3_val.get('claim', 'N/A')}",
                "sources": [
                    {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                    for s in arr3_val.get("sources", []) if isinstance(s, dict)
                ]
            }
        else:
            arr3 = {"claim": f"Year 3 ARR: {arr3_val or 'N/A'}", "sources": []}

        key_business_constraints = {}
        for metric in ("cac", "ltv", "payback_period", "ltv_cac_ratio"):
            metric_val = bs_content.get("unit_economics", {}).get(metric)
            if isinstance(metric_val, dict):
                key_business_constraints[metric] = {
                    "claim": metric_val.get("claim"),
                    "sources": [
                        {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                        for s in metric_val.get("sources", []) if isinstance(s, dict)
                    ]
                }
            else:
                key_business_constraints[metric] = {"claim": str(metric_val) if metric_val else "N/A", "sources": []}

        business = {
            "revenue_model": {
                "claim": bs_content.get("revenue_model", {}).get("claim") if isinstance(bs_content.get("revenue_model"), dict) else bs_content.get("revenue_model") or "N/A",
                "sources": [
                    {"source_url": s.get("source_url"), "source_title": s.get("source_title")}
                    for s in bs_content.get("revenue_model", {}).get("sources", []) if isinstance(s, dict)
                ] if isinstance(bs_content.get("revenue_model"), dict) else []
            },
            "pricing": pricing_strategy,
            "arr_projection": arr3,
            "key_business_constraints": key_business_constraints,
        }

        grounding_map = build_grounding_map(context, registry)
        claim_lineage = context.get("claim_lineage", grounding_map)[:40]
        preserved_sources = grounding_map[:12]

        nd_content = context.get("novelty_detection", {}).get("content", {}) if isinstance(context.get("novelty_detection"), dict) else {}
        novelty_score = nd_content.get("novelty_score", 0)
        market_classification = nd_content.get("market_classification", "N/A")
        is_frontier = context.get("is_frontier_mode", False)

        verified_claims = sum(1 for entry in grounding_map if entry.get("source_url"))
        evidence_summary = {
            "novelty_score": novelty_score,
            "market_type": market_classification,
            "is_frontier_mode": is_frontier,
            "retrieval_stats": {
                "verified_claims": verified_claims,
                "unverified_claims": max(0, len(claim_lineage) - verified_claims),
                "failed_retrievals": 0,
            },
            "evidence_stats": {
                "total_sources": len({entry["source_url"] for entry in grounding_map if entry.get("source_url")}),
                "total_claims": len(grounding_map),
            },
            "grounding_map": grounding_map,
            "preserved_sources": preserved_sources,
            "claim_lineage": claim_lineage,
        }

        return {
            "market": market,
            "competitors": competitors,
            "product": product,
            "business": business,
            "validation_evidence_summary": evidence_summary,
        }

    async def _run_nvidia(self, idea: str, context: dict[str, Any], rag_context: str, diagnostics: dict[str, Any] = None) -> dict[str, Any]:
        rag_context = normalize_rag_sources(rag_context)
        serializable_context = {k: v for k, v in context.items() if k != "evaluation_context"}
        context_summary_before = json.dumps({k: v.get("content", {}) if isinstance(v, dict) else v for k, v in serializable_context.items()}, indent=2)

        rag_formatted = format_rag_for_prompt(rag_context)

        # Identify top 5 largest context contributors
        contributors = {}
        for k, v in serializable_context.items():
            val = v.get("content", {}) if isinstance(v, dict) else v
            contributors[f"agent_{k}"] = len(json.dumps(val))
        
        try:
            structured_rag = json.loads(rag_context)
            contributors["rag_vector_context"] = len(json.dumps(structured_rag.get("vector_context", [])))
            contributors["rag_memory_context"] = len(json.dumps(structured_rag.get("memory_context", [])))
            contributors["rag_live_sources"] = len(json.dumps(structured_rag.get("live_sources", [])))
        except Exception:
            contributors["rag_context"] = len(rag_formatted)

        sorted_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
        top_5_contributors = sorted_contributors[:5]

        # Define prompts and details before optimization
        system_prompt = self.get_system_prompt(context)
        user_prompt_before = f"""Startup Idea: {idea}

Previous Agent Outputs:
{context_summary_before}

Context and Research Feeds:
{rag_formatted}
{GROUNDING_INSTRUCTIONS}
Provide a comprehensive analysis as structured JSON matching the expected output format for {self.name}."""

        system_prompt_len = len(system_prompt)
        context_len_before = len(context_summary_before) + len(rag_formatted)
        user_input_len_before = len(user_prompt_before) - context_len_before
        prompt_length_before = system_prompt_len + len(user_prompt_before)

        # Optimize for specific agents
        if self.agent_type in (
            AgentType.TECHNICAL_ARCHITECT,
            AgentType.INVESTOR_PITCH,
            AgentType.EXECUTION_PLANNING,
            AgentType.VALIDATION,
        ):
            concise_summary = self._get_concise_context_summary(context, rag_context)
            context_summary_after = json.dumps(concise_summary, indent=2)
            user_prompt_after = f"""Startup Idea: {idea}

Previous Agent Outputs:
{context_summary_after}

Context and Research Feeds:
{rag_formatted}
{GROUNDING_INSTRUCTIONS}
Provide a comprehensive analysis as structured JSON matching the expected output format for {self.name}."""

            context_len_after = len(context_summary_after) + len(rag_formatted)
            user_input_len_after = len(user_prompt_after) - context_len_after
            prompt_length_after = system_prompt_len + len(user_prompt_after)
            compression_ratio = round((1 - prompt_length_after / prompt_length_before) * 100, 1)
            user_prompt = user_prompt_after
            context_summary = context_summary_after
        else:
            context_len_after = context_len_before
            user_input_len_after = user_input_len_before
            prompt_length_after = prompt_length_before
            compression_ratio = 0.0
            user_prompt = user_prompt_before
            context_summary = context_summary_before

        # FRONTIER MODE DYNAMIC INJECTIONS
        if context.get("is_frontier_mode"):
            user_prompt += "\n\nCRITICAL FRONTIER MODE INSTRUCTION:\n" \
                           "This startup idea operates in a Frontier / Speculative Market. Therefore:\n" \
                           "1. Disable verified market sizing claims (e.g. TAM/SAM/SOM value numbers) unless explicitly supported by retrieved evidence from RAG context. Otherwise, set values to 'Unknown/Speculative' or present them as hypotheses.\n" \
                           "2. When evidence is low or missing, mark claims with claim_type='generated', verification='unverified', and evidence_strength='low'. Lower the claim confidence score (e.g., maximum 0.60).\n" \
                           "3. Reframe the tone from established facts to strategic hypotheses."

            if self.agent_type == AgentType.VALIDATION:
                system_prompt += "\n\nVALIDATION FRONTIER MODE RULES:\n" \
                                 "Since this is a speculative market:\n" \
                                 "1. You MUST flag any claim as 'unsupported' or 'disputed' if it is marked as 'verified' but lacks concrete, external, verified links in its 'sources' array.\n" \
                                 "2. Reject fabricated companies, fake repositories, fake launch announcements, or non-existent reports, forcing them to be labeled as 'unverified' and claim_type='generated'."

        # Log prompt breakdown and contributors
        logger.info("================ PROMPT AUDIT REPORT (%s) ================", self.name)
        logger.info("Before Optimization:")
        logger.info("  - System Prompt Length: %d chars", system_prompt_len)
        logger.info("  - Context Length: %d chars", context_len_before)
        logger.info("  - User Input Length: %d chars", user_input_len_before)
        logger.info("  - Total Prompt Length: %d chars", prompt_length_before)
        logger.info("Top 5 Context Contributors:")
        for name, size in top_5_contributors:
            logger.info("  - %s: %d chars", name, size)
        
        if self.agent_type in (
            AgentType.TECHNICAL_ARCHITECT,
            AgentType.INVESTOR_PITCH,
            AgentType.EXECUTION_PLANNING,
            AgentType.VALIDATION,
        ):
            logger.info("After Optimization (Concise Summary):")
            logger.info("  - Context Length: %d chars", context_len_after)
            logger.info("  - User Input Length: %d chars", user_input_len_after)
            logger.info("  - Total Prompt Length: %d chars", prompt_length_after)
            logger.info("  - Compression Ratio: %.1f%%", compression_ratio)
        logger.info("==========================================================")

        # Baseline durations for before/after comparison
        baseline_duration = "120.02s (Timeout)" if self.agent_type == AgentType.TECHNICAL_ARCHITECT else ("119.00s" if self.agent_type == AgentType.INVESTOR_PITCH else "N/A")

        validation_fn = self._validate_investor_pitch if self.agent_type == AgentType.INVESTOR_PITCH else None
        max_tokens = 8192 if self.agent_type == AgentType.MARKET_RESEARCH else 4096
        nim_start = time.time()
        result = await nim_service.complete_json(
            system_prompt,
            user_prompt,
            agent_name=self.name,
            validation_fn=validation_fn,
            max_tokens=max_tokens,
        )
        nim_duration = time.time() - nim_start

        logger.info(
            "Execution Time Comparison for %s:\n"
            "  - Execution Time Before: %s\n"
            "  - Execution Time After: %.2fs",
            self.name,
            baseline_duration,
            nim_duration
        )

        if diagnostics is not None:
            diagnostics.update({
                "prompt_length_before": prompt_length_before,
                "prompt_length_after": prompt_length_after,
                "compression_ratio": compression_ratio,
                "system_prompt_length": system_prompt_len,
                "context_length_before": context_len_before,
                "context_length_after": context_len_after,
                "user_input_length_before": user_input_len_before,
                "user_input_length_after": user_input_len_after,
                "execution_time_before": baseline_duration,
                "execution_time_after": f"{nim_duration:.2f}s",
                "top_5_contributors": [{"name": n, "size_chars": s} for n, s in top_5_contributors]
            })

        return result
