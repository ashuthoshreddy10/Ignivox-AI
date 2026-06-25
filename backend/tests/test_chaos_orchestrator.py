import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_blank_slate_gibberish_input():
    """Scenario 3: Verifies random characters/tokens trigger a 422 validation error via Pydantic."""
    response = client.post("/api/generate", json={"idea": "asdfg12345!!!@@@ qwert"})
    assert response.status_code == 422
    assert "validation_error" in response.text or "value_error" in response.text

def test_compliance_trap_input():
    """Scenario 2: Verifies KYC-avoidant minor micro-lending is intercepted at the input rail layer."""
    response = client.post("/api/generate", json={"idea": "An anonymous micro-lending app for minors with zero KYC verification."})
    assert response.status_code == 400
    assert "policy_violation" in response.json()["detail"].lower()

def test_websocket_compliance_trap():
    """Scenario 2 (WS): Verifies that the WebSocket handler intercepts compliance violations and returns error."""
    with client.websocket_connect("/api/ws/generate") as websocket:
        websocket.send_json({
            "idea": "An anonymous micro-lending app for minors with zero KYC verification.",
            "generate_idea": False
        })
        response = websocket.receive_json()
        assert response["status"] == "error"
        assert "policy_violation" in response["message"].lower()

def test_contradictory_paradox_processing():
    """Scenario 1: Verifies paradoxes bypass input validation but are handled safely by the orchestrator.
    We force demo mode here to avoid making expensive live LLM requests during standard tests, 
    but the system still executes the full orchestrator agent workflow pipeline.
    """
    original_demo_mode = settings.demo_mode
    settings.demo_mode = True
    try:
        response = client.post("/api/generate", json={
            "idea": "A localized hyper-physical marketplace platform entirely built inside virtual reality."
        })
        assert response.status_code == 200
        blueprint = response.json()
        
        # Ensure the orchestration engine ran and evaluated the workflow safely
        assert "product_strategy" in blueprint
        assert blueprint["product_strategy"] is not None
        assert "content" in blueprint["product_strategy"]
        assert blueprint["score"] is not None
        assert blueprint["score"]["overall"] > 0
    finally:
        settings.demo_mode = original_demo_mode
