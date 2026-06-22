"""FastAPI routes for Ignivox AI."""

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.schemas import (
    AgentState,
    AgentStatus,
    AgentType,
    ApprovalRequest,
    CompareRequest,
    GenerateRequest,
    WorkflowEvent,
)
from app.orchestration.workflow import orchestrator
from app.services.memory import memory
from app.agents import AGENT_REGISTRY, AGENT_ORDER

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    from app.services.nemo_retriever import retriever
    return {
        "status": "healthy",
        "service": "Ignivox AI",
        "nvidia_mode": settings.use_nvidia,
        "demo_mode": settings.demo_mode,
        "agents": len(AGENT_REGISTRY),
        "retriever_mode": retriever.retriever_mode,
    }


@router.get("/agents")
async def list_agents():
    agents = []
    for agent_type in AGENT_ORDER:
        agent = AGENT_REGISTRY[agent_type]
        agents.append({
            "type": agent_type.value,
            "name": agent.name,
            "description": agent.description,
            "status": agent.status.value,
        })
    return {"agents": agents}


@router.get("/agents/status")
async def agent_status():
    states = []
    for agent_type in AGENT_ORDER:
        agent = AGENT_REGISTRY[agent_type]
        states.append(AgentState(
            agent=agent_type,
            status=agent.status,
            current_task=agent.description if agent.status == AgentStatus.WORKING else None,
        ))
    return {"states": [s.model_dump() for s in states]}


@router.post("/generate")
async def generate_blueprint(request: GenerateRequest):
    try:
        blueprint = await orchestrator.generate(request)
        return blueprint.model_dump()
    except Exception as e:
        logger.error("Generation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blueprint/{workflow_id}")
async def get_blueprint(workflow_id: str):
    blueprint = orchestrator.get_workflow(workflow_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint.model_dump()


@router.post("/compare")
async def compare_ideas(request: CompareRequest):
    try:
        comparisons = await orchestrator.compare_ideas(request.ideas)
        return {"comparisons": comparisons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_workflow(request: ApprovalRequest):
    success = orchestrator.approve(request.workflow_id, request.approved)
    if not success:
        raise HTTPException(status_code=404, detail="No pending approval for this workflow")
    return {"approved": request.approved, "workflow_id": request.workflow_id}


@router.get("/memory/history")
async def get_history(limit: int = 20):
    return {"history": memory.get_history(limit)}


@router.get("/memory/patterns")
async def get_patterns():
    return memory.get_patterns()


@router.get("/graph/dependencies")
async def get_agent_graph():
    from app.agents import AGENT_DEPENDENCIES
    nodes = [{"id": a.value, "name": AGENT_REGISTRY[a].name} for a in AGENT_ORDER]
    edges = []
    for agent, deps in AGENT_DEPENDENCIES.items():
        for dep in deps:
            if dep != agent:
                edges.append({"source": dep.value, "target": agent.value})
    return {"nodes": nodes, "edges": edges}


@router.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted from %s", websocket.client)
    try:
        data = await websocket.receive_json()
        idea = data.get("idea", "")
        logger.info("WebSocket request received | idea=%s", idea[:100] if idea else "")
        if not idea:
            await websocket.send_json({"type": "error", "message": "Idea is required"})
            return

        request = GenerateRequest(
            idea=idea,
            generate_idea=data.get("generate_idea", False),
            industry=data.get("industry"),
            require_approval=data.get("require_approval", False),
        )

        async def emit_event(event: WorkflowEvent):
            logger.info(
                "Workflow event | type=%s agent=%s progress=%.0f message=%s",
                event.type,
                event.agent,
                event.progress,
                event.message[:80],
            )
            try:
                await websocket.send_json(json.loads(event.model_dump_json()))
            except RuntimeError as re:
                if "once a close message has been sent" in str(re):
                    logger.info("WebSocket already closed by client, skipping send.")
                else:
                    raise
            except Exception as e:
                logger.info("Failed to send WebSocket message (connection may be closed): %s", e)

        logger.info("Orchestrator starting workflow for idea: %s", idea[:100])
        blueprint = await orchestrator.generate(request, emit=emit_event)
        logger.info("Workflow completed | blueprint_id=%s score=%s", blueprint.id, blueprint.score.overall if blueprint.score else "N/A")
        await websocket.send_json({
            "type": "result",
            "blueprint": json.loads(blueprint.model_dump_json()),
        })
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception("WebSocket workflow failed: %s", e)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
