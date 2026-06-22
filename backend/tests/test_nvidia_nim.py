import pytest
import os
import json
from unittest.mock import MagicMock
from app.services.nvidia_nim import (
    repair_investor_pitch_structure,
    _parse_json_with_recovery,
    _close_open_json_structures
)


def test_repair_investor_pitch_structure_non_matching_agent():
    # If agent_type != "investor_pitch", it should not modify the dictionary or do any repairs
    data = {"some_key": "some_value"}
    result = repair_investor_pitch_structure(data, "other_agent")
    assert result == data
    assert "_recovered" not in result


def test_repair_investor_pitch_structure_matching_agent_missing_fields():
    # Ensure logs directory is ready and clear test logs
    log_path = "logs/investor_pitch_failures.json"
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except Exception:
            pass

    data = {}
    result = repair_investor_pitch_structure(data, "investor_pitch")
    
    # Assert top level _recovered flag exists
    assert result["_recovered"] is True
    
    # Assert slides, funding_ask, executive_summary, key_metrics defaults are set
    assert "slides" in result
    assert len(result["slides"]) >= 1
    assert result["slides"][0]["_recovered"] is True

    assert "pitch_slides" in result
    assert len(result["pitch_slides"]) >= 1
    assert result["pitch_slides"][0]["_recovered"] is True

    assert "funding_ask" in result
    assert result["funding_ask"]["_recovered"] is True
    assert result["funding_ask"]["amount"]["_recovered"] is True

    assert "executive_summary" in result
    assert isinstance(result["executive_summary"], str)
    assert getattr(result["executive_summary"], "_recovered", False) is True
    assert result["executive_summary_recovered"] is True

    assert "key_metrics" in result
    assert isinstance(result["key_metrics"], list)
    assert len(result["key_metrics"]) > 0

    # Verify logging to logs/investor_pitch_failures.json
    assert os.path.exists(log_path)
    with open(log_path, "r", encoding="utf-8") as f:
        failures = json.load(f)
        assert len(failures) > 0
        for entry in failures:
            assert "timestamp" in entry
            assert "field_name" in entry
            assert "recovery_action" in entry


def test_repair_investor_pitch_structure_truncated_slides():
    data = {
        "slides": [
            {"title": "Valid slide", "content": "Valid body", "speaker_notes": "notes"},
            {"title": "Truncated slide"}  # Missing content
        ]
    }
    result = repair_investor_pitch_structure(data, "investor_pitch")
    # Discard the last slide since it is truncated (missing content)
    assert len(result["slides"]) == 1
    assert result["slides"][0]["title"] == "Valid slide"


def test_parse_json_with_recovery_investor_pitch():
    # If the text is truncated JSON and executive_summary is parsed as a string,
    # it should wrap the validation function to accept it.
    truncated_json = """
    {
        "executive_summary": "This is a recovered text.",
        "pitch_slides": [{"title": "Title", "content": "Content", "speaker_notes": "Notes"}],
        "funding_strategy": {"stage": "Seed", "target_investors": ["VCs"], "timeline": "now", "key_metrics_for_series_a": []},
        "funding_ask": {"amount": {"claim": "1M"}, "valuation": {"claim": "5M"}, "runway_months": {"claim": "18"}, "use_of_funds": {}},
        "narrative": {"claim": "Narrative"}
    """
    
    # Mock validator
    def mock_validator(data):
        errors = []
        if not isinstance(data.get("executive_summary"), dict):
            errors.append("Key 'executive_summary' is not a JSON object")
        return errors

    # This should succeed since _parse_json_with_recovery wraps the validator for investor_pitch agent type
    result = _parse_json_with_recovery(truncated_json, mock_validator, "investor_pitch")
    assert result["executive_summary"] == "This is a recovered text."
