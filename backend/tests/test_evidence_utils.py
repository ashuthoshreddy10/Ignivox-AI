"""Unit tests for evidence integrity utilities."""

import json

from app.services.evidence_utils import (
    build_grounding_map,
    detect_template_architecture,
    enforce_competitor_evidence,
    enforce_validation_output,
    fix_template_architecture,
    normalize_url,
    registry_to_serializable,
    merge_cumulative_registry,
    classify_claim,
    sanitize_investor_pitch,
)


def test_normalize_url_strips_tracking_and_truncates():
    raw = (
        "https://duckduckgo.com/l/?uddg="
        "https%3A%2F%2Fexample.com%2Freport%3Futm_source%3Dddg%26utm_campaign%3Dtest%26keep%3D1"
    )
    cleaned = normalize_url(raw)
    assert "utm_" not in cleaned
    assert "duckduckgo.com" not in cleaned
    assert cleaned.startswith("https://example.com")
    assert len(cleaned) <= 120


def test_competitor_enforcement_removes_unsupported_entities():
    registry = merge_cumulative_registry(
        None,
        json.dumps({
            "vector_context": [{
                "title": "Competitor Landscape - EdTech",
                "content": "Major players: Coursera https://coursera.org , Unacademy, Udemy",
                "category": "competitor",
            }],
            "memory_context": [],
            "live_sources": [],
        }),
    )
    content = {
        "competitors": {
            "direct_competitors": [
                {"name": "Coursera", "pricing": {"claim": "$39", "sources": [{"source_url": "https://coursera.org"}]}},
                {"name": "FakePrepBot AI", "pricing": {"claim": "$9", "sources": [{"source_url": "https://fake.ai"}]}},
            ]
        }
    }
    filtered = enforce_competitor_evidence(content, registry, "AI placement preparation platform")
    names = [c["name"] for c in filtered["competitors"]["direct_competitors"]]
    assert "Coursera" in names
    assert "FakePrepBot AI" not in names


def test_validation_enforcement_rejects_ungrounded_verification():
    grounding_map = [{
        "claim": "Global edtech market was $800B in 2025",
        "source_url": "https://example.com/market",
        "source_title": "Market Report",
        "agent": "market_research",
        "retrieval_timestamp": "2026-06-18T00:00:00Z",
    }]
    registry = merge_cumulative_registry(
        None,
        json.dumps({
            "live_sources": [{
                "title": "Market Report",
                "url": "https://example.com/market",
                "snippet": "Global edtech market was $800B in 2025",
                "timestamp": "2026-06-18T00:00:00Z",
            }],
            "vector_context": [],
            "memory_context": [],
        }),
    )
    content = {
        "evidence_quality_report": {
            "verified_claims": [
                {
                    "agent": "market_research",
                    "claim": "Global edtech market was $800B in 2025",
                    "status": "verified",
                    "verification": "verified",
                    "source": "https://example.com/market",
                    "sources": [{"source_url": "https://example.com/market", "source_title": "Market Report"}],
                },
                {
                    "agent": "competitor",
                    "claim": "Competitor X leads market",
                    "status": "verified",
                    "verification": "verified",
                    "source": "https://fabricated.example/comp",
                    "sources": [{"source_url": "https://fabricated.example/comp", "source_title": "Fake"}],
                },
            ]
        }
    }
    corrected = enforce_validation_output(content, grounding_map, registry)
    claims = corrected["evidence_quality_report"]["verified_claims"]
    by_claim = {c["claim"]: c for c in claims}
    assert by_claim["Global edtech market was $800B in 2025"]["status"] == "verified"
    assert by_claim["Competitor X leads market"]["status"] == "unsupported"


