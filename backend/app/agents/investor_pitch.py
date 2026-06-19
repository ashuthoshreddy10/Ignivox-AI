"""Investor Pitch Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class InvestorPitchAgent(BaseAgent):
    agent_type = AgentType.INVESTOR_PITCH
    name = "Investor Pitch Agent"
    description = "Creates funding-ready pitch deck content and executive summaries"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Investor Pitch Agent for Ignivox AI.
Create compelling pitch deck content. Return JSON with this exact structure:
{
  "executive_summary": {
    "claim": "a short text summary of the business blueprint and market opportunity",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "pitch_slides": [
    {
      "title": "slide title",
      "content": "slide content text",
      "speaker_notes": "speaker notes text for presentation"
    }
  ],
  "funding_strategy": {
    "stage": "Pre-seed / Seed / Series A",
    "target_investors": ["VCs", "Angel investors"],
    "timeline": "fundraising timeline strategy",
    "key_metrics_for_series_a": ["metric 1", "metric 2"]
  },
  "funding_ask": {
    "amount": {
      "claim": "$1.5M",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "valuation": {
      "claim": "$8M pre-money",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "use_of_funds": {
      "engineering": "45%",
      "marketing_growth": "30%",
      "operations": "15%",
      "reserve": "10%"
    },
    "runway_months": {
      "claim": "18",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "milestones_with_funding": ["milestone 1", "milestone 2"]
  },
  "narrative": {
    "claim": "the storytelling narrative of the pitch",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  }
}
Ensure that "use_of_funds" in "funding_ask" is a dictionary mapping categories to their percentage strings (e.g., {"engineering": "45%", "marketing_growth": "30%"}).

CRITICAL TRACTION & GROUNDING RULES:
1. You are strictly forbidden from generating or claiming historical/existing traction, patents, partnerships, prototypes, revenue, active customers, or successful deployments unless they are explicitly documented in the previous agent context.
2. If no such grounded context exists, formulate statements to focus purely on future roadmap milestones (e.g., planned patent filings, target partnerships, target customer acquisition, and planned MVP development timelines)."""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://www.crunchbase.com/hub/seed-funding", "source_title": "Crunchbase Seed Funding Reports", "retrieval_timestamp": timestamp, "confidence_score": 0.95},
            {"source_url": "https://pitchbook.com/news", "source_title": "PitchBook Venture Monitor", "retrieval_timestamp": timestamp, "confidence_score": 0.92}
        ]

        # Check domain to customize VCs
        idea_lower = idea.lower()
        if any(w in idea_lower for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career"]):
            vc_sector = "EdTech-focused VCs"
        elif any(w in idea_lower for w in ["health", "medical", "patient", "clinic", "hospital", "doctor"]):
            vc_sector = "Healthcare/HealthTech VCs"
        elif any(w in idea_lower for w in ["fintech", "finance", "payment", "bank", "invest"]):
            vc_sector = "Fintech VCs"
        elif any(w in idea_lower for w in ["cyber", "security", "threat", "hack", "penetration", "siem"]):
            vc_sector = "Cybersecurity VCs"
        elif any(w in idea_lower for w in ["supply chain", "logistics", "shipping", "warehouse", "inventory"]):
            vc_sector = "Logistics/Supply Chain VCs"
        elif any(w in idea_lower for w in ["energy", "utility", "grid", "maintenance", "sensor", "scada", "iot"]):
            vc_sector = "Industrial IoT / Energy VCs"
        else:
            vc_sector = "Enterprise SaaS VCs"

        target_investors = [vc_sector, "AI/ML specialist funds", "Angel investors with domain expertise"]

        market = context.get("market_research", {}).get("content", {}) if isinstance(context.get("market_research"), dict) else {}
        business = context.get("business_strategy", {}).get("content", {}) if isinstance(context.get("business_strategy"), dict) else {}

        # Safe retrievals for nested dict/values
        def _get_claim(d, key, default):
            v = d.get(key, {})
            return v.get("claim", default) if isinstance(v, dict) else str(v) or default

        tam_val = _get_claim(market, "tam", "$12B")
        arr_val = _get_claim(business, "projected_arr_year3", "$8.5M")
        ratio_val = business.get("unit_economics", {}).get("ltv_cac_ratio", {})
        ratio_str = ratio_val.get("claim", "13:1") if isinstance(ratio_val, dict) else str(ratio_val) or "13:1"

        return {
            "executive_summary": {
                "claim": f"We're building the AI-native platform that transforms {idea} — addressing a {tam_val} market with a SaaS model projected to reach {arr_val} ARR by year 3.",
                "sources": sources,
                "confidence": 0.93
            },
            "pitch_slides": [
                {"title": "The Problem", "content": market.get("problem_statement", "Users face significant challenges that existing solutions fail to address adequately"), "speaker_notes": "Lead with emotional story of target user struggling with current solutions"},
                {"title": "Our Solution", "content": f"An AI-powered platform that {idea} — personalized, adaptive, and 10x more effective than alternatives", "speaker_notes": "Demo the core AI workflow live if possible"},
                {"title": "Market Opportunity", "content": f"TAM: {tam_val} | SAM: {_get_claim(market, 'sam', '$2.8B')} | Growing at {_get_claim(market, 'growth_rate', '23% CAGR')}", "speaker_notes": "Emphasize timing — AI adoption inflection point"},
                {"title": "Product", "content": "AI-native platform with personalized engine, real-time analytics, and community features", "speaker_notes": "Show product screenshots and user flow"},
                {"title": "Business Model", "content": f"Freemium SaaS: Free -> Pro ($9.99) -> Premium ($19.99) -> Enterprise ($5/user). LTV:CAC = {ratio_str}", "speaker_notes": "Highlight unit economics strength"},
                {"title": "Traction & Roadmap", "content": "MVP in 12 weeks | Target beta with 500 users | Projected path to $480K ARR year 1", "speaker_notes": "Show development timeline and future target milestones"},
                {"title": "Competitive Advantage", "content": "AI-native architecture powered by NVIDIA NeMo — not bolted-on AI but built from the ground up", "speaker_notes": "Differentiate from incumbents adding AI as feature"},
                {"title": "The Team", "content": "Founding team with AI/ML expertise and domain knowledge", "speaker_notes": "Highlight relevant experience and advisory board"},
                {"title": "The Ask", "content": "Raising $1.5M Seed round for 18-month runway to reach Series A metrics", "speaker_notes": "Clear use of funds breakdown"},
            ],
            "funding_strategy": {
                "stage": "Seed",
                "target_investors": target_investors,
                "timeline": "Begin fundraising after beta launch with initial traction metrics",
                "key_metrics_for_series_a": ["$40K+ MRR", "1000+ active users", "70%+ retention", "Proven unit economics"],
            },
            "funding_ask": {
                "amount": {
                    "claim": "$1.5M",
                    "sources": sources[:1],
                    "confidence": 0.94
                },
                "valuation": {
                    "claim": "$8M pre-money",
                    "sources": sources[1:],
                    "confidence": 0.90
                },
                "use_of_funds": {
                    "engineering": "45%",
                    "marketing_growth": "30%",
                    "operations": "15%",
                    "reserve": "10%",
                },
                "runway_months": {
                    "claim": "18 months",
                    "sources": sources,
                    "confidence": 0.92
                },
                "milestones_with_funding": ["Public launch", "1000 users", "$40K MRR", "Series A ready"],
            },
            "narrative": {
                "claim": f"In a world where target users struggle with outdated solutions, we're building the AI co-pilot that makes {idea} accessible, personalized, and effective for everyone.",
                "sources": sources[:1],
                "confidence": 0.94
            }
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        ask = content.get("funding_ask", {})
        amt_val = ask.get("amount", {})
        amt = amt_val.get("claim", "$1.5M") if isinstance(amt_val, dict) else str(amt_val)
        
        val_val = ask.get("valuation", {})
        val = val_val.get("claim", "$8M pre-money") if isinstance(val_val, dict) else str(val_val)
        
        runway_val = ask.get("runway_months", {})
        runway = runway_val.get("claim", "18 months") if isinstance(runway_val, dict) else str(runway_val)
        
        exec_val = content.get("executive_summary", {})
        exec_summary = exec_val.get("claim", "") if isinstance(exec_val, dict) else str(exec_val)

        return [
            ExplainableInsight(
                recommendation=f"Raise {amt} seed at {val} valuation",
                reasoning=exec_summary,
                data_sources=["market analysis", "business model projections", "comparable startup valuations"],
                confidence=0.80,
                evidence=[f"Runway: {runway}", f"Use of funds: {len(ask.get('use_of_funds', {}))} categories"],
            )
        ]
