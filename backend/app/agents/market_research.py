"""Market Research Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class MarketResearchAgent(BaseAgent):
    agent_type = AgentType.MARKET_RESEARCH
    name = "Market Research Agent"
    description = "Discovers market opportunities, trends, and customer pain points"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Market Research Agent for Ignivox AI.
Analyze market opportunities for startup ideas. Return JSON with this exact structure:
{
  "target_audience": "description",
  "problem_statement": "description",
  "pain_points": [
    {
      "claim": "pain point description",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    }
  ],
  "market_trends": [
    {
      "claim": "trend description",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    }
  ],
  "tam": {
    "claim": "$12.5B global addressable market size",
    "value": "$12.5B",
    "assumptions": ["Assumed 23,000 institutions globally", "Average contract value of $540,000/year per college"],
    "assumption_confidence": 0.92,
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "sam": {
    "claim": "$2.8B serviceable market size",
    "value": "$2.8B",
    "assumptions": ["Serviceable market matches top 15% of institutions adopting AI-native infrastructure", "Approximately 3,450 colleges"],
    "assumption_confidence": 0.88,
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "som": {
    "claim": "$85M target market size",
    "value": "$85M",
    "assumptions": ["SOM is 3% of SAM in Year 3", "Targeting 100 high-tier colleges with an average ACV of $850,000"],
    "assumption_confidence": 0.85,
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "growth_rate": {
    "claim": "23% CAGR",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "opportunity_assessment": {
    "score": 82,
    "summary": "opportunity summary description"
  }
}

ADDITIONAL INSTRUCTIONS FOR SIZING METRICS:
Under each of 'tam', 'sam', and 'som', you MUST output:
1. 'value': a string representing the formatted number (e.g. '$12.5B').
2. 'assumptions': an array of strings documenting the equations, logical assumptions, and math used to calculate/derive that number.
3. 'assumption_confidence': a float between 0.0 and 1.0 representing your confidence in these logical sizing assumptions.

Live Sizing Mode: Base all TAM, SAM, and SOM figures and calculations directly on retrieved evidence, reports, and real database facts from the RAG research feeds.
"""

    # NOTE FOR CONTRIBUTORS:
    # - Demo Mode uses dynamic keyword-based sizing heuristics (implemented below)
    #   solely to avoid producing identical mock outputs for different demo runs.
    # - Live Mode performs actual evidence-based calculations derived directly
    #   from retrieved RAG research sources processed by NVIDIA NIM.

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        is_edtech = any(w in idea.lower() for w in ["student", "college", "education", "placement", "learn", "academic", "university"])
        is_health = any(w in idea.lower() for w in ["health", "medical", "patient", "care"])
        is_fintech = any(w in idea.lower() for w in ["fintech", "finance", "payment", "bank"])
        is_energy = any(w in idea.lower() for w in ["energy", "electricity", "utility", "grid", "helios", "scada", "iot", "sensor", "telemetry", "maintenance"])

        if is_edtech:
            raw = self._edtech_market(idea)
        elif is_health:
            raw = self._health_market(idea)
        elif is_fintech:
            raw = self._fintech_market(idea)
        elif is_energy:
            raw = self._energy_market(idea)
        else:
            raw = self._general_market(idea)

        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://www.statista.com/topics/technology", "source_title": "Statista Tech Markets", "retrieval_timestamp": timestamp, "confidence_score": 0.95},
            {"source_url": "https://www.gartner.com/en/research", "source_title": "Gartner Research Portal", "retrieval_timestamp": timestamp, "confidence_score": 0.90}
        ]
        
        return {
            "target_audience": raw["target_audience"],
            "problem_statement": raw["problem_statement"],
            "pain_points": [
                {"claim": p, "sources": sources[:1], "confidence": 0.92}
                for p in raw["pain_points"]
            ],
            "market_trends": [
                {"claim": t, "sources": sources[1:], "confidence": 0.88}
                for t in raw["market_trends"]
            ],
            "tam": {
                "claim": f"{raw['tam']['value']} - {raw['tam']['description']}",
                "value": raw["tam"]["value"],
                "assumptions": raw["tam"].get("assumptions", []),
                "assumption_confidence": raw["tam"].get("assumption_confidence", 0.90),
                "sources": sources,
                "confidence": 0.94
            },
            "sam": {
                "claim": f"{raw['sam']['value']} - {raw['sam']['description']}",
                "value": raw["sam"]["value"],
                "assumptions": raw["sam"].get("assumptions", []),
                "assumption_confidence": raw["sam"].get("assumption_confidence", 0.85),
                "sources": sources[:1],
                "confidence": 0.91
            },
            "som": {
                "claim": f"{raw['som']['value']} - {raw['som']['description']}",
                "value": raw["som"]["value"],
                "assumptions": raw["som"].get("assumptions", []),
                "assumption_confidence": raw["som"].get("assumption_confidence", 0.80),
                "sources": sources[1:],
                "confidence": 0.89
            },
            "growth_rate": {
                "claim": raw["growth_rate"],
                "sources": sources,
                "confidence": 0.92
            },
            "opportunity_assessment": raw["opportunity_assessment"]
        }

    def _edtech_market(self, idea: str) -> dict:
        idea_lower = idea.lower()
        if "attendance" in idea_lower:
            tam_val, tam_desc = "$42B", f"Global market size for tools supporting {idea}"
            sam_val, sam_desc = "$1.5B", f"Higher-ed administrative and operations vertical matching {idea}"
            som_val, som_desc = "$25M", f"Realistic capture targeting universities with core packages for {idea}"
            tam_ass = ["Estimated 23,000 universities and 150,000 schools globally", "Average baseline software spend of $200k/year per school"]
            sam_ass = [f"Serviceable market targeting universities adopting cloud solutions for {idea}", "Estimated 2,300 institutions with $650k average contract size"]
            som_ass = ["SOM based on capturing 1.6% of SAM within the first three years", f"Targeting 200 universities at $125k annual software licensing for {idea}"]
            
            target_audience = "School administrators, operations coordinators, and educational registrars"
            problem_statement = f"Educational institutions lack automated, seamless solutions to manage processes like {idea}, relying instead on manual input and legacy logs."
            pain_points = [
                f"High manual administrative workload for tracking {idea}",
                "Prone to human entry error and data discrepancies",
                f"Lack of real-time insights or automated tracking for {idea}",
                "Integration challenges with other institutional databases"
            ]
            market_trends = [
                f"Growing digitisation of school administrative tasks and {idea}",
                "Shift toward automated verification and cloud logging systems",
                "Demand for simplified, centralized management platforms"
            ]
            opp_summary = f"Substantial opportunity to automate {idea} workflows, reducing admin overhead by up to 35%."
        elif "placement" in idea_lower or "career" in idea_lower:
            tam_val, tam_desc = "$12.5B", "Global career preparation and recruitment market size"
            sam_val, sam_desc = "$2.8B", f"AI-powered professional development and training systems matching {idea}"
            som_val, som_desc = "$85M", "Initial target market capturing professional/technical training centers"
            tam_ass = ["Estimated 42 million technical/professional students globally", "Average career-prep annual training spend of $300 per student"]
            sam_ass = [f"Targeting top 20% of premium professional institutions (approx 8.4M students) for {idea}", "Average software license ACV of $330/year per student"]
            som_ass = ["SOM is 3% of SAM in Year 3", f"Targeting 100 high-tier organizations at $340/student for {idea}"]
            
            target_audience = "Students, job seekers, career advisors, and institutional placement cell staff"
            problem_statement = f"Candidates lack intelligent, adaptive tools to prepare for career opportunities like {idea}, relying on static resources."
            pain_points = [
                f"Inefficient and non-personalized preparation paths for {idea}",
                "Lack of realistic mock environments and real-time skill assessment",
                "High cost of personalized coaching and standard training programs",
                "Difficulty for advisors in tracking student readiness and metrics"
            ]
            market_trends = [
                f"Surge in demand for AI-driven personalized tutoring and {idea}",
                "Employers prioritizing verified skill readiness over generic degrees",
                "Higher education institutions investing in automated placement support software"
            ]
            opp_summary = f"Strong opportunity as companies and colleges seek data-driven platforms to accelerate placement readiness."
        else:
            tam_val, tam_desc = "$40B", "Global higher education and school software market size"
            sam_val, sam_desc = "$5B", f"Addressable market for modern cloud solutions matching {idea}"
            som_val, som_desc = "$50M", "Target market capture within 3 years targeting mid-tier educational institutions"
            tam_ass = ["Estimated 23,000 higher education institutions globally", "Average annual software spending matching the scale of " + idea]
            sam_ass = ["Targeting the top 15% of institutions adopting modern software (approx. 3,450 colleges)", f"Assumes average annual licensing contract value (ACV) of $1.4M for {idea}"]
            som_ass = ["SOM calculated as capturing 1% of the SAM within the first three years", f"Targeting approximately 100 universities with an average contract value (ACV) of $500,000"]

            target_audience = "Students, educators, and administrators in higher education or secondary schools"
            problem_statement = f"Educational institutions face operational inefficiencies managing {idea} due to fragmented, non-AI-native tools."
            pain_points = [
                f"High administrative friction in managing workflows for {idea}",
                f"Lack of interactive, AI-supported assistance for student success in {idea}",
                "High cost and complexity of deploying customized educational software",
                "Poor mobile capability and outdated user interfaces"
            ]
            market_trends = [
                f"Rapid adoption of AI and personalized learning paths for {idea}",
                "Colleges prioritizing cloud-native solutions to modernize workflows",
                "Increased focus on student engagement and success tools"
            ]
            opp_summary = f"Excellent opportunity to capture market share by offering an intuitive, AI-native platform specialized in {idea}."

        return {
            "target_audience": target_audience,
            "problem_statement": problem_statement,
            "pain_points": pain_points,
            "market_trends": market_trends,
            "tam": {
                "value": tam_val,
                "description": tam_desc,
                "assumptions": tam_ass,
                "assumption_confidence": 0.92
            },
            "sam": {
                "value": sam_val,
                "description": sam_desc,
                "assumptions": sam_ass,
                "assumption_confidence": 0.88
            },
            "som": {
                "value": som_val,
                "description": som_desc,
                "assumptions": som_ass,
                "assumption_confidence": 0.85
            },
            "growth_rate": "23% CAGR (2024-2029)",
            "opportunity_assessment": {
                "score": 88,
                "summary": opp_summary
            }
        }

    def _health_market(self, idea: str) -> dict:
        return {
            "target_audience": "Healthcare providers, patients, and health-conscious consumers",
            "problem_statement": "Fragmented healthcare data and lack of AI-driven preventive care solutions",
            "pain_points": ["Delayed diagnoses", "High healthcare costs", "Limited access in rural areas", "Data silos between providers"],
            "market_trends": ["Digital health market $660B by 2028", "AI diagnostics FDA approvals increasing", "Telehealth adoption at 38%"],
            "tam": {
                "value": "$660B", 
                "description": "Global digital health market",
                "assumptions": ["Based on global healthcare IT expenditure trends", "Multiplied by active digital health software adoptions"],
                "assumption_confidence": 0.90
            },
            "sam": {
                "value": "$45B", 
                "description": "AI healthcare applications in developed markets",
                "assumptions": ["Serviceable addressable segment for FDA-cleared AI clinical support systems"],
                "assumption_confidence": 0.84
            },
            "som": {
                "value": "$120M", 
                "description": "Initial target segment",
                "assumptions": ["Targeting 3% of the SAM within the first three years across premium clinics"],
                "assumption_confidence": 0.80
            },
            "growth_rate": "18% CAGR",
            "opportunity_assessment": {"score": 78, "summary": "Large market with regulatory considerations but strong demand"},
        }

    def _fintech_market(self, idea: str) -> dict:
        return {
            "target_audience": "SMBs and underserved consumers seeking modern financial tools",
            "problem_statement": "Legacy financial infrastructure fails to serve modern digital-native users",
            "pain_points": ["High transaction fees", "Slow settlement", "Poor UX in traditional banking", "Limited credit access for SMBs"],
            "market_trends": ["Embedded finance $7T by 2030", "Open banking adoption", "Crypto-fiat integration"],
            "tam": {
                "value": "$310B", 
                "description": "Global fintech market",
                "assumptions": ["Total addressable transaction fees and financial software globally"],
                "assumption_confidence": 0.93
            },
            "sam": {
                "value": "$28B", 
                "description": "Target fintech segment",
                "assumptions": ["AI-native financial workflow segment and transaction volume in target regions"],
                "assumption_confidence": 0.89
            },
            "som": {
                "value": "$95M", 
                "description": "Initial geographic focus",
                "assumptions": ["SOM is 0.3% of SAM targeting metropolitan SMBs in the initial launch year"],
                "assumption_confidence": 0.82
            },
            "growth_rate": "25% CAGR",
            "opportunity_assessment": {"score": 80, "summary": "High-growth market with strong monetization potential"},
        }

    def _energy_market(self, idea: str) -> dict:
        return {
            "target_audience": "Utility operators, grid engineers, and energy service companies (ESCOs)",
            "problem_statement": "Decentralization of energy resources and high frequency smart meter data require real-time grid balancing software",
            "pain_points": [
                "High power grid instability from intermittent renewable energy inputs",
                "Lack of predictive insights for transformer and SCADA asset maintenance",
                "Inefficient load dispatching and manual balancing operations",
                "High security risks from vulnerable industrial IoT endpoints"
            ],
            "market_trends": [
                "Grid modernization spending reaching $120B annually",
                "Rapid scaling of virtual power plants and distributed energy resources (DERs)",
                "Transition from legacy SCADA to cloud-native real-time analytics"
            ],
            "tam": {
                "value": "$120B", 
                "description": "Global grid modernization and utility software market",
                "assumptions": ["Based on global utility IT infrastructure budgets", "Multiplied by software slice of utility operational expenses"],
                "assumption_confidence": 0.90
            },
            "sam": {
                "value": "$18B", 
                "description": "Real-time grid balancing and DERMS platform segment",
                "assumptions": ["Serviceable addressable segment for smart software in developed grid zones"],
                "assumption_confidence": 0.85
            },
            "som": {
                "value": "$50M", 
                "description": "Initial target of mid-size regional cooperatives and ESCOs",
                "assumptions": ["Capturing 0.3% of SAM in initial regions in the first three years"],
                "assumption_confidence": 0.80
            },
            "growth_rate": "14% CAGR",
            "opportunity_assessment": {"score": 85, "summary": "Highly strategic market with high-value contracts and long retention"}
        }

    def _general_market(self, idea: str) -> dict:
        return {
            "target_audience": "Early adopters and SMBs in the target vertical",
            "problem_statement": f"Existing solutions fail to adequately address the core problem that {idea} aims to solve",
            "pain_points": ["Manual processes consuming 40% of work time", "Lack of intelligent automation", "Poor integration with existing tools", "High cost of enterprise alternatives"],
            "market_trends": ["AI adoption in enterprise at 65%", "SaaS market growing 18% annually", "Remote work driving digital transformation"],
            "tam": {
                "value": "$50B", 
                "description": "Addressable market in target vertical",
                "assumptions": ["Estimated global operational SaaS spend in the target industry vertical"],
                "assumption_confidence": 0.85
            },
            "sam": {
                "value": "$5B", 
                "description": "Serviceable market for AI-powered solutions",
                "assumptions": ["Portion of the market transitioning to modern AI-integrated software"],
                "assumption_confidence": 0.80
            },
            "som": {
                "value": "$50M", 
                "description": "Realistic 3-year capture",
                "assumptions": ["Capturing 1% of the SAM targeting mid-market SMBs in initial launch regions"],
                "assumption_confidence": 0.75
            },
            "growth_rate": "20% CAGR",
            "opportunity_assessment": {"score": 75, "summary": "Solid opportunity with room for AI-native differentiation"},
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        opp = content.get("opportunity_assessment", {})
        score = opp.get("score", 75) if isinstance(opp, dict) else 75
        
        def _get_val(v):
            if isinstance(v, dict) and "claim" in v:
                return str(v["claim"])
            if isinstance(v, dict):
                return v.get("claim", str(v))
            return str(v)
            
        target = _get_val(content.get('target_audience', 'identified segment'))
        prob = _get_val(content.get('problem_statement', ''))
        pain_points = content.get("pain_points", [])
        evidence = [_get_val(p) for p in pain_points[:3]]
        
        return [
            ExplainableInsight(
                recommendation=f"Target {target} as primary market",
                reasoning=prob,
                data_sources=["market research databases", "industry reports", "NeMo Retriever knowledge base"],
                confidence=score / 100 if score > 1 else score,
                evidence=evidence,
            )
        ]
