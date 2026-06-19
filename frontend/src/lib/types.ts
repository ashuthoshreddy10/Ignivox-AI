export interface SourceInfo {
  source_url: string;
  source_title: string;
  retrieval_timestamp: string;
  confidence_score: number;
}

export interface GroundedClaim {
  claim: string;
  sources: SourceInfo[];
  confidence: number;
  retrieval_status: string;
  claim_type: string;
  verification: string;
  source_count: number;
  evidence_strength: string;
}

export interface EvidenceQualityReport {
  evidence_quality_score: number;
  total_claims_verified: number;
  unsupported_claims_count: number;
  trusted_sources_count: number;
  quality_summary: string;
  verified_claims: Array<{
    agent: string;
    claim: string;
    status: string;
    source: string;
    confidence: number;
    retrieval_status: string;
    claim_type: string;
    verification: string;
    sources: SourceInfo[];
    source_count: number;
    evidence_strength: string;
  }>;
}

export interface ExplainableInsight {
  recommendation: string;
  reasoning: string;
  data_sources: string[];
  confidence: number;
  evidence: string[];
}

export interface AgentOutput {
  agent: string;
  status: string;
  title: string;
  content: Record<string, unknown>;
  insights: ExplainableInsight[];
  confidence: number;
  duration_ms: number;
}

export interface ScoreBreakdown {
  market_potential: number;
  revenue_potential: number;
  technical_feasibility: number;
  scalability: number;
  competition_intensity: number;
  overall: number;
}

export interface StartupBlueprint {
  id: string;
  idea: string;
  created_at: string;
  workflow_plan: {
    idea: string;
    steps: Array<{ step: number; agent: string; task: string; depends_on: string[] }>;
    agent_assignments: Record<string, string>;
    estimated_duration_minutes: number;
  };
  novelty_detection?: AgentOutput;
  market_research?: AgentOutput;
  competitor_analysis?: AgentOutput;
  product_strategy?: AgentOutput;
  business_strategy?: AgentOutput;
  technical_architecture?: AgentOutput;
  execution_plan?: AgentOutput;
  investor_pitch?: AgentOutput;
  validation?: AgentOutput;
  score?: ScoreBreakdown;
  recommendations?: ExplainableInsight[];
  evidence_quality_report?: EvidenceQualityReport;
  confidence_scores?: Record<string, number>;
  status: string;
}

export interface WorkflowEvent {
  type: string;
  agent?: string;
  status?: string;
  message: string;
  progress: number;
  data?: Record<string, unknown>;
  timestamp: string;
}

export interface AgentInfo {
  type: string;
  name: string;
  description: string;
  status: string;
}

export const AGENT_COLORS: Record<string, string> = {
  orchestrator: '#22c55e',
  novelty_detection: '#6366f1',
  market_research: '#3b82f6',
  competitor: '#f59e0b',
  product_strategy: '#8b5cf6',
  business_strategy: '#ec4899',
  technical_architect: '#06b6d4',
  execution_planning: '#f97316',
  investor_pitch: '#eab308',
  validation: '#10b981',
};

export const AGENT_LABELS: Record<string, string> = {
  orchestrator: 'Orchestrator',
  novelty_detection: 'Novelty Detection',
  market_research: 'Market Research',
  competitor: 'Competitor Intel',
  product_strategy: 'Product Strategy',
  business_strategy: 'Business Strategy',
  technical_architect: 'Tech Architect',
  execution_planning: 'Execution Plan',
  investor_pitch: 'Investor Pitch',
  validation: 'Validation',
};
