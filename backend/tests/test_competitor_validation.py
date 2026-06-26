import os
import json
import pytest
from app.services.evidence_utils import enforce_competitor_evidence
from app.config import BACKEND_DIR

def test_competitor_reclassification_and_logging():
    # Setup mock data with direct hardware competitors
    content = {
        "competitors": {
            "direct_competitors": [
                {
                    "name": "Climeworks",
                    "pricing": "Varies",
                    "market_share": "15%"
                },
                {
                    "name": "SaaS Carbon Tracker Pro",
                    "pricing": "$99/mo",
                    "market_share": "5%"
                }
            ],
            "indirect_competitors": []
        }
    }
    # Mock registry (does not contain evidence for Climeworks or SaaS Carbon Tracker Pro)
    # But SaaS Carbon Tracker Pro will be removed because it has no evidence and is not a hardware player,
    # whereas Climeworks is reclassified and kept as indirect.
    registry = {
        "text_corpus": "",
        "domains": set(),
        "entity_names": set()
    }
    idea = "CarbonLedger: A SaaS emissions accounting platform"

    # Clear audit_diagnostics if exists before test
    audit_file = os.path.join(BACKEND_DIR, "audit_diagnostics.json")
    if os.path.exists(audit_file):
        try:
            os.remove(audit_file)
        except Exception:
            pass

    fixed = enforce_competitor_evidence(content, registry, idea)
    
    # Check that Climeworks is moved to indirect and marked
    directs = fixed["competitors"]["direct_competitors"]
    indirects = fixed["competitors"]["indirect_competitors"]
    
    # SaaS Carbon Tracker Pro is filtered out completely because it has no evidence
    assert len(directs) == 0
    
    # Climeworks is kept in indirects
    assert len(indirects) == 1
    climeworks_entry = indirects[0]
    assert climeworks_entry["name"] == "Climeworks"
    assert climeworks_entry.get("reclassified") == "hardware_to_indirect"
    
    # Verify logged entry in audit_diagnostics.json
    assert os.path.exists(audit_file)
    with open(audit_file, "r") as f:
        log = json.load(f)
    assert len(log) > 0
    last_log = log[-1]
    assert last_log["agent"] == "Competitor Agent"
    assert last_log["event"] == "competitor_reclassification"
    assert last_log["competitor_name"] == "Climeworks"
    assert last_log["reclassified"] == "hardware_to_indirect"

def test_non_hardware_competitors_are_not_reclassified():
    content = {
        "competitors": {
            "direct_competitors": [
                {
                    "name": "Stripe",
                    "pricing": "2.9% + 30c"
                }
            ],
            "indirect_competitors": []
        }
    }
    # Mock registry containing Stripe (lowercase for python case-sensitive in-check)
    registry = {
        "text_corpus": "stripe pricing is standard",
        "domains": {"stripe.com"},
        "entity_names": {"stripe"}
    }
    idea = "Payment flow utility platform"
    
    fixed = enforce_competitor_evidence(content, registry, idea)
    directs = fixed["competitors"]["direct_competitors"]
    indirects = fixed["competitors"]["indirect_competitors"]
    
    # Stripe is kept as direct competitor
    assert len(directs) == 1
    assert directs[0]["name"] == "Stripe"
    assert "reclassified" not in directs[0]
    assert len(indirects) == 0


def test_competitor_validation_under_fallback():
    content = {
        "competitors": {
            "direct_competitors": [
                {
                    "name": "Coursera",
                    "pricing": {
                        "claim": "Pricing is $39/month",
                        "sources": [{"source_url": "https://www.ipcc.ch/reports", "source_title": "Static Domain Metrics for Fintech"}]
                    }
                }
            ],
            "indirect_competitors": []
        }
    }
    registry = {
        "is_fallback": True,
        "text_corpus": "static domain metrics for fintech",
        "domains": set(),
        "entity_names": set(),
        "urls": {
            "https://www.ipcc.ch/reports": {
                "source_title": "Static Domain Metrics for Fintech",
                "source_url": "https://www.ipcc.ch/reports",
                "source_snippet": "Grounding context for a secure financial platform managing transaction ledgers and compliance audit logs.",
                "is_fallback": True
            }
        }
    }
    idea = "A micro-lending platform for small businesses"
    
    fixed = enforce_competitor_evidence(content, registry, idea)
    directs = fixed["competitors"]["direct_competitors"]
    
    # Coursera must be kept under fallback mode
    assert len(directs) == 1
    assert directs[0]["name"] == "Coursera"
    assert directs[0]["pricing"]["verification"] == "verified"
    assert directs[0]["pricing"]["source_count"] == 1
    assert directs[0]["pricing"]["sources"][0]["support_score"] >= 0.85