def test_template_architecture_detection_and_fix():
    content = {
        "tech_stack": {
            "frontend": {"claim": "customized frontend frameworks and libraries matching the domain"},
            "backend": {"claim": "FastAPI, Kafka, Celery"},
        }
    }
    assert detect_template_architecture(content)
    fixed = fix_template_architecture(content, "Helios Grid AI-powered smart energy optimization platform")
    assert "Kafka" in fixed["tech_stack"]["backend"]["claim"]
    assert "customized frontend" not in fixed["tech_stack"]["frontend"]["claim"].lower()


def test_grounding_map_preserves_required_fields():
    context = {
        "market_research": {
            "content": {
                "tam": {
                    "claim": "TAM $1B",
                    "sources": [{
                        "source_url": "https://example.com/tam",
                        "source_title": "TAM Source",
                        "retrieval_timestamp": "2026-06-18T00:00:00Z",
                    }],
                }
            }
        }
    }
    registry = merge_cumulative_registry(
        None,
        json.dumps({
            "live_sources": [{
                "title": "TAM Source",
                "url": "https://example.com/tam",
                "snippet": "TAM $1B",
                "timestamp": "2026-06-18T00:00:00Z",
            }],
            "vector_context": [],
            "memory_context": [],
        }),
    )
    mapping = build_grounding_map(context, registry)
    assert mapping
    entry = mapping[0]
    assert entry["claim"] == "TAM $1B"
    assert entry["source_url"] == "https://example.com/tam"
    assert entry["agent"] == "market_research"
    assert entry["retrieval_timestamp"]


def test_validation_enforcement_requires_claim_url_pair():
    grounding_map = [{
        "claim": "Global edtech market was $800B in 2025",
        "source_url": "https://example.com/market",
        "source_title": "Market Report",
        "agent": "market_research",
        "retrieval_timestamp": "2026-06-18T00:00:00Z",
    }]
    registry = merge_cumulative_registry(
        None,
        json.dumps({
            "live_sources": [{
                "title": "Market Report",
                "url": "https://example.com/market",
                "snippet": "Global edtech market was $800B in 2025",
                "timestamp": "2026-06-18T00:00:00Z",
            }],
            "vector_context": [],
            "memory_context": [],
        }),
    )
    content = {
        "evidence_quality_report": {
            "verified_claims": [{
                "agent": "competitor",
                "claim": "Different claim not in grounding map",
                "status": "verified",
                "verification": "verified",
                "source": "https://example.com/market",
                "sources": [{"source_url": "https://example.com/market", "source_title": "Market Report"}],
            }]
        }
    }
    corrected = enforce_validation_output(content, grounding_map, registry)
    claim = corrected["evidence_quality_report"]["verified_claims"][0]
    assert claim["status"] == "unsupported"


def test_registry_serializable_for_workflow_context():
    registry = merge_cumulative_registry(None, json.dumps({"vector_context": [], "memory_context": [], "live_sources": []}))
    serialized = registry_to_serializable(registry)
    json.dumps(serialized)


def test_enforce_competitor_evidence_removes_matrix_when_zero_comps():
    registry = merge_cumulative_registry(None, json.dumps({"vector_context": [], "memory_context": [], "live_sources": []}))
    content = {
        "competitors": {
            "direct_competitors": [
                {"name": "FakePrepBot AI", "pricing": {"claim": "$9", "sources": [{"source_url": "https://fake.ai"}]}},
            ]
        },
        "competitive_matrix": {
            "features": ["Pricing"],
            "our_product": [9],
            "competitor_avg": [5],
        },
        "competitor_averages": [5],
    }
    filtered = enforce_competitor_evidence(content, registry, "AI placement preparation platform")
    assert "competitive_matrix" not in filtered
    assert "competitor_averages" not in filtered
    assert filtered["competitor_evidence_status"] == "Insufficient competitor evidence"


