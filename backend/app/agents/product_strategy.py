"""Product Strategy Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class ProductStrategyAgent(BaseAgent):
    agent_type = AgentType.PRODUCT_STRATEGY
    name = "Product Strategy Agent"
    description = "Designs product vision, MVP scope, and feature roadmap"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Product Strategy Agent for Ignivox AI.
Define product vision and MVP. Return JSON with this exact structure:
{
  "product_vision": {
    "claim": "vision statement",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "core_features": [
    {
      "claim": "feature description",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    }
  ],
  "mvp_definition": {
    "features": [
      {
        "claim": "MVP feature",
        "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
        "confidence": 0.90
      }
    ],
    "timeline": {
      "claim": "8-12 weeks",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "success_metrics": [
      {
        "claim": "success metric",
        "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
        "confidence": 0.90
      }
    ],
    "out_of_scope": ["out of scope item"]
  },
  "feature_roadmap": [
    {"phase": "MVP (Month 1-3)", "features": ["Core AI engine"]}
  ],
  "user_personas": [
    {"name": "Persona Name", "age": "25", "goals": "goals description", "pain": "pain description"}
  ],
  "value_proposition": {
    "claim": "value proposition statement",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  }
}"""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://productschool.com/resources", "source_title": "Product School Resources", "retrieval_timestamp": timestamp, "confidence_score": 0.95},
            {"source_url": "https://www.pragmaticinstitute.com/resources", "source_title": "Pragmatic Institute", "retrieval_timestamp": timestamp, "confidence_score": 0.90}
        ]

        is_edtech = any(w in idea.lower() for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career"])
        if is_edtech:
            user_personas = [
                {"name": "Alex the Ambitious Student", "age": "20", "goals": f"Excel in topics related to {idea}", "pain": f"Overwhelmed by study materials for {idea}"},
                {"name": "Sarah the Career Switcher", "age": "28", "goals": f"Transition to tech or professional role using {idea}", "pain": "Gap in structured learning path for this domain"},
            ]
        else:
            user_personas = [
                {"name": "Alex the Professional", "age": "29", "goals": f"Optimize workflow efficiency and automate tasks using {idea}", "pain": f"High manual effort and slow processing in current tools for {idea}"},
                {"name": "Sarah the Manager", "age": "34", "goals": f"Coordinate team operations and maintain quality for {idea}", "pain": f"Fragmented data systems and lack of real-time insights"},
            ]

        return {
            "product_vision": {
                "claim": f"Transform how users experience {idea} through intelligent, adaptive AI that learns and improves with every interaction",
                "sources": sources,
                "confidence": 0.93
            },
            "core_features": [
                {"claim": f, "sources": sources[:1], "confidence": 0.91}
                for f in [
                    "AI-powered personalized dashboard",
                    "Adaptive learning/recommendation engine",
                    "Real-time progress analytics",
                    "Community collaboration hub",
                    "Smart notification and reminder system",
                    "Integration API for third-party tools",
                ]
            ],
            "mvp_definition": {
                "features": [
                    {"claim": f, "sources": sources[:1], "confidence": 0.90}
                    for f in [
                        "User onboarding with AI assessment",
                        "Core AI recommendation engine",
                        "Progress tracking dashboard",
                        "Basic analytics and reporting",
                        "Mobile-responsive web app",
                    ]
                ],
                "timeline": {
                    "claim": "8-12 weeks",
                    "sources": sources[1:],
                    "confidence": 0.92
                },
                "success_metrics": [
                    {"claim": m, "sources": sources, "confidence": 0.89}
                    for m in [
                        "500 beta users in first month",
                        "70% weekly retention rate",
                        "NPS score above 40",
                        "Average session duration > 15 minutes",
                    ]
                ],
                "out_of_scope": ["Native mobile apps", "Enterprise SSO", "Advanced API marketplace"],
            },
            "feature_roadmap": [
                {"phase": "MVP (Month 1-3)", "features": ["Core AI engine", "Dashboard", "User auth", "Basic analytics"]},
                {"phase": "Growth (Month 4-6)", "features": ["Mobile app", "Social features", "Premium tier", "Integrations"]},
                {"phase": "Scale (Month 7-12)", "features": ["Enterprise features", "API platform", "International", "AI coaching"]},
            ],
            "user_personas": user_personas,
            "value_proposition": {
                "claim": "Your AI co-pilot that creates a personalized path to success — adapting to your pace, identifying gaps, and accelerating results",
                "sources": sources,
                "confidence": 0.94
            },
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        if not isinstance(content, dict):
            return []

        mvp = content.get("mvp_definition", {})
        if not isinstance(mvp, dict):
            mvp = {}
        timeline_val = mvp.get("timeline", {})
        timeline = timeline_val.get("claim", "8-12 weeks") if isinstance(timeline_val, dict) else str(timeline_val)
        
        features = mvp.get("features", [])
        metrics = mvp.get("success_metrics", [])
        if not isinstance(features, list):
            features = []
        if not isinstance(metrics, list):
            metrics = []
        evidence = [m.get("claim", str(m)) if isinstance(m, dict) else str(m) for m in metrics[:2]]
        
        return [
            ExplainableInsight(
                recommendation=f"Launch MVP in {timeline} with {len(features)} core features",
                reasoning="Focused MVP reduces time-to-market while validating core value proposition",
                data_sources=["product strategy framework", "competitor feature analysis"],
                confidence=0.88,
                evidence=evidence,
            )
        ]
