"""FastAPI routes for Ignivox AI."""

import asyncio
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
from app.services.evidence_utils import sanitize_timeline_payload

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
    # Run input guardrails
    from app.services.nemo_guardrails import guardrails
    safety_check = await guardrails.validate_input(request.idea)
    if not safety_check["passed"]:
        raise HTTPException(
            status_code=400,
            detail=f"policy_violation: {', '.join(safety_check['issues'])}"
        )
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
    send_lock = asyncio.Lock()
    socket_closed = False

    async def safe_send_json(payload: dict[str, Any]) -> bool:
        nonlocal socket_closed
        if socket_closed:
            return False
        try:
            async with send_lock:
                if socket_closed:
                    return False
                await websocket.send_json(payload)
            return True
        except RuntimeError as re:
            if "close message has been sent" not in str(re):
                logger.info("WebSocket runtime send failure: %s", re)
            socket_closed = True
            return False
        except Exception as e:
            logger.info("Failed to send WebSocket message (connection may be closed): %s", e)
            socket_closed = True
            return False
    
    # 🚀 THE INDEPENDENT HEARTBEAT DAEMON
    async def heartbeat_daemon(ws: WebSocket):
        try:
            while True:
                await asyncio.sleep(15)  # Pulse every 15 seconds
                sent = await safe_send_json({"type": "ping", "message": "heartbeat"})
                if not sent:
                    return
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    heartbeat_task = asyncio.create_task(heartbeat_daemon(websocket))

    try:
        data = await websocket.receive_json()
        idea = data.get("idea", "")
        logger.info("WebSocket request received | idea=%s", idea[:100] if idea else "")
        if not idea:
            await safe_send_json({"type": "error", "message": "Idea is required"})
            return

        try:
            request = GenerateRequest(
                idea=idea,
                generate_idea=bool(data.get("generate_idea", False)),
                industry=data.get("industry"),
                require_approval=bool(data.get("require_approval", False)),
            )
        except Exception as validation_err:
            await safe_send_json({
                "type": "error",
                "status": "error",
                "message": sanitize_timeline_payload(str(validation_err)),
            })
            return

        # Run input guardrails
        from app.services.nemo_guardrails import guardrails
        safety_check = await guardrails.validate_input(request.idea)
        if not safety_check["passed"]:
            await safe_send_json({
                "status": "error",
                "type": "error",
                "message": f"policy_violation: {', '.join(safety_check['issues'])}"
            })
            await websocket.close(code=4000)
            return

        async def emit_event(event: WorkflowEvent):
            logger.info(
                "Workflow event | type=%s agent=%s progress=%.0f message=%s",
                event.type,
                event.agent,
                event.progress,
                event.message[:80],
            )
            try:
                payload = json.loads(event.model_dump_json())
                payload = sanitize_timeline_payload(payload)
                await safe_send_json(payload)
            except Exception as e:
                logger.info("Failed to prepare WebSocket message: %s", e)

        logger.info("Orchestrator starting workflow for idea: %s", idea[:100])
        blueprint = await orchestrator.generate(request, emit=emit_event)
        logger.info("Workflow completed | blueprint_id=%s score=%s", blueprint.id, blueprint.score.overall if blueprint.score else "N/A")
        blueprint_json = json.loads(blueprint.model_dump_json())
        blueprint_json = sanitize_timeline_payload(blueprint_json)
        await safe_send_json({
            "type": "result",
            "blueprint": blueprint_json,
        })
    except WebSocketDisconnect:
        socket_closed = True
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception("WebSocket workflow failed: %s", e)
        error_msg = sanitize_timeline_payload(str(e))
        await safe_send_json({"type": "error", "status": "error", "message": error_msg})
    finally:
        heartbeat_task.cancel()
        await asyncio.gather(heartbeat_task, return_exceptions=True)
