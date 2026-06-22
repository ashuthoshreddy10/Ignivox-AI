import json
import os
import glob

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
        
    # Get all claims (excluding validation)
    all_claims = []
    for section_name, section_data in blueprint.items():
        if section_name == "validation":
            continue
        if isinstance(section_data, dict) and "content" in section_data:
            all_claims.extend(scan_claims(section_data["content"]))
            
    # Filter verified claims (Historical Fact or Retrieved Fact with status == "verified")
    verified_claims = [c for c in all_claims if c.get("status") == "verified"]
    
    scores = []
    for claim in verified_claims:
        # Get support_score of verified sources
        for s in claim.get("sources", []):
            if "support_score" in s:
                scores.append(s["support_score"])
                
    print(f"Total verified claims scanned: {len(verified_claims)}")
    print(f"Total support scores extracted: {len(scores)}")
    
    if scores:
        print(f"1. Minimum support score: {min(scores)}")
        print(f"2. Maximum support score: {max(scores)}")
        print(f"3. Average support score: {sum(scores) / len(scores):.4f}")
    else:
        print("No support scores found for verified claims.")

    # Also inspect validation.verified_claims
    val_claims = blueprint.get("validation", {}).get("content", {}).get("evidence_quality_report", {}).get("verified_claims", [])
    val_scores = [c.get("support_score") for c in val_claims if c.get("status") == "verified" and c.get("support_score") is not None]
    print(f"\nInside validation.verified_claims:")
    print(f"Total verified claims: {len([c for c in val_claims if c.get('status') == 'verified'])}")
    if val_scores:
        print(f"1. Minimum support score: {min(val_scores)}")
        print(f"2. Maximum support score: {max(val_scores)}")
        print(f"3. Average support score: {sum(val_scores) / len(val_scores):.4f}")

if __name__ == "__main__":
    main()
