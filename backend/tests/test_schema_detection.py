import pytest
from app.services.evidence_utils import _fix_energy_table_leakage, remove_edtech_contamination

def test_energy_idea_does_not_modify_energy_tables():
    content = {
        "database_schema": {
            "users": "id, email",
            "grid_elements": "id, status",
            "maintenance_logs": "id, elements"
        }
    }
    idea = "Smart grid energy optimization network"
    # Call leakage fixer directly
    fixed = _fix_energy_table_leakage(content, idea)
    assert "grid_elements" in fixed["database_schema"]
    assert "maintenance_logs" in fixed["database_schema"]
    assert "emissions_ledger" not in fixed["database_schema"]

def test_climatetech_idea_replaces_energy_tables():
    content = {
        "database_schema": {
            "users": "id, email",
            "grid_elements": "id, status",
            "maintenance_logs": "id, elements"
        }
    }
    idea = "Carbon offset registry and emissions ledger tracking platform"
    fixed = _fix_energy_table_leakage(content, idea)
    schema = fixed["database_schema"]
    assert "grid_elements" not in schema
    assert "maintenance_logs" not in schema
    assert "emissions_ledger" in schema
    assert "offset_registry" in schema
    assert "telemetry_ingest" in schema
    assert "iot_device_registry" in schema
    assert "scope_mapping" in schema
    assert fixed.get("_architecture_template_corrected") is True

def test_healthtech_idea_replaces_energy_tables():
    content = {
        "database_schema": {
            "users": "id, email",
            "grid_elements": "id, status",
            "maintenance_logs": "id, elements"
        }
    }
    idea = "Secure medical clinic patient records platform"
    fixed = _fix_energy_table_leakage(content, idea)
    schema = fixed["database_schema"]
    assert "grid_elements" not in schema
    assert "maintenance_logs" not in schema
    assert "patients" in schema
    assert "audit_logs" in schema
    assert "fhir_records" in schema
    assert "consent_registry" in schema

def test_fintech_idea_replaces_energy_tables():
    content = {
        "database_schema": {
            "users": "id, email",
            "grid_elements": "id, status",
            "maintenance_logs": "id, elements"
        }
    }
    idea = "A microfinance bank offering custom ledgers"
    fixed = _fix_energy_table_leakage(content, idea)
    schema = fixed["database_schema"]
    assert "grid_elements" not in schema
    assert "maintenance_logs" not in schema
    assert "transactions" in schema
    assert "ledger_entries" in schema
    assert "compliance_log" in schema
    assert "kyc_records" in schema

def test_logistics_idea_replaces_energy_tables():
    content = {
        "database_schema": {
            "users": "id, email",
            "grid_elements": "id, status",
            "maintenance_logs": "id, elements"
        }
    }
    idea = "Shipping and freight warehouse supply chain tracking software"
    fixed = _fix_energy_table_leakage(content, idea)
    schema = fixed["database_schema"]
    assert "grid_elements" not in schema
    assert "maintenance_logs" not in schema
    assert "shipments" in schema
    assert "carriers" in schema
    assert "routes" in schema
    assert "tracking_events" in schema

def test_end_to_end_post_process_via_edtech_contamination():
    # Verify that remove_edtech_contamination (which is run at the end of post processing)
    # properly intercepts and corrects Energy table leakage for technical architect output
    content = {
        "database_schema": {
            "users": "id, email",
            "grid_elements": "id, status",
            "maintenance_logs": "id, elements"
        }
    }
    idea = "Offset emissions carbon platform"
    fixed = remove_edtech_contamination(content, idea)
    schema = fixed["database_schema"]
    assert "grid_elements" not in schema
    assert "emissions_ledger" in schema
