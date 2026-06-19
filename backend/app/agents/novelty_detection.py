"""Novelty Detection and Sizing Classification Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class NoveltyDetectionAgent(BaseAgent):
    agent_type = AgentType.NOVELTY_DETECTION
    name = "Novelty Detection Agent"
    description = "Classifies market maturity and detects speculative startup elements"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Novelty Detection Agent for Ignivox AI.
Your job is to analyze the startup idea and evaluate how novel, speculative, or established the market is.
Evaluate if there are existing commercial solutions, if it relies on unproven/frontier tech (like autonomous multi-agent operational systems), or if it is a standard business model.

Return JSON with this exact structure:
{
  "market_classification": "Established Market / Emerging Market / Frontier / Speculative Market",
  "novelty_score": 85, // integer 0-100. Higher means more speculative, novel, or frontier.
  "evidence_coverage_est": 0.30, // estimated percentage (0.0 to 1.0) of public commercial data/evidence available.
  "speculative_content_ratio": 0.70, // estimated percentage (0.0 to 1.0) of the business model that relies on assumptions or hypotheses rather than established historical facts.
  "key_hypotheses": [
    "Key speculative hypothesis 1",
    "Key speculative hypothesis 2"
  ],
  "rationale": "Detailed logical explanation of your classification and sizing assessment."
}

SCORING RULES FOR MARKET TYPES:
1. Established Market (0-35 Score): Highly standardized solutions, mature sectors, lots of public documentation (e.g. traditional CRM, simple task tracker, standard LMS).
2. Emerging Market (35-70 Score): Growing segment with existing reference benchmarks but introducing new methodologies or AI-native extensions (e.g. college agentic operating system, AI SMB employees, AI infrastructure monitoring, automated AIOps, predictive maintenance).
3. Frontier / Speculative Market (70-100 Score): Unproven commercial feasibility, no direct production predecessors, high reliance on future technological breakthroughs (e.g. Brain-Computer cloud, fusion reactor AI, Mars infrastructure swarms).

CRITICAL SCORE RULES:
- AI operations, infrastructure monitoring, predictive analytics, enterprise SaaS, and generic developer tools are EMERGING, not Frontier. They must be scored in the 35-70 range.
- Do NOT classify any idea as Frontier unless it requires a fundamental scientific breakthrough (e.g. quantum brain interfaces, clean nuclear fusion, interplanetary transport swarms).
"""

    # NOTE FOR CONTRIBUTORS:
    # - Demo Mode uses dynamic keyword-based sizing heuristics (implemented below)
    #   solely to avoid producing identical mock outputs for different demo runs.
    # - Live Mode performs actual evidence-based calculations derived directly
    #   from retrieved RAG research sources processed by NVIDIA NIM.

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        idea_lower = idea.lower()
        if any(w in idea_lower for w in ["fusion", "quantum", "space", "mars", "brain", "bci", "telepathy"]):
            novelty_score = 88
            market_classification = "Frontier / Speculative Market"
            evidence_coverage_est = 0.25
            speculative_ratio = 0.75
            hypotheses = [
                f"It is scientifically and commercially feasible to implement {idea}",
                "Target industries are willing to adopt unproven frontier methods over established processes",
                "Integrations with complex hardware or specialized architectures can scale efficiently"
            ]
            rationale = f"High novelty due to the deep technology requirements and significant scientific uncertainty associated with {idea}."
        elif any(w in idea_lower for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career"]):
            novelty_score = 65
            market_classification = "Emerging Market"
            evidence_coverage_est = 0.60
            speculative_ratio = 0.40
            hypotheses = [
                "AI-driven personalization yields measurable learning or career readiness improvements compared to static methods",
                "Educational institutions or learners will partner with early-stage AI co-pilot tools"
            ]
            rationale = f"AI-based educational tools for '{idea}' represent an emerging market with growing digital adoption and personalized training workflows."
        elif any(w in idea_lower for w in ["monitoring", "infrastructure", "telemetry", "maintenance", "sensor", "scada", "iot"]):
            novelty_score = 65
            market_classification = "Emerging Market"
            evidence_coverage_est = 0.60
            speculative_ratio = 0.40
            hypotheses = [
                "Predictive models can ingest real-time IoT/telemetry data streams without introducing excessive latency",
                "Operators will trust autonomous AI system insights to modify controls or setpoints"
            ]
            rationale = f"AI-driven telemetry monitoring and predictive maintenance for '{idea}' are emerging segments with high data volume requirements and growing automation."
        else:
            novelty_score = 25
            market_classification = "Established Market"
            evidence_coverage_est = 0.85
            speculative_ratio = 0.15
            hypotheses = [
                f"AI-assisted workflow automation for {idea} reduces manual operational time by more than 20%"
            ]
            rationale = "General SaaS workflow tooling sits in a highly defined, mature market with numerous comparable benchmark references."

        return {
            "market_classification": market_classification,
            "novelty_score": novelty_score,
            "evidence_coverage_est": evidence_coverage_est,
            "speculative_content_ratio": speculative_ratio,
            "key_hypotheses": hypotheses,
            "rationale": rationale
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        score = content.get("novelty_score", 50)
        market_type = content.get("market_classification", "Emerging Market")
        
        return [
            ExplainableInsight(
                recommendation=f"Classified as {market_type} (Novelty Score: {score}/100)",
                reasoning=content.get("rationale", "Market maturity classification complete."),
                data_sources=["market databases", "patent filings", "NIM reasoning agent"],
                confidence=0.90,
                evidence=content.get("key_hypotheses", [])[:2],
            )
        ]
