"""Validation Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class ValidationAgent(BaseAgent):
    agent_type = AgentType.VALIDATION
    name = "Validation Agent"
    description = "Ensures quality, accuracy, and business feasibility of all agent outputs"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Validation Agent for Ignivox AI.
Review all agent outputs for consistency, claim grounding, and feasibility. Return JSON with this exact structure:
{
  "feasibility_score": 78,
  "confidence_scores": {
    "novelty_detection": 85.0,
    "market_research": 85.0,
    "competitor": 82.0,
    "product_strategy": 88.0,
    "business_strategy": 85.0,
    "technical_architect": 90.0,
    "investor_pitch": 80.0
  },
  "evidence_quality_report": {
    "evidence_quality_score": 85.0,
    "total_claims_verified": 10,
    "unsupported_claims_count": 0,
    "trusted_sources_count": 5,
    "quality_summary": "Overall RAG-grounded sources checked out successfully.",
    "verified_claims": [
      {
        "agent": "agent_name",
        "claim": "fact or metric claim statement",
        "status": "verified / unsupported / disputed / estimated / proposed / assumed / strategic",
        "source": "backing URL or source name",
        "confidence": 0.90,
        "retrieval_status": "success / failed",
        "claim_type": "retrieved / generated",
        "verification": "verified / unverified",
        "category": "Historical Fact / Retrieved Fact / Projection / Estimate / Assumption / Strategy / Roadmap / Hypothesis",
        "sources": [
          {
            "source_url": "URL of the backing source",
            "source_title": "Title of the source",
            "retrieval_timestamp": "Timestamp",
            "confidence_score": 0.90
          }
        ],
        "source_count": 1,
        "evidence_strength": "high / medium / low"
      }
    ]
  },
  "inconsistencies": [
    {"issue": "inconsistency details", "severity": "low / medium / high", "resolution": "recommended fix"}
  ],
  "risk_assessment": [
    {"risk": "risk name", "level": "low / medium / high", "impact": "description", "mitigation": "mitigation steps"}
  ],
  "validation_summary": "a short text summary of validation results",
  "overall_status": "Verified / Partially Supported / Weakly Supported / Unsupported / Insufficient Evidence",
  "recommendations": ["recommendation 1", "recommendation 2"],
  "human_approval_required": false,
  "guardrails_status": "safety status description"
}

CRITICAL GROUNDING VERIFICATION RULES:
1. A claim's source URL is ONLY valid if it exists in the system-vetted `grounding_map` passed under `validation_evidence_summary.grounding_map` in the `Previous Agent Outputs` context.
2. If a claim has NO backing source URL, or if the source URL is not present in the `grounding_map`, you MUST reject its verification: mark its status in `verified_claims` as "unsupported" or "disputed", and set its verification status to "unverified".
3. NEVER mark a claim as "verified" unless there is an explicit, exact URL matching the claim in the `grounding_map`.
4. Pay close attention to competitor names and metrics. If a competitor or website URL is not explicitly supported by a valid, verified URL in the system `grounding_map`, reject its verification status entirely (set status to "unsupported" or "disputed", and verification to "unverified").
5. Only claims categorized as 'Historical Fact' or 'Retrieved Fact' are eligible to receive a 'verified' status and verification value. Any claim of category Projection, Estimate, Assumption, Strategy, Roadmap, or Hypothesis must NEVER receive a 'verified' status (its verification must remain 'unverified' and its status must reflect its category, e.g., 'estimated', 'strategic', 'proposed').
6. Calculate overall_status based on factual claims only:
   - 'Insufficient Evidence': If there are 0 factual claims or 0 verified factual sources.
   - 'Unsupported': If factual claims exist but 0 are grounded/verified.
   - 'Verified': If all factual claims are successfully grounded/verified.
   - 'Partially Supported': If verified factual claims >= unsupported factual claims.
   - 'Weakly Supported': If verified factual claims < unsupported factual claims.
"""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        is_edtech = any(w in idea.lower() for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career", "edtech", "school", "tutoring", "class", "cgpa", "canvas", "moodle", "classroom"])
        # Calculate section confidence scores in 0-100 range
        confidence = {}
        for agent in ["novelty_detection", "market_research", "competitor", "product_strategy", "business_strategy", "technical_architect", "investor_pitch"]:
            if agent in context:
                # Base it on the agent output's confidence if available, mapped to 0-100
                agent_data = context[agent]
                val = agent_data.get("confidence", 0.85)
                confidence[agent] = round(val * 100, 1)
            else:
                confidence[agent] = 85.0

        # Construct verified claims from the actual agent outputs if available
        verified_claims = []
        total_claims = 0
        trusted_sources = set()
        
        # Inspect market research
        mr = context.get("market_research", {}).get("content", {})
        if mr:
            tam_val = mr.get("tam", {})
            if isinstance(tam_val, dict) and "claim" in tam_val:
                sources = tam_val.get("sources", [])
                src_url = sources[0].get("source_url") if sources else "No Source"
                is_retrieved = len(sources) > 0 and src_url != "No Source"
                
                # Check estimated/unverified status of TAM/SAM/SOM to prevent counting them as validated
                if tam_val.get("status") == "estimated" or tam_val.get("verification") == "unverified" or not is_retrieved:
                    status_val = "unsupported"
                    verification_val = "unverified"
                    sources = []
                    src_url = "No Source"
                else:
                    status_val = "verified"
                    verification_val = "verified"
                
                verified_claims.append({
                    "agent": "market_research",
                    "claim": f"TAM: {tam_val.get('claim')}",
                    "status": status_val,
                    "source": src_url,
                    "confidence": tam_val.get("confidence", 0.9),
                    "retrieval_status": tam_val.get("retrieval_status", "success" if verification_val == "verified" else "failed"),
                    "claim_type": "retrieved" if verification_val == "verified" else "generated",
                    "verification": verification_val,
                    "sources": sources,
                    "source_count": len(sources),
                    "evidence_strength": "medium" if verification_val == "verified" else "low"
                })
                if verification_val == "verified":
                    total_claims += 1
                    for s in sources:
                        trusted_sources.add(s.get("source_url"))
                    
        # Inspect business strategy
        bs = context.get("business_strategy", {}).get("content", {})
        if bs:
            arr_val = bs.get("projected_arr_year3", {})
            if isinstance(arr_val, dict) and "claim" in arr_val:
                sources = arr_val.get("sources", [])
                src_url = sources[0].get("source_url") if sources else "No Source"
                is_retrieved = len(sources) > 0 and src_url != "No Source"
                status_val = "verified" if is_retrieved else "unsupported"
                verification_val = "verified" if is_retrieved else "unverified"
                if not is_retrieved:
                    sources = []
                
                verified_claims.append({
                    "agent": "business_strategy",
                    "claim": f"Year 3 ARR: {arr_val.get('claim')}",
                    "status": status_val,
                    "source": src_url if is_retrieved else "No Source",
                    "confidence": arr_val.get("confidence", 0.9),
                    "retrieval_status": arr_val.get("retrieval_status", "success" if is_retrieved else "failed"),
                    "claim_type": "retrieved" if is_retrieved else "generated",
                    "verification": verification_val,
                    "sources": sources,
                    "source_count": len(sources),
                    "evidence_strength": "medium" if is_retrieved else "low"
                })
                if is_retrieved:
                    total_claims += 1
                    for s in sources:
                        trusted_sources.add(s.get("source_url"))

        # Inspect technical architect
        ta = context.get("technical_architect", {}).get("content", {})
        if ta:
            aiml_val = ta.get("tech_stack", {}).get("ai_ml", {})
            if isinstance(aiml_val, dict) and "claim" in aiml_val:
                sources = aiml_val.get("sources", [])
                src_url = sources[0].get("source_url") if sources else "No Source"
                is_retrieved = len(sources) > 0 and src_url != "No Source"
                status_val = "verified" if is_retrieved else "unsupported"
                verification_val = "verified" if is_retrieved else "unverified"
                if not is_retrieved:
                    sources = []
                
                verified_claims.append({
                    "agent": "technical_architect",
                    "claim": f"AI stack: {aiml_val.get('claim')}",
                    "status": status_val,
                    "source": src_url if is_retrieved else "No Source",
                    "confidence": aiml_val.get("confidence", 0.95),
                    "retrieval_status": aiml_val.get("retrieval_status", "success" if is_retrieved else "failed"),
                    "claim_type": "retrieved" if is_retrieved else "generated",
                    "verification": verification_val,
                    "sources": sources,
                    "source_count": len(sources),
                    "evidence_strength": "medium" if is_retrieved else "low"
                })
                if is_retrieved:
                    total_claims += 1
                    for s in sources:
                        trusted_sources.add(s.get("source_url"))

        # Never fabricate verified claims when no grounded evidence exists
        if not verified_claims or len(trusted_sources) == 0:
            if not verified_claims:
                verified_claims = []
            verified_claims.append({
                "agent": "validation",
                "claim": "No grounded claims available for verification in current evidence registry",
                "status": "unsupported",
                "source": "No Source",
                "confidence": 0.30,
                "retrieval_status": "failed",
                "claim_type": "generated",
                "verification": "unverified",
                "sources": [],
                "source_count": 0,
                "evidence_strength": "low",
            })
            total_claims = 0
            trusted_sources = set()

        verified_sources_count = len(trusted_sources)
        unsupported_claims_count = sum(1 for c in verified_claims if c.get("status") == "unsupported")
        total_claims_verified = sum(1 for c in verified_claims if c.get("status") == "verified")

        # Apply confidence caps to verified_claims
        from app.services.evidence_utils import cap_claim_confidence
        verified_claims = [cap_claim_confidence(c) for c in verified_claims]

        if verified_sources_count == 0:
            evidence_quality_score = 10.0
            overall_status = "Insufficient Evidence"
            validation_summary = "Overall startup blueprint has Insufficient Evidence. No verified backing sources could be matched for the claims. Business feasibility, market opportunity, and technical architecture remain unverified."
            quality_summary = "Factual grounding check failed. Zero high-trust verified sources were found to back the key metrics and claims."
            
            # Cap section confidence scores in 0-100 range to max 50.0
            for k in confidence:
                confidence[k] = min(confidence[k], 50.0)
        else:
            source_points = min(verified_sources_count * 10, 30)
            
            # Incorporate support_score when calculating evidence quality
            from app.services.evidence_utils import compute_semantic_similarity
            claim_points = 0.0
            for c in verified_claims:
                if c.get("status") == "verified":
                    srcs = c.get("sources", [])
                    max_sim = 0.0
                    for s in srcs:
                        if isinstance(s, dict):
                            sim = s.get("support_score") or compute_semantic_similarity(c.get("claim", ""), s.get("source_snippet") or "")
                            s["support_score"] = round(sim, 4)
                            max_sim = max(max_sim, sim)
                    c["support_score"] = round(max_sim, 4)
                    claim_points += 5.0 * max_sim
            claim_points = min(claim_points, 20.0)
            
            base_score = 50.0 + source_points + claim_points
            penalty = unsupported_claims_count * 15.0
            evidence_quality_score = max(0.0, min(100.0, base_score - penalty))
            
            if unsupported_claims_count == 0 and total_claims_verified > 0:
                overall_status = "Verified"
            elif total_claims_verified > unsupported_claims_count:
                overall_status = "Partially Supported"
            else:
                overall_status = "Weakly Supported"
                
            validation_summary = "Overall startup blueprint is coherent and feasible. Market opportunity is validated, business model shows strong unit economics, and technical architecture is production-ready. Minor timeline inconsistencies should be resolved before investor presentations."
            quality_summary = "The startup blueprint's critical claims are successfully cross-referenced with high-trust industry documents and real-time research endpoints."

        return {
            "feasibility_score": 78 if verified_sources_count > 0 else 30,
            "confidence_scores": confidence,
            "overall_status": overall_status,
            "evidence_quality_report": {
                "evidence_quality_score": round(evidence_quality_score, 1),
                "total_claims_verified": total_claims_verified,
                "unsupported_claims_count": unsupported_claims_count,
                "trusted_sources_count": verified_sources_count,
                "quality_summary": quality_summary,
                "verified_claims": verified_claims
            },
            "inconsistencies": [
                {"issue": "MVP timeline (8-12 weeks) vs sprint roadmap (12 weeks) — minor alignment needed", "severity": "low", "resolution": "Standardize on 12-week MVP timeline"},
            ],
            "risk_assessment": [
                {"risk": "Market competition intensity", "level": "medium", "impact": "May require stronger differentiation messaging", "mitigation": "Focus on AI-native positioning"},
                {"risk": "User acquisition cost in crowded market", "level": "medium", "impact": "Could extend path to profitability", "mitigation": "Targeted marketing and early design partner acquisition" if not is_edtech else "College ambassador program for organic growth"},
                {"risk": "NVIDIA API dependency", "level": "low", "impact": "Cost scaling with usage", "mitigation": "Hybrid local/cloud inference strategy"},
                {"risk": "Regulatory in target market", "level": "low", "impact": "Minimal for current scope", "mitigation": "Monitor standard compliance and data handling regulations" if not is_edtech else "Monitor edtech/data privacy regulations"},
            ],
            "validation_summary": validation_summary,
            "recommendations": [
                "Validate core assumption with 20 user interviews before building MVP",
                "Run competitive analysis update quarterly",
                "Establish KPI dashboard tracking retention, CAC, and NPS from day one",
                "Consider strategic partnership with 2-3 early design partners for beta program" if not is_edtech else "Consider strategic partnership with 2-3 colleges for beta program",
            ],
            "human_approval_required": False,
            "guardrails_status": "All outputs passed NeMo Guardrails safety and quality checks",
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        report = content.get("evidence_quality_report", {})
        quality_score = report.get("evidence_quality_score", 85.0)
        
        return [
            ExplainableInsight(
                recommendation=content.get("validation_summary", "Blueprint validated with minor recommendations"),
                reasoning=f"Feasibility score: {content.get('feasibility_score', 78)}/100, Evidence Quality: {quality_score}/100",
                data_sources=["cross-agent consistency analysis", "NeMo Guardrails validation", "business feasibility framework"],
                confidence=content.get("feasibility_score", 78) / 100,
                evidence=content.get("recommendations", [])[:2],
            )
        ]