def test_enforce_validation_output_insufficient_evidence():
    grounding_map = []
    registry = merge_cumulative_registry(None, json.dumps({"vector_context": [], "memory_context": [], "live_sources": []}))
    content = {
        "confidence_scores": {
            "market_research": 95.0,
            "competitor": 90.0,
        },
        "evidence_quality_report": {
            "verified_claims": [
                {
                    "agent": "market_research",
                    "claim": "Global edtech market was $800B in 2025",
                    "status": "verified",
                    "verification": "verified",
                    "source": "https://example.com/market",
                    "sources": [{"source_url": "https://example.com/market", "source_title": "Market Report"}],
                    "confidence": 0.95,
                }
            ]
        },
        "validation_summary": "Initial summary"
    }
    corrected = enforce_validation_output(content, grounding_map, registry)
    report = corrected["evidence_quality_report"]
    assert report["trusted_sources_count"] == 0
    assert report["evidence_quality_score"] <= 10.0
    assert corrected["overall_status"] == "Insufficient Evidence"
    assert "Insufficient Evidence" in corrected["validation_summary"]
    assert corrected["confidence_scores"]["market_research"] <= 50.0
    assert corrected["confidence_scores"]["competitor"] <= 50.0
    
    # Check claim confidence cap for unverified/unsupported claim
    claim = report["verified_claims"][0]
    assert claim["status"] == "unsupported"
    assert claim["confidence"] <= 30.0 / 100.0 or claim["confidence"] <= 0.30


def test_classify_claim_rules():
    # 1. TAM/SAM/SOM should always be Estimate
    assert classify_claim("TAM size is $20B", "tam_key", "market_research.tam", "market_research") == "Estimate"
    
    # 2. Financial projections should be Estimate, Projection, or Strategy, never fact (except for competitors)
    assert classify_claim("Year 3 ARR of $12M", "arr", "business_strategy.arr", "business_strategy") == "Projection"
    assert classify_claim("CAC is $150", "cac", "business_strategy.cac", "business_strategy") == "Estimate"
    assert classify_claim("$1.5M funding ask", "funding_ask", "investor_pitch.funding_ask", "investor_pitch") == "Strategy"
    
    # Financial projection for competitor CAN be Retrieved Fact
    assert classify_claim("Competitor A has $50M ARR", "arr", "competitor.competitors.direct.arr", "competitor") == "Retrieved Fact"

    # 3. Path-based matching
    assert classify_claim("Build MVP", "mvp", "product_strategy.mvp_definition.timeline", "product_strategy") == "Roadmap"
    assert classify_claim("High conversion rate", "assumption", "business_strategy.assumptions.conversion", "business_strategy") == "Assumption"

    # 4. Keyword-based matching
    assert classify_claim("projected to grow by 20%", "some_key", "some_path", "some_agent") == "Projection"


def test_sanitize_pitch_unauthorized_traction():
    context = {
        "market_research": {
            "content": {
                "problem_statement": "Grid waste is high."
            }
        }
    }
    registry = merge_cumulative_registry(
        None,
        json.dumps({
            "live_sources": [],
            "vector_context": [],
            "memory_context": [],
        }),
    )
    
    # Pitch deck claiming patents and active customers (not grounded in context)
    content = {
        "executive_summary": {
            "claim": "We have established partnerships and secured active customers."
        },
        "pitch_slides": [
            {
                "title": "Traction & Partnerships",
                "content": "Already adopted by 10+ enterprise customers with active partnerships.",
                "speaker_notes": "We have patents pending."
            }
        ],
        "narrative": {
            "claim": "Proven platform with successful deployments."
        }
    }
    
    sanitized = sanitize_investor_pitch(content, context, registry)
    
    # Check that sentences have been converted to future milestones
    assert "milestone" in sanitized["executive_summary"]["claim"].lower() or "target" in sanitized["executive_summary"]["claim"].lower()
    
    slide = sanitized["pitch_slides"][0]
    assert "target" in slide["content"].lower() or "milestone" in slide["content"].lower()
    assert "planned" in slide["speaker_notes"].lower() or "target" in slide["speaker_notes"].lower()
    
    assert "milestone" in sanitized["narrative"]["claim"].lower() or "target" in sanitized["narrative"]["claim"].lower()

