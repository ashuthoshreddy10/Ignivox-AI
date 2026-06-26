import os
import json
import pytest
from app.agents.business_strategy import BusinessStrategyAgent
from app.config import BACKEND_DIR

@pytest.mark.anyio
async def test_business_strategy_no_adjustment_consumer():
    # Consumer idea, target audience has no enterprise signals
    agent = BusinessStrategyAgent()
    idea = "A personal calorie tracking mobile app"
    context = {
        "market_research": {
            "content": {
                "target_audience": "Individual health-conscious consumers"
            }
        }
    }
    content = {
        "pricing_strategy": {
            "free": {"price": "$0", "features": ["Basic"]},
            "pro": {"price": "$9.99/month", "features": ["Advanced"]}
        }
    }
    
    # Call post processing
    result = agent._post_process_output(content, idea, context, "")
    
    # Should not adjust pricing
    assert "pricing_adjusted" not in result
    assert result["pricing_strategy"]["pro"]["price"] == "$9.99/month"

@pytest.mark.anyio
async def test_business_strategy_adjustment_enterprise_target_audience():
    # Enterprise target audience, consumer-level pricing
    agent = BusinessStrategyAgent()
    idea = "Carbon accounting system"
    context = {
        "market_research": {
            "content": {
                "target_audience": "Enterprise sustainability officers and B2B energy managers"
            }
        }
    }
    content = {
        "pricing_strategy": {
            "free": {"price": "$0", "features": ["Basic"]},
            "pro": {"price": "$9.99/month", "features": ["Advanced"]}
        }
    }
    
    # Clear audit_diagnostics if exists before test
    audit_file = os.path.join(BACKEND_DIR, "audit_diagnostics.json")
    if os.path.exists(audit_file):
        try:
            os.remove(audit_file)
        except Exception:
            pass
            
    # Call post processing
    result = agent._post_process_output(content, idea, context, "")
    
    # Should adjust pricing
    assert result.get("pricing_adjusted") is True
    assert result["pricing_strategy"].get("pricing_adjusted") is True
    assert result["pricing_strategy"]["smb"]["price"] == "$12,000/year"
    assert result["pricing_strategy"]["enterprise"]["price"] == "$60,000/year"
    
    # Verify logged entry
    assert os.path.exists(audit_file)
    with open(audit_file, "r") as f:
        log = json.load(f)
    assert len(log) > 0
    last_log = log[-1]
    assert last_log["agent"] == "Business Strategy Agent"
    assert last_log["event"] == "pricing_adjustment"
    assert last_log["pricing_adjusted"] is True
    assert last_log["old_pricing"]["pro"]["price"] == "$9.99/month"

@pytest.mark.anyio
async def test_business_strategy_adjustment_enterprise_idea_signals():
    # Target audience empty but idea contains B2B enterprise signal
    agent = BusinessStrategyAgent()
    idea = "Industrial AI maintenance and IoT infrastructure"
    context = {}
    content = {
        "pricing_strategy": {
            "pro": {"price": "$29/month", "features": ["Standard"]},
            "enterprise": {"price": "$99/month", "features": ["Full"]}
        }
    }
    
    # Call post processing
    result = agent._post_process_output(content, idea, context, "")
    
    # Should adjust pricing because idea contains "IoT" and "industrial" B2B signals
    assert result.get("pricing_adjusted") is True
    assert result["pricing_strategy"]["smb"]["price"] == "$12,000/year"
    assert result["pricing_strategy"]["enterprise"]["price"] == "$60,000/year"
