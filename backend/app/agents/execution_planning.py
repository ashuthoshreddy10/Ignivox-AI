"""Execution Planning Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class ExecutionPlanningAgent(BaseAgent):
    agent_type = AgentType.EXECUTION_PLANNING
    name = "Execution Planning Agent"
    description = "Transforms plans into actionable development roadmap"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Execution Planning Agent for Ignivox AI.
Create actionable development and launch plans. Return JSON with this exact structure:
{
  "roadmap_summary": {
    "claim": "12-week agile development plan consisting of 6 two-week sprints",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "sprint_roadmap": [
    {"sprint": 1, "duration": "2 weeks", "focus": "Foundation", "deliverables": ["Project setup", "Auth system", "Database schema", "CI/CD pipeline"]},
    {"sprint": 2, "duration": "2 weeks", "focus": "Core AI", "deliverables": ["NIM integration", "Agent orchestrator", "Basic RAG pipeline", "WebSocket streaming"]}
  ],
  "milestones": [
    {"name": "MVP Alpha", "date": "Week 6", "criteria": "Core workflow generates blueprint end-to-end"}
  ],
  "launch_timeline_summary": {
    "claim": "12-week launch schedule covering pre-launch prep, Product Hunt launch week, and post-launch iteration",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.85}],
    "confidence": 0.85
  },
  "launch_timeline": {
    "pre_launch": {"weeks": "1-2", "activities": ["Beta user recruitment", "Landing page", "Social media setup"]},
    "launch_week": {"activities": ["Product Hunt launch", "Press release", "Influencer outreach"]},
    "post_launch": {"weeks": "1-4", "activities": ["User feedback iteration", "Performance monitoring"]}
  },
  "team_requirements": {
    "claim": "Immediate hiring of lead engineer, ML developer, frontend dev, and designer",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  },
  "launch_checklist": [
    "Production environment configured",
    "Security audit completed"
  ],
  "risk_mitigation": [
    {"risk": "NIM API latency", "mitigation": "Response caching + async processing with progress updates"}
  ]
}"""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        is_edtech = any(w in idea.lower() for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career"])
        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://www.atlassian.com/agile/scrum", "source_title": "Atlassian Scrum Guide", "retrieval_timestamp": timestamp, "confidence_score": 0.95},
            {"source_url": "https://www.ycombinator.com/library", "source_title": "Y Combinator Startup Library", "retrieval_timestamp": timestamp, "confidence_score": 0.90}
        ]

        return {
            "roadmap_summary": {
                "claim": "12-week agile development plan consisting of 6 targeted two-week sprints to construct the MVP",
                "sources": sources[:1],
                "confidence": 0.92
            },
            "sprint_roadmap": [
                {"sprint": 1, "duration": "2 weeks", "focus": "Foundation", "deliverables": ["Project setup", "Auth system", "Database schema", "CI/CD pipeline"]},
                {"sprint": 2, "duration": "2 weeks", "focus": "Core AI", "deliverables": ["NIM integration", "Agent orchestrator", "Basic RAG pipeline", "WebSocket streaming"]},
                {"sprint": 3, "duration": "2 weeks", "focus": "Agents", "deliverables": ["All 8 specialized agents", "Workflow engine", "Guardrails integration", "Memory system"]},
                {"sprint": 4, "duration": "2 weeks", "focus": "Frontend", "deliverables": ["Dashboard UI", "Agent graph visualization", "Blueprint workspace", "Real-time progress"]},
                {"sprint": 5, "duration": "2 weeks", "focus": "Polish", "deliverables": ["Scoring engine", "Multi-idea comparison", "Investor mode", "Beta testing"]},
                {"sprint": 6, "duration": "2 weeks", "focus": "Launch", "deliverables": ["Performance optimization", "Security audit", "Documentation", "Public launch"]},
            ],
            "milestones": [
                {"name": "MVP Alpha", "date": "Week 6", "criteria": "Core workflow generates blueprint end-to-end"},
                {"name": "Beta Launch", "date": "Week 10", "criteria": "50 beta users, all agents operational"},
                {"name": "Public Launch", "date": "Week 12", "criteria": "Production deployment, marketing live"},
                {"name": "Series A Ready", "date": "Month 6", "criteria": "1000 users, $40K MRR, pitch deck validated"},
            ],
            "launch_timeline_summary": {
                "claim": "Pre-launch preparation across weeks 1-2, Product Hunt launch during week 3, followed by a 4-week iteration phase",
                "sources": sources[1:],
                "confidence": 0.89
            },
            "launch_timeline": {
                "pre_launch": {"weeks": "1-2", "activities": ["Beta user recruitment", "Landing page", "Social media setup"]},
                "launch_week": {"activities": ["Product Hunt launch", "Press release", "Influencer outreach", "College ambassador activation" if is_edtech else "Targeted customer demo days"]},
                "post_launch": {"weeks": "1-4", "activities": ["User feedback iteration", "Performance monitoring", "Feature prioritization from analytics"]},
            },
            "team_requirements": {
                "claim": "4 immediate engineering hires (Full-stack lead, AI/ML engineer, Frontend dev, Product designer), scaling with 3 strategic hires by month 3",
                "sources": sources,
                "confidence": 0.91
            },
            "launch_checklist": [
                "Production environment configured",
                "NVIDIA API keys and rate limits set",
                "Security audit completed",
                "Privacy policy and ToS published",
                "Analytics and error tracking live",
                "Customer support channel ready",
                "Payment processing integrated",
                "Beta feedback incorporated",
            ],
            "risk_mitigation": [
                {"risk": "NIM API latency", "mitigation": "Response caching + async processing with progress updates"},
                {"risk": "Low initial user adoption", "mitigation": "College ambassador program + free tier" if is_edtech else "Incentive-based referral program + free trial tier"},
                {"risk": "Agent output quality", "mitigation": "NeMo Guardrails + validation agent + human-in-the-loop"},
            ],
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        sprints = content.get("sprint_roadmap", [])
        milestones = content.get("milestones", [])
        evidence = [
            m.get("name", str(m)) if isinstance(m, dict) else str(m)
            for m in milestones
        ]
        
        roadmap = content.get("roadmap_summary", {})
        roadmap_claim = roadmap.get("claim", f"{len(sprints)}-sprint roadmap") if isinstance(roadmap, dict) else str(roadmap)
        
        return [
            ExplainableInsight(
                recommendation=f"Execute roadmap: {roadmap_claim}",
                reasoning="Phased approach de-risks development with clear milestones and deliverables",
                data_sources=["agile development best practices", "startup launch playbooks"],
                confidence=0.87,
                evidence=evidence,
            )
        ]
