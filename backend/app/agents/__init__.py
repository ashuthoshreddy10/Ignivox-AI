"""Agent registry."""

from app.agents.base import BaseAgent
from app.agents.business_strategy import BusinessStrategyAgent
from app.agents.competitor import CompetitorAgent
from app.agents.execution_planning import ExecutionPlanningAgent
from app.agents.investor_pitch import InvestorPitchAgent
from app.agents.market_research import MarketResearchAgent
from app.agents.novelty_detection import NoveltyDetectionAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.product_strategy import ProductStrategyAgent
from app.agents.technical_architect import TechnicalArchitectAgent
from app.agents.validation import ValidationAgent
from app.models.schemas import AgentType

AGENT_REGISTRY: dict[AgentType, BaseAgent] = {
    AgentType.ORCHESTRATOR: OrchestratorAgent(),
    AgentType.NOVELTY_DETECTION: NoveltyDetectionAgent(),
    AgentType.MARKET_RESEARCH: MarketResearchAgent(),
    AgentType.COMPETITOR: CompetitorAgent(),
    AgentType.PRODUCT_STRATEGY: ProductStrategyAgent(),
    AgentType.BUSINESS_STRATEGY: BusinessStrategyAgent(),
    AgentType.TECHNICAL_ARCHITECT: TechnicalArchitectAgent(),
    AgentType.EXECUTION_PLANNING: ExecutionPlanningAgent(),
    AgentType.INVESTOR_PITCH: InvestorPitchAgent(),
    AgentType.VALIDATION: ValidationAgent(),
}

AGENT_ORDER = [
    AgentType.ORCHESTRATOR,
    AgentType.NOVELTY_DETECTION,
    AgentType.MARKET_RESEARCH,
    AgentType.COMPETITOR,
    AgentType.PRODUCT_STRATEGY,
    AgentType.BUSINESS_STRATEGY,
    AgentType.TECHNICAL_ARCHITECT,
    AgentType.EXECUTION_PLANNING,
    AgentType.INVESTOR_PITCH,
    AgentType.VALIDATION,
]

AGENT_DEPENDENCIES = {
    AgentType.NOVELTY_DETECTION: [],
    AgentType.MARKET_RESEARCH: [AgentType.NOVELTY_DETECTION],
    AgentType.COMPETITOR: [AgentType.MARKET_RESEARCH],
    AgentType.PRODUCT_STRATEGY: [AgentType.MARKET_RESEARCH, AgentType.COMPETITOR],
    AgentType.BUSINESS_STRATEGY: [AgentType.PRODUCT_STRATEGY],
    AgentType.TECHNICAL_ARCHITECT: [AgentType.PRODUCT_STRATEGY],
    AgentType.EXECUTION_PLANNING: [AgentType.TECHNICAL_ARCHITECT, AgentType.BUSINESS_STRATEGY],
    AgentType.INVESTOR_PITCH: [AgentType.BUSINESS_STRATEGY, AgentType.MARKET_RESEARCH],
    AgentType.VALIDATION: list(AgentType),
}
