import json
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file = os.path.join(backend_dir, "grounding_audit_log.json")

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        log = json.load(f)
    print(f"Total evaluated claims in log: {len(log)}")
    for i, entry in enumerate(log[:10]):
        print(f"\n[{i+1}] Claim: {entry.get('claim')}")
        print(f"    Source URL: {entry.get('source_url')}")
        print(f"    Similarity: {entry.get('support_score')}")
        print(f"    Is Supported: {entry.get('is_supported')}")
        print(f"    Agent: {entry.get('agent')}")
else:
    print("grounding_audit_log.json not found!")
