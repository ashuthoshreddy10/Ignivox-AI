"""Orchestrator Agent - central workflow coordinator."""

from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class OrchestratorAgent(BaseAgent):
    agent_type = AgentType.ORCHESTRATOR
    name = "Orchestrator Agent"
    description = "Central coordinator of the multi-agent startup analysis workflow"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Orchestrator Agent for Ignivox AI, an autonomous startup co-founder platform.
Your role is to analyze the user's startup idea and create a comprehensive workflow plan.
Break down the objective into subtasks and assign them to specialized agents.
Return JSON with this exact structure:
{
  "workflow_plan": {
    "idea": "the startup idea",
    "steps": [
      {
        "step": 1,
        "agent": "market_research",
        "task": "Analyze market opportunity and TAM/SAM/SOM",
        "depends_on": []
      },
      {
        "step": 2,
        "agent": "competitor",
        "task": "Research competitors and identify gaps",
        "depends_on": ["market_research"]
      },
      {
        "step": 3,
        "agent": "product_strategy",
        "task": "Define MVP and product roadmap",
        "depends_on": ["market_research", "competitor"]
      },
      {
        "step": 4,
        "agent": "business_strategy",
        "task": "Design revenue model and GTM strategy",
        "depends_on": ["product_strategy"]
      },
      {
        "step": 5,
        "agent": "technical_architect",
        "task": "Design system architecture and tech stack",
        "depends_on": ["product_strategy"]
      },
      {
        "step": 6,
        "agent": "execution_planning",
        "task": "Create sprint roadmap and launch timeline",
        "depends_on": ["technical_architect", "business_strategy"]
      },
      {
        "step": 7,
        "agent": "investor_pitch",
        "task": "Generate pitch deck content",
        "depends_on": ["business_strategy", "market_research"]
      },
      {
        "step": 8,
        "agent": "validation",
        "task": "Validate all outputs and assess feasibility",
        "depends_on": ["*"]
      }
    ],
    "agent_assignments": {
      "market_research": "Discover market opportunities and customer pain points",
      "competitor": "Analyze competing solutions and differentiation",
      "product_strategy": "Define product vision and MVP scope",
      "business_strategy": "Create sustainable business model",
      "technical_architect": "Design scalable technical infrastructure",
      "execution_planning": "Transform plans into actionable tasks",
      "investor_pitch": "Create funding-ready presentations",
      "validation": "Ensure quality and accuracy of all outputs"
    },
    "estimated_duration_minutes": 3
  },
  "analysis_summary": "Initiating comprehensive startup analysis...",
  "recommended_focus": ["focus area 1", "focus area 2"]
}

The available agents are: market_research, competitor, product_strategy, business_strategy, technical_architect, execution_planning, investor_pitch, validation.
Make sure the "steps" list contains dictionaries with keys "step", "agent", "task", and "depends_on"."""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "workflow_plan": {
                "idea": idea,
                "steps": [
                    {"step": 1, "agent": "market_research", "task": "Analyze market opportunity and TAM/SAM/SOM", "depends_on": []},
                    {"step": 2, "agent": "competitor", "task": "Research competitors and identify gaps", "depends_on": ["market_research"]},
                    {"step": 3, "agent": "product_strategy", "task": "Define MVP and product roadmap", "depends_on": ["market_research", "competitor"]},
                    {"step": 4, "agent": "business_strategy", "task": "Design revenue model and GTM strategy", "depends_on": ["product_strategy"]},
                    {"step": 5, "agent": "technical_architect", "task": "Design system architecture and tech stack", "depends_on": ["product_strategy"]},
                    {"step": 6, "agent": "execution_planning", "task": "Create sprint roadmap and launch timeline", "depends_on": ["technical_architect", "business_strategy"]},
                    {"step": 7, "agent": "investor_pitch", "task": "Generate pitch deck content", "depends_on": ["business_strategy", "market_research"]},
                    {"step": 8, "agent": "validation", "task": "Validate all outputs and assess feasibility", "depends_on": ["*"]},
                ],
                "agent_assignments": {
                    "market_research": "Discover market opportunities and customer pain points",
                    "competitor": "Analyze competing solutions and differentiation",
                    "product_strategy": "Define product vision and MVP scope",
                    "business_strategy": "Create sustainable business model",
                    "technical_architect": "Design scalable technical infrastructure",
                    "execution_planning": "Transform plans into actionable tasks",
                    "investor_pitch": "Create funding-ready presentations",
                    "validation": "Ensure quality and accuracy of all outputs",
                },
                "estimated_duration_minutes": 3,
            },
            "analysis_summary": f"Initiating comprehensive startup analysis for: {idea}",
            "recommended_focus": ["market validation", "MVP scoping", "competitive differentiation"],
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        return [
            ExplainableInsight(
                recommendation="Execute 8-agent parallel-sequential workflow for comprehensive analysis",
                reasoning="Market research and competitor analysis can inform product strategy; validation runs last to verify consistency",
                data_sources=["workflow orchestration engine", "agent capability matrix"],
                confidence=0.95,
                evidence=[f"Planned {len(content.get('workflow_plan', {}).get('steps', []))} workflow steps"],
            )
        ]
