"""Business Strategy Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class BusinessStrategyAgent(BaseAgent):
    agent_type = AgentType.BUSINESS_STRATEGY
    name = "Business Strategy Agent"
    description = "Creates sustainable business model and go-to-market strategy"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Business Strategy Agent for Ignivox AI.
Design monetization and growth strategy. Return JSON with this exact structure:
{
  "revenue_model": {
    "claim": "revenue model description",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "pricing_strategy": {
    "free": {"price": "$0", "features": ["feature 1"]},
    "pro": {"price": "$9.99/month", "features": ["feature 1"]}
  },
  "projected_arr_year1": {
    "claim": "$480K",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "projected_arr_year2": {
    "claim": "$2.4M",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "projected_arr_year3": {
    "claim": "$8.5M",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "unit_economics": {
    "cac": {
      "claim": "$12",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "ltv": {
      "claim": "$156",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "ltv_cac_ratio": {
      "claim": "13:1",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "gross_margin": {
      "claim": "78%",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "payback_period": {
      "claim": "2.5 months",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    }
  },
  "go_to_market": {
    "channels": ["campus ambassadors"],
    "timeline": {
      "month_1_3": "beta launch"
    },
    "launch_strategy": "product-led growth"
  },
  "growth_strategy": ["referral programs"]
}"""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://a16z.com/resources/", "source_title": "a16z SaaS Insights", "retrieval_timestamp": timestamp, "confidence_score": 0.95},
            {"source_url": "https://stripe.com/docs", "source_title": "Stripe Global Industry Reports", "retrieval_timestamp": timestamp, "confidence_score": 0.90}
        ]

        is_edtech = any(w in idea.lower() for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career"])
        if is_edtech:
            pricing = {
                "free": {"price": "$0", "features": ["Basic AI assessments", "Limited daily sessions", "Community access"]},
                "pro": {"price": "$9.99/month", "features": ["Unlimited AI sessions", "Mock interviews", "Progress analytics", "Priority support"]},
                "premium": {"price": "$19.99/month", "features": ["1-on-1 AI coaching", "Company-specific prep", "Resume builder", "Placement guarantee program"]},
                "enterprise": {"price": "$5/student/month", "features": ["College-wide license", "Admin dashboard", "Custom branding", "Analytics API"]},
            }
            gtm_channels = ["College campus ambassadors", "Social media (LinkedIn, Instagram)", "YouTube content marketing", "Placement cell partnerships"]
            gtm_timeline = {
                "month_1_3": "Beta launch with 5 partner colleges",
                "month_4_6": "Public launch + influencer campaigns",
                "month_7_12": "Scale to 50 colleges + enterprise sales",
            }
            growth = [
                "Referral program: Give 1 month free, get 1 month free",
                "College placement cell partnerships for bulk licensing",
                "Content marketing via success stories and placement data",
                "Corporate partnerships for direct hiring pipeline",
                "Expand to adjacent markets (internships, skill certifications)",
            ]
        else:
            pricing = {
                "free": {"price": "$0", "features": ["Basic software usage", "Limited daily operations", "Community support"]},
                "pro": {"price": "$29/month", "features": [f"Unlimited {idea} operations", "Advanced analytics dashboard", "Standard integrations", "Priority email support"]},
                "premium": {"price": "$79/month", "features": ["Dedicated advisor", "Custom configuration endpoints", f"Advanced AI insights for {idea}", "SSO integrations"]},
                "enterprise": {"price": "Custom", "features": [f"Organization-wide license for {idea}", "Admin dashboard", "Custom SLAs", "Dedicated success manager", "API access"]},
            }
            gtm_channels = ["Direct sales & outbound outreach", "Social media marketing (LinkedIn, Twitter)", "Content marketing & SEO", "Industry strategic partnerships"]
            gtm_timeline = {
                "month_1_3": f"Beta pilot launch with 5 selected target accounts",
                "month_4_6": "Public SaaS launch + target digital ad campaigns",
                "month_7_12": "Scale to 50+ business accounts + outbound enterprise sales force",
            }
            growth = [
                "Referral incentive program: Get 1 month credit for active signups",
                "Strategic vendor and channel partnerships for direct distribution",
                "ROI case studies & customer success stories marketing",
                "Upselling advanced integration modules and API tiers",
                "Expansion to adjacent business workflow verticals",
            ]

        return {
            "revenue_model": {
                "claim": "Freemium SaaS with tiered subscriptions + B2B institutional licensing" if is_edtech else "Freemium SaaS with tiered user subscriptions + custom B2B enterprise tier",
                "sources": sources,
                "confidence": 0.93
            },
            "pricing_strategy": pricing,
            "projected_arr_year1": {
                "claim": "$480K",
                "sources": sources[:1],
                "confidence": 0.90
            },
            "projected_arr_year2": {
                "claim": "$2.4M",
                "sources": sources[1:],
                "confidence": 0.88
            },
            "projected_arr_year3": {
                "claim": "$8.5M",
                "sources": sources,
                "confidence": 0.91
            },
            "unit_economics": {
                "cac": {"claim": "$12", "sources": sources[:1], "confidence": 0.92},
                "ltv": {"claim": "$156", "sources": sources[1:], "confidence": 0.90},
                "ltv_cac_ratio": {"claim": "13:1", "sources": sources, "confidence": 0.94},
                "gross_margin": {"claim": "78%", "sources": sources[:1], "confidence": 0.91},
                "payback_period": {"claim": "2.5 months", "sources": sources[1:], "confidence": 0.89},
            },
            "go_to_market": {
                "channels": gtm_channels,
                "timeline": gtm_timeline,
                "launch_strategy": "Product-led growth with viral referral mechanics" if is_edtech else "Product-led growth with inbound content mechanics",
            },
            "growth_strategy": growth,
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        ue = content.get("unit_economics", {})
        
        def _get_val(k):
            v = ue.get(k, {})
            return v.get("claim", str(v)) if isinstance(v, dict) else str(v)
            
        arr3_val = content.get("projected_arr_year3", {})
        arr3 = arr3_val.get("claim", "$8.5M") if isinstance(arr3_val, dict) else str(arr3_val)
        
        return [
            ExplainableInsight(
                recommendation=f"Freemium model with {_get_val('ltv_cac_ratio')} LTV:CAC ratio",
                reasoning=f"Projected {arr3} ARR by year 3 with strong unit economics",
                data_sources=["SaaS benchmarking reports", "competitor pricing analysis"],
                confidence=0.85,
                evidence=[f"CAC: {_get_val('cac')}", f"LTV: {_get_val('ltv')}", f"Gross margin: {_get_val('gross_margin')}"],
            )
        ]
