import json
import os
import glob
import re

def scan_claims(obj, path=""):
    claims = []
    if isinstance(obj, dict):
        if "claim" in obj and ("sources" in obj or "verification" in obj):
            claims.append((path, obj))
        else:
            for k, v in obj.items():
                p = f"{path}.{k}" if path else k
                claims.extend(scan_claims(v, p))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            claims.extend(scan_claims(item, f"{path}[{idx}]"))
    return claims

def main():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    files = glob.glob(os.path.join(backend_dir, "blueprint_run_*.json"))
    if not files:
        print("No blueprint_run_*.json file found!")
        return
    blueprint_file = max(files, key=os.path.getmtime)
    
    with open(blueprint_file, "r", encoding="utf-8") as f:
        blueprint = json.load(f)
        
    all_claims = []
    for agent_name, agent_data in blueprint.items():
        if isinstance(agent_data, dict) and "content" in agent_data:
            claims = scan_claims(agent_data["content"], agent_name)
            all_claims.extend(claims)
            
    print(f"TOTAL_GROUNDED_CLAIMS_GENERATED: {len(all_claims)}")
    
    # 4. Count by category
    categories = {"Historical Fact": 0, "Retrieved Fact": 0, "Projection": 0, "Estimate": 0, "Assumption": 0, "Strategy": 0, "Recommendation": 0, "Roadmap": 0}
    other_categories = {}
    for path, claim in all_claims:
        cat = claim.get("category", "None")
        if cat in categories:
            categories[cat] += 1
        else:
            other_categories[cat] = other_categories.get(cat, 0) + 1
            
    print("\n=== COUNT BY CATEGORY ===")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    for cat, count in other_categories.items():
        print(f"  {cat} (Other): {count}")
        
    print("\n=== TOP 20 CLAIMS ===")
    for idx, (path, claim) in enumerate(all_claims[:20]):
        print(f"{idx+1}. Path: {path}")
        print(f"   Text: {claim.get('claim')}")
        print(f"   Category: {claim.get('category')}")
        print(f"   Status: {claim.get('status')}")
        print(f"   Reason/Path rules: {path}")


if __name__ == "__main__":
    main()
