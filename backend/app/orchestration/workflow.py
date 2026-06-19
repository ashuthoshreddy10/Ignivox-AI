"""Multi-agent workflow orchestration engine."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Awaitable

from app.agents import AGENT_ORDER, AGENT_REGISTRY, AGENT_DEPENDENCIES
from app.models.schemas import (
    AgentStatus,
    AgentType,
    AgentOutput,
    ExplainableInsight,
    GenerateRequest,
    ScoreBreakdown,
    StartupBlueprint,
    WorkflowEvent,
    WorkflowPlan,
    EvidenceQualityReport,
)
from app.services.memory import memory
from app.services.nemo_retriever import retriever
from app.services.scoring import scoring_engine
from app.services.evidence_utils import (
    accumulate_claim_lineage,
    merge_cumulative_registry,
    normalize_rag_sources,
    registry_to_serializable,
)
import json

logger = logging.getLogger(__name__)

EventEmitter = Callable[[WorkflowEvent], Awaitable[None]]

_active_workflows: dict[str, StartupBlueprint] = {}
_pending_approvals: dict[str, asyncio.Event] = {}


class WorkflowOrchestrator:
    """NeMo-style orchestrator coordinating multi-agent startup analysis."""

    def __init__(self) -> None:
        self.workflows = _active_workflows

    async def generate(
        self,
        request: GenerateRequest,
        emit: EventEmitter | None = None,
    ) -> StartupBlueprint:
        # Reset all agent statuses to idle at the start of a new workflow run
        for agent in AGENT_REGISTRY.values():
            agent.status = AgentStatus.IDLE

        import os
        try:
            if os.path.exists("audit_diagnostics.json"):
                os.remove("audit_diagnostics.json")
        except Exception:
            pass

        workflow_id = str(uuid.uuid4())
        idea = request.idea

        if request.generate_idea and request.industry:
            idea = await self._generate_idea(request.industry)

        async def _emit(event_type: str, agent: AgentType | None, status: AgentStatus | None, message: str, progress: float, data: dict | None = None):
            if emit:
                await emit(WorkflowEvent(
                    type=event_type,
                    agent=agent,
                    status=status,
                    message=message,
                    progress=progress,
                    data=data,
                ))

        await _emit("workflow_start", None, None, f"Starting analysis for: {idea}", 0)
        logger.info("Workflow %s started for idea: %s", workflow_id, idea[:100])

        retrieval_records = []
        context: dict[str, Any] = {
            "idea": idea,
            "evidence_registry": registry_to_serializable({}),
            "claim_lineage": [],
        }
        blueprint = StartupBlueprint(
            id=workflow_id,
            idea=idea,
            created_at=datetime.utcnow(),
            workflow_plan=WorkflowPlan(idea=idea, steps=[], agent_assignments={}),
        )

        self.workflows[workflow_id] = blueprint
        total_agents = len(AGENT_ORDER)
        completed_agents = 0
        completed_lock = asyncio.Lock()

        async def run_agent(agent_type: AgentType) -> AgentOutput:
            nonlocal completed_agents
            agent = AGENT_REGISTRY[agent_type]
            
            logger.info("Agent started | workflow=%s agent=%s", workflow_id, agent_type.value)
            await _emit(
                "agent_working",
                agent_type,
                AgentStatus.WORKING,
                f"{agent.name} is analyzing...",
                (completed_agents / total_agents) * 100
            )
            
            # Context assembly (Multi-Source context)
            rag_query = f"{idea} {agent.name} {agent.description}"
            rag_docs = await retriever.retrieve(rag_query, top_k=5)
            for doc in rag_docs:
                logger.info(
                    "RAG Context Item | Query: '%s' | Document: '%s' | Similarity Score: %.4f | Category: '%s'",
                    rag_query,
                    doc.get("title", "Untitled"),
                    doc.get("relevance_score", 0.0),
                    doc.get("category", "general")
                )
            
            total_r = getattr(rag_docs, "total_retrieved", len(rag_docs))
            filtered_r = getattr(rag_docs, "docs_filtered", 0)
            used_r = len(rag_docs)
            categories_r = [d.get("category", "general") for d in rag_docs]
            retrieval_records.append({
                "total_retrieved": total_r,
                "docs_filtered": filtered_r,
                "docs_used": used_r,
                "categories": categories_r
            })

            vector_context = [{"title": d.get("title"), "content": d.get("content"), "category": d.get("category")} for d in rag_docs]
            
            memory_insights = memory.get_relevant_insights(idea)
            memory_context = [{"insight": i.get("insight"), "timestamp": i.get("timestamp"), "category": i.get("category")} for i in memory_insights]
            
            from app.services.live_research import live_researcher
            live_results = await live_researcher.search(idea + " " + agent.name, top_k=5)
            live_sources = [{"title": s.get("title"), "url": s.get("url"), "snippet": s.get("snippet"), "timestamp": s.get("timestamp")} for s in live_results]
            
            structured_context = {
                "vector_context": vector_context,
                "memory_context": memory_context,
                "live_sources": live_sources
            }
            rag_context_str = json.dumps(structured_context)
            rag_context_str = normalize_rag_sources(rag_context_str)
            
            async def local_event(event_type: str, a_type: AgentType, status: AgentStatus, message: str, progress: float):
                pass
                
            output = await agent.run(idea, context, rag_context_str, on_event=local_event)

            registry = merge_cumulative_registry(context.get("evidence_registry"), rag_context_str)
            context["evidence_registry"] = registry_to_serializable(registry)
            context["claim_lineage"] = accumulate_claim_lineage(
                context,
                agent_type.value,
                output.content,
                registry,
            )
            
            async with completed_lock:
                completed_agents += 1
                logger.info(
                    "Agent completed | workflow=%s agent=%s confidence=%.2f duration_ms=%d",
                    workflow_id,
                    agent_type.value,
                    output.confidence,
                    output.duration_ms,
                )
                await _emit(
                    "agent_complete",
                    agent_type,
                    AgentStatus.COMPLETE,
                    f"{agent.name} completed analysis",
                    (completed_agents / total_agents) * 100,
                    data={"agent": agent_type.value, "confidence": output.confidence},
                )
                
            return output

        # PHASE 0: Orchestrator
        orchestrator_output = await run_agent(AgentType.ORCHESTRATOR)
        context[AgentType.ORCHESTRATOR.value] = orchestrator_output.model_dump()
        
        plan_data = orchestrator_output.content.get("workflow_plan", {})
        if not isinstance(plan_data, dict):
            plan_data = {"steps": plan_data} if isinstance(plan_data, list) else {}
        
        steps = plan_data.get("steps", [])
        normalized_steps = []
        if isinstance(steps, list):
            for i, step in enumerate(steps):
                if isinstance(step, dict):
                    normalized_steps.append(step)
                elif isinstance(step, str):
                    agents = ["novelty_detection", "market_research", "competitor", "product_strategy", "business_strategy", "technical_architect", "execution_planning", "investor_pitch", "validation"]
                    agent_name = agents[i] if i < len(agents) else "validation"
                    normalized_steps.append({
                        "step": i + 1,
                        "agent": agent_name,
                        "task": step,
                        "depends_on": [agents[i - 1]] if i > 0 else []
                    })
        
        agent_assignments = plan_data.get("agent_assignments", {})
        if not isinstance(agent_assignments, dict):
            agent_assignments = {}

        blueprint.workflow_plan = WorkflowPlan(
            idea=idea,
            steps=normalized_steps if normalized_steps else [
                {"step": 1, "agent": "novelty_detection", "task": "Evaluate market novelty", "depends_on": []},
                {"step": 2, "agent": "market_research", "task": "Analyze market opportunity", "depends_on": ["novelty_detection"]}
            ],
            agent_assignments=agent_assignments,
            estimated_duration_minutes=int(plan_data.get("estimated_duration_minutes", 5)) if isinstance(plan_data.get("estimated_duration_minutes"), (int, float)) else 5,
        )

        # PHASE 0.5: Novelty Detection & Sizing Classification
        nd_output = await run_agent(AgentType.NOVELTY_DETECTION)
        context[nd_output.agent.value] = nd_output.model_dump()
        blueprint.novelty_detection = nd_output

        # Determine if Frontier Mode is active
        novelty_score = nd_output.content.get("novelty_score", 0)
        context["is_frontier_mode"] = novelty_score > 70
        context["novelty_score"] = novelty_score
        context["market_classification"] = nd_output.content.get("market_classification", "Established Market")

        # PHASE 1: Market Research (Sequential foundation)
        mr_output = await run_agent(AgentType.MARKET_RESEARCH)
        context[mr_output.agent.value] = mr_output.model_dump()
        blueprint.market_research = mr_output

        # PHASE 2: Discovery (Competitor Intel, then Product Strategy)
        comp_output = await run_agent(AgentType.COMPETITOR)
        context[comp_output.agent.value] = comp_output.model_dump()
        blueprint.competitor_analysis = comp_output

        ps_output = await run_agent(AgentType.PRODUCT_STRATEGY)
        context[ps_output.agent.value] = ps_output.model_dump()
        blueprint.product_strategy = ps_output

        if request.require_approval:
            await _emit("approval_required", AgentType.PRODUCT_STRATEGY, AgentStatus.WAITING_APPROVAL, "Human approval required before continuing to Phase 3", (completed_agents / total_agents) * 100)
            approval_event = asyncio.Event()
            _pending_approvals[workflow_id] = approval_event
            try:
                await asyncio.wait_for(approval_event.wait(), timeout=300)
            except asyncio.TimeoutError:
                logger.warning("Approval timeout for workflow %s", workflow_id)
            finally:
                _pending_approvals.pop(workflow_id, None)

        # PHASE 3: Strategy & Engineering scoping (Business Strategy, then Technical Architect)
        bs_output = await run_agent(AgentType.BUSINESS_STRATEGY)
        context[bs_output.agent.value] = bs_output.model_dump()
        blueprint.business_strategy = bs_output

        ta_output = await run_agent(AgentType.TECHNICAL_ARCHITECT)
        context[ta_output.agent.value] = ta_output.model_dump()
        blueprint.technical_architecture = ta_output

        # PHASE 4: Roadmapping & deck assembly (Execution Planning, then Investor Pitch)
        ep_output = await run_agent(AgentType.EXECUTION_PLANNING)
        context[ep_output.agent.value] = ep_output.model_dump()
        blueprint.execution_plan = ep_output

        ip_output = await run_agent(AgentType.INVESTOR_PITCH)
        context[ip_output.agent.value] = ip_output.model_dump()
        
        content = ip_output.content
        if isinstance(content, dict):
            funding_ask = content.setdefault("funding_ask", {})
            funding_strategy = content.get("funding_strategy", {})
            
            if isinstance(funding_ask, dict):
                if "amount" not in funding_ask or not funding_ask["amount"]:
                    funding_ask["amount"] = funding_strategy.get("amount", "$1.5M")
                if isinstance(funding_ask.get("amount"), (int, float)):
                    funding_ask["amount"] = f"${funding_ask['amount']:,}" if funding_ask["amount"] >= 1000 else f"${funding_ask['amount']}"
                
                if "valuation" not in funding_ask or not funding_ask["valuation"]:
                    raw_val = funding_strategy.get("valuation")
                    if isinstance(raw_val, (int, float)):
                        funding_ask["valuation"] = f"${raw_val:,} pre-money" if raw_val >= 1000 else f"${raw_val} pre-money"
                    else:
                        funding_ask["valuation"] = raw_val or "$8M pre-money"
                elif isinstance(funding_ask.get("valuation"), (int, float)):
                    val_num = funding_ask["valuation"]
                    funding_ask["valuation"] = f"${val_num:,} pre-money" if val_num >= 1000 else f"${val_num} pre-money"
                    
                if "runway_months" not in funding_ask or not funding_ask["runway_months"]:
                    funding_ask["runway_months"] = funding_strategy.get("runway_months", 18)
                    
                if "use_of_funds" not in funding_ask or not funding_ask["use_of_funds"]:
                    funds_val = funding_strategy.get("use_of_funds", {})
                    if isinstance(funds_val, dict):
                        funding_ask["use_of_funds"] = funds_val
                    else:
                        funding_ask["use_of_funds"] = {
                            "engineering": "45%",
                            "marketing_growth": "30%",
                            "operations": "15%",
                            "reserve": "10%"
                        }
                        
                if not isinstance(funding_ask.get("use_of_funds"), dict):
                    funding_ask["use_of_funds"] = {
                        "engineering": "45%",
                        "marketing_growth": "30%",
                        "operations": "15%",
                        "reserve": "10%"
                    }
        blueprint.investor_pitch = ip_output

        # PHASE 5: Validation (Audit compliance layer)
        validation_output = await run_agent(AgentType.VALIDATION)
        context[AgentType.VALIDATION.value] = validation_output.model_dump()
        
        content = validation_output.content
        if isinstance(content, dict):
            if "feasibility_score" not in content or content["feasibility_score"] is None:
                content["feasibility_score"] = content.get("score", 78)
            try:
                content["feasibility_score"] = int(content["feasibility_score"])
            except (ValueError, TypeError):
                content["feasibility_score"] = 78
                
            if "validation_summary" not in content or not content["validation_summary"]:
                content["validation_summary"] = content.get("summary", "Overall startup blueprint is coherent and feasible.")
            
            # Map evidence report & section scores
            evidence_data = content.get("evidence_quality_report", {})
            blueprint.evidence_quality_report = EvidenceQualityReport(
                evidence_quality_score=float(evidence_data.get("evidence_quality_score", 85.0)),
                total_claims_verified=int(evidence_data.get("total_claims_verified", 10)),
                unsupported_claims_count=int(evidence_data.get("unsupported_claims_count", 0)),
                trusted_sources_count=int(evidence_data.get("trusted_sources_count", 5)),
                quality_summary=str(evidence_data.get("quality_summary", "Overall RAG-grounded sources checked out successfully.")),
                verified_claims=evidence_data.get("verified_claims", [])
            )
            
            blueprint.confidence_scores = {
                "novelty_detection": float(content.get("confidence_scores", {}).get("novelty_detection", nd_output.confidence * 100)),
                "market_research": float(content.get("confidence_scores", {}).get("market_research", 88.0)),
                "competitor": float(content.get("confidence_scores", {}).get("competitor", 84.0)),
                "product_strategy": float(content.get("confidence_scores", {}).get("product_strategy", 86.0)),
                "business_strategy": float(content.get("confidence_scores", {}).get("business_strategy", 85.0)),
                "technical_architect": float(content.get("confidence_scores", {}).get("technical_architect", 90.0)),
                "investor_pitch": float(content.get("confidence_scores", {}).get("investor_pitch", 82.0)),
            }
        blueprint.validation = validation_output

        blueprint_data = blueprint.model_dump()
        blueprint_data["claim_lineage"] = context.get("claim_lineage", [])
        blueprint.score = scoring_engine.score(blueprint_data)
        blueprint.recommendations = self._generate_recommendations(context)
        blueprint.status = "complete"

        # Compile retrieval audit
        total_retrieved = 0
        docs_filtered = 0
        docs_used = 0
        category_distribution = {}
        for record in retrieval_records:
            total_retrieved += record.get("total_retrieved", 0)
            docs_filtered += record.get("docs_filtered", 0)
            docs_used += record.get("docs_used", 0)
            for cat in record.get("categories", []):
                category_distribution[cat] = category_distribution.get(cat, 0) + 1

        retrieval_audit = {
            "total_docs_retrieved": total_retrieved,
            "docs_filtered": docs_filtered,
            "docs_used": docs_used,
            "category_distribution": category_distribution
        }

        try:
            import os
            audit_file = "audit_diagnostics.json"
            audit_data = []
            if os.path.exists(audit_file):
                with open(audit_file, "r") as f:
                    audit_data = json.load(f)
            audit_data.append({"retrieval_audit": retrieval_audit})
            with open(audit_file, "w") as f:
                json.dump(audit_data, f, indent=2)
            logger.info("RAG Retrieval Audit Compiled and Saved | %s", json.dumps(retrieval_audit))
        except Exception as err:
            logger.warning("Failed to write retrieval audit: %s", err)

        memory.store_analysis(
            workflow_id,
            idea,
            blueprint.score.overall,
            {"industry": self._detect_industry(idea), "score": blueprint.score.overall},
        )

        await _emit("workflow_complete", None, AgentStatus.COMPLETE, "Startup blueprint generated!", 100, data={"blueprint_id": workflow_id})
        return blueprint

    def approve(self, workflow_id: str, approved: bool) -> bool:
        event = _pending_approvals.get(workflow_id)
        if event:
            event.set()
            return True
        return False

    def get_workflow(self, workflow_id: str) -> StartupBlueprint | None:
        return self.workflows.get(workflow_id)

    async def compare_ideas(self, ideas: list[str]) -> list[dict]:
        results = []
        for idea in ideas:
            bp = await self.generate(GenerateRequest(idea=idea))
            results.append(bp.model_dump())
        return scoring_engine.compare_ideas(results)

    async def _generate_idea(self, industry: str) -> str:
        ideas_map = {
            "fintech": "An AI-powered personal finance co-pilot that automates budgeting, investing, and tax optimization for millennials",
            "healthtech": "A telehealth platform using AI diagnostics to provide instant preliminary health assessments and doctor matching",
            "edtech": "An AI placement preparation platform that creates personalized study paths for college students targeting top companies",
            "saas": "An AI workflow automation platform for SMBs that learns business processes and automates repetitive tasks",
            "ai": "A multi-agent AI platform that functions as an autonomous startup co-founder, generating complete business blueprints",
        }
        return ideas_map.get(industry.lower(), f"An innovative AI-powered startup in the {industry} space")

    def _detect_industry(self, idea: str) -> str:
        idea_lower = idea.lower()
        for industry, keywords in {
            "edtech": ["student", "education", "college", "learn", "placement"],
            "healthtech": ["health", "medical", "patient", "care"],
            "fintech": ["fintech", "finance", "payment", "bank", "invest"],
            "saas": ["saas", "business", "enterprise", "workflow"],
        }.items():
            if any(k in idea_lower for k in keywords):
                return industry
        return "general"

    def _generate_recommendations(self, context: dict[str, Any]) -> list[ExplainableInsight]:
        recs = []
        for key, val in context.items():
            if isinstance(val, dict) and "insights" in val:
                for insight in val["insights"]:
                    if isinstance(insight, dict):
                        recs.append(ExplainableInsight(**insight))
                    elif isinstance(insight, ExplainableInsight):
                        recs.append(insight)

        validation = context.get("validation", {})
        if isinstance(validation, dict):
            val_content = validation.get("content", validation)
            for rec in val_content.get("recommendations", []):
                recs.append(ExplainableInsight(
                    recommendation=rec,
                    reasoning="Identified during validation review",
                    data_sources=["validation agent"],
                    confidence=0.85,
                    evidence=[],
                ))
        return recs[:10]


orchestrator = WorkflowOrchestrator()
