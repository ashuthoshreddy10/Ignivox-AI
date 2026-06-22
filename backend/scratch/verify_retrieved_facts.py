import json
import os
import glob

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
        print("No blueprint run found!")
        return
    blueprint_file = max(files, key=os.path.getmtime)
    print(f"Opening: {os.path.basename(blueprint_file)}\n")
    
    with open(blueprint_file, "r", encoding="utf-8") as f:
        blueprint = json.load(f)
        
    # Extract all claims except validation
    all_claims = []
    for section_name, section_data in blueprint.items():
        if section_name == "validation":
            continue
        if isinstance(section_data, dict) and "content" in section_data:
            all_claims.extend(scan_claims(section_data["content"], section_name))
            
    # Filter Retrieved Facts
    retrieved_facts = [(path, claim) for path, claim in all_claims if claim.get("category") == "Retrieved Fact"]
    print(f"Found {len(retrieved_facts)} Retrieved Facts:")
    
    for idx, (path, claim) in enumerate(retrieved_facts):
        print(f"\nRetrieved Fact {idx+1} (Path: {path}):")
        print(f"  Claim dictionary keys: {list(claim.keys())}")
        print(f"  Root fields:")
        print(f"    claim        : {claim.get('claim')}")
        print(f"    source       : {claim.get('source')}")
        print(f"    support_score: {claim.get('support_score')}")
        print(f"  Sources array:")
        sources = claim.get("sources", [])
        print(f"    Number of sources: {len(sources)}")
        for src_idx, src in enumerate(sources):
            print(f"    Source {src_idx+1}:")
            print(f"      source_url   : {src.get('source_url')}")
            print(f"      source_title : {src.get('source_title')}")
            print(f"      support_score: {src.get('support_score')}")

if __name__ == "__main__":
    main()
