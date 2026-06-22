import json
import os
import glob

def main():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Find the generated blueprint file
    files = glob.glob(os.path.join(backend_dir, "blueprint_run_*.json"))
    if not files:
        print("No blueprint_run_*.json file found!")
        return
        
    # Pick the most recently modified one if there are multiple
    blueprint_file = max(files, key=os.path.getmtime)
    print(f"Reading blueprint from: {os.path.basename(blueprint_file)}")
    
    with open(blueprint_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Extract verified_claims from evidence_quality_report
    report = data.get("validation", {}).get("content", {}).get("evidence_quality_report", {})
    verified_claims = report.get("verified_claims", [])
    
    print(f"Total claims in evidence_quality_report.verified_claims: {len(verified_claims)}")
    
    # Let's count by category
    categories = {}
    for claim in verified_claims:
        cat = claim.get("category", "None")
        categories[cat] = categories.get(cat, 0) + 1
        
    print("\n--- CATEGORY COUNTS ---")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
        
    print("\n--- TOP 20 CLAIMS ---")
    for i, claim in enumerate(verified_claims[:20]):
        print(f"\nClaim {i+1}:")
        print(f"  Text     : {claim.get('claim')}")
        print(f"  Category : {claim.get('category')}")
        print(f"  Status   : {claim.get('status')}")
        print(f"  Agent    : {claim.get('agent')}")
        print(f"  Path/Key : {claim.get('parent_path') or claim.get('parent_key') or 'N/A'}")
        print(f"  Source   : {claim.get('source')}")

if __name__ == "__main__":
    main()
