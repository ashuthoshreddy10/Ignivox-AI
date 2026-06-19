from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    COMPLETE = "complete"
    ERROR = "error"
    WAITING_APPROVAL = "waiting_approval"


class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    NOVELTY_DETECTION = "novelty_detection"
    MARKET_RESEARCH = "market_research"
    COMPETITOR = "competitor"
    PRODUCT_STRATEGY = "product_strategy"
    BUSINESS_STRATEGY = "business_strategy"
    TECHNICAL_ARCHITECT = "technical_architect"
    EXECUTION_PLANNING = "execution_planning"
    INVESTOR_PITCH = "investor_pitch"
    VALIDATION = "validation"


class SourceInfo(BaseModel):
    source_url: str
    source_title: str
    retrieval_timestamp: str
    confidence_score: float = Field(default=1.0, ge=0, le=1.0)


class GroundedClaim(BaseModel):
    claim: str
    sources: list[SourceInfo] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0, le=1.0)
    retrieval_status: str = Field(default="success")  # "success" or "failed"
    claim_type: str = Field(default="generated")  # "retrieved" or "generated"
    verification: str = Field(default="unverified")  # "verified" or "unverified"
    source_count: int = Field(default=0)
    evidence_strength: str = Field(default="low")  # "high", "medium", "low"
    category: str = Field(default="Historical Fact")


class EvidenceQualityReport(BaseModel):
    evidence_quality_score: float = Field(default=0.0, ge=0, le=100.0)
    total_claims_verified: int = 0
    unsupported_claims_count: int = 0
    trusted_sources_count: int = 0
    quality_summary: str = ""
    verified_claims: list[dict[str, Any]] = Field(default_factory=list)


class ExplainableInsight(BaseModel):
    recommendation: str
    reasoning: str
    data_sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    agent: AgentType
    status: AgentStatus = AgentStatus.COMPLETE
    title: str
    content: dict[str, Any]
    insights: list[ExplainableInsight] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0, le=1)
    duration_ms: int = 0


class WorkflowPlan(BaseModel):
    idea: str
    steps: list[dict[str, Any]]
    agent_assignments: dict[str, str]
    estimated_duration_minutes: int = 5


class ScoreBreakdown(BaseModel):
    market_potential: float = Field(ge=0, le=100)
    revenue_potential: float = Field(ge=0, le=100)
    technical_feasibility: float = Field(ge=0, le=100)
    scalability: float = Field(ge=0, le=100)
    competition_intensity: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)


class StartupBlueprint(BaseModel):
    id: str
    idea: str
    created_at: datetime
    workflow_plan: WorkflowPlan
    novelty_detection: AgentOutput | None = None
    market_research: AgentOutput | None = None
    competitor_analysis: AgentOutput | None = None
    product_strategy: AgentOutput | None = None
    business_strategy: AgentOutput | None = None
    technical_architecture: AgentOutput | None = None
    execution_plan: AgentOutput | None = None
    investor_pitch: AgentOutput | None = None
    validation: AgentOutput | None = None
    score: ScoreBreakdown | None = None
    recommendations: list[ExplainableInsight] = Field(default_factory=list)
    evidence_quality_report: EvidenceQualityReport | None = None
    confidence_scores: dict[str, float] | None = None
    status: str = "in_progress"


class WorkflowEvent(BaseModel):
    type: str
    agent: AgentType | None = None
    status: AgentStatus | None = None
    message: str
    progress: float = Field(default=0, ge=0, le=100)
    data: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GenerateRequest(BaseModel):
    idea: str = Field(..., min_length=5, max_length=2000)
    generate_idea: bool = False
    industry: str | None = None
    require_approval: bool = False


class CompareRequest(BaseModel):
    ideas: list[str] = Field(..., min_length=2, max_length=5)


class ApprovalRequest(BaseModel):
    workflow_id: str
    approved: bool
    feedback: str | None = None


class AgentState(BaseModel):
    agent: AgentType
    status: AgentStatus
    current_task: str | None = None
    progress: float = 0
    last_output: str | None = None
