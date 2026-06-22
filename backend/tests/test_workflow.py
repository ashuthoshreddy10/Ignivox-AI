"""Unit tests for multi-agent workflow orchestration engine."""

import pytest
import asyncio
from app.models.schemas import GenerateRequest, AgentType, AgentStatus
from app.orchestration.workflow import orchestrator
from app.config import settings

@pytest.mark.anyio
async def test_workflow_orchestrator_generate_demo_mode():
    # Force demo mode to run local mock data and avoid remote API calls
    original_demo_mode = settings.demo_mode
    settings.demo_mode = True
    
    try:
        request = GenerateRequest(
            idea="An AI-powered energy grid management tool for smart dispatching",
            generate_idea=False,
            industry="energy",
            require_approval=False
        )
        
        blueprint = await orchestrator.generate(request)
        
        assert blueprint is not None
        assert blueprint.status == "complete"
        assert blueprint.novelty_detection is not None
        assert blueprint.market_research is not None
        assert blueprint.competitor_analysis is not None
        assert blueprint.product_strategy is not None
        assert blueprint.business_strategy is not None
        assert blueprint.technical_architecture is not None
        assert blueprint.execution_plan is not None
        assert blueprint.investor_pitch is not None
        assert blueprint.validation is not None
        
        # Verify the structure of outputs
        assert blueprint.score is not None
        assert len(blueprint.claim_lineage) >= 0
        
    finally:
        settings.demo_mode = original_demo_mode


@pytest.mark.anyio
async def test_workflow_orchestrator_concurrency_evaluation_context():
    from app.services.evidence_utils import EVALUATED_CLAIMS
    
    # Ensure global list remains clean
    assert len(EVALUATED_CLAIMS) == 0
    
    original_demo_mode = settings.demo_mode
    settings.demo_mode = True
    
    try:
        request1 = GenerateRequest(idea="Idea One: Health tracker SCADA sensor diagnostic app", generate_idea=False, require_approval=False)
        request2 = GenerateRequest(idea="Idea Two: Fintech banking ledger ledger application", generate_idea=False, require_approval=False)
        
        bp1, bp2 = await asyncio.gather(
            orchestrator.generate(request1),
            orchestrator.generate(request2)
        )
        
        # Verify that global list is still empty, meaning session-scoped context was used
        assert len(EVALUATED_CLAIMS) == 0
        assert bp1 is not None and bp2 is not None
        
    finally:
        settings.demo_mode = original_demo_mode

