import asyncio
import json
import os
import sys
import glob
import uuid

# Setup sys path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config import settings, BACKEND_DIR
from app.models.schemas import GenerateRequest
from app.orchestration.workflow import orchestrator

HELIOS_GRID_IDEA = "Helios Grid: AI-powered smart energy optimization platform"

async def run():
    # 1. Clean previous audit outputs and blueprints
    print("\n--- PRE-RUN CLEANING ---")
    deleted_files = []
    
    # Audit and logging outputs
    cleanup_patterns = [
        "audit_diagnostics.json",
        "grounding_audit_log.json",
        "blueprint_run_*.json",
        "helios_blueprint_*.json",
        "helios_live_run_report.json",
        "grounding_run.log"
    ]
    
    for pattern in cleanup_patterns:
        for f in glob.glob(os.path.join(BACKEND_DIR, pattern)):
            try:
                os.remove(f)
                deleted_files.append(f)
                print(f"Deleted previous output: {os.path.basename(f)}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")
                
    # Memory database history
    history_path = os.path.join(BACKEND_DIR, "data", "memory", "history.json")
    if os.path.exists(history_path):
        try:
            os.remove(history_path)
            deleted_files.append(history_path)
            print("Deleted history.json database.")
        except Exception as e:
            print(f"Failed to delete history.json: {e}")
            
    print(f"Total previous outputs cleaned: {len(deleted_files)}")
    
    # 2. Show details before execution
    print("\n--- NEW WORKFLOW DETAILS ---")
    print(f"Startup Idea to test      : {HELIOS_GRID_IDEA}")
    
    # Generate a run ID for logging filename
    pre_generated_id = str(uuid.uuid4())
    blueprint_filename = f"blueprint_run_{pre_generated_id}.json"
    blueprint_filepath = os.path.join(BACKEND_DIR, blueprint_filename)
    
    print(f"Target Blueprint Filename : {blueprint_filename}")
    print(f"API Mode                  : NVIDIA Live (DEMO_MODE=False)")
    print("----------------------------\n")
    
    print("Executing workflow, please wait...")
    
    # 3. Execute
    blueprint = await orchestrator.generate(GenerateRequest(idea=HELIOS_GRID_IDEA))
    
    run_id = blueprint.id
    
    # Rename to use the actual workflow ID
    actual_filename = f"blueprint_run_{run_id}.json"
    actual_filepath = os.path.join(BACKEND_DIR, actual_filename)
    
    with open(actual_filepath, "w", encoding="utf-8") as f:
        json.dump(blueprint.model_dump(mode="json"), f, indent=2)
        
    print(f"\n[SUCCESS] Blueprint generated and saved to: {actual_filename}")
    print(f"Run ID: {run_id}")
    
    # 4. Parse validation metrics across the entire blueprint
    def scan_claims(obj):
        claims = []
        if isinstance(obj, dict):
            if "claim" in obj and ("sources" in obj or "verification" in obj):
                claims.append(obj)
            else:
                for v in obj.values():
                    claims.extend(scan_claims(v))
        elif isinstance(obj, list):
            for item in obj:
                claims.extend(scan_claims(item))
        return claims

    blueprint_dict = blueprint.model_dump(mode="json")
    all_claims = []
    for section_name, section_data in blueprint_dict.items():
        if section_name == "validation":
            continue
        if isinstance(section_data, dict) and "content" in section_data:
            all_claims.extend(scan_claims(section_data["content"]))

    historical_facts_count = 0
    retrieved_facts_count = 0
    projection_claims_count = 0
    recommendation_claims_count = 0
    
    for claim in all_claims:
        category = claim.get("category", "")
        if category == "Historical Fact":
            historical_facts_count += 1
        elif category == "Retrieved Fact":
            retrieved_facts_count += 1
        elif category == "Projection":
            projection_claims_count += 1
        elif category == "Recommendation":
            recommendation_claims_count += 1

    total_factual_claims_count = historical_facts_count + retrieved_facts_count
    final_score = blueprint.validation.content.get("evidence_quality_report", {}).get("evidence_quality_score", 0.0)
    
    # Count competitors
    competitors = blueprint.competitor_analysis.content.get("competitors", {})
    direct = len(competitors.get("direct_competitors", [])) if isinstance(competitors.get("direct_competitors"), list) else 0
    indirect = len(competitors.get("indirect_competitors", [])) if isinstance(competitors.get("indirect_competitors"), list) else 0
    alt = len(competitors.get("alternative_solutions", [])) if isinstance(competitors.get("alternative_solutions"), list) else 0
    res_alt = len(competitors.get("research_alternatives", [])) if isinstance(competitors.get("research_alternatives"), list) else 0
    en_tech = len(competitors.get("enabling_technologies", [])) if isinstance(competitors.get("enabling_technologies"), list) else 0
    competitors_count = direct + indirect + alt + res_alt + en_tech
    
    print("\n--- RESULTS REPORT ---")
    print(f"Historical Facts            : {historical_facts_count}")
    print(f"Retrieved Facts             : {retrieved_facts_count}")
    print(f"Total Factual Claims        : {total_factual_claims_count}")
    print(f"Projection Claims           : {projection_claims_count}")
    print(f"Recommendation Claims       : {recommendation_claims_count}")
    print(f"Competitors                 : {competitors_count}")
    print(f"Evidence Quality Score      : {final_score}")
    print("----------------------\n")

if __name__ == "__main__":
    asyncio.run(run())
