import json
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
blueprint_file = os.path.join(backend_dir, "blueprint_run_cc1210fc-2676-4535-94dc-57d7bda1b005.json")

with open(blueprint_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# The validation agent context or the evidence registry can be found in the blueprint
# Let's inspect data["claim_lineage"] or other fields
print("Lineage sample:")
for entry in data.get("claim_lineage", [])[:5]:
    print(entry)

print("\nCompetitor Analysis output:")
print(json.dumps(data.get("competitor_analysis", {}).get("content"), indent=2))

print("\nMarket Research output:")
print(json.dumps(data.get("market_research", {}).get("content"), indent=2))

# Let's find the evidence registry in validation/context if it is there
# Wait, let's check if there is an evidence_registry in the context or if we can rebuild it from the audit files
