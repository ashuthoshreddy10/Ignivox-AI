import os
import json
import glob

def main():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Check grounding_audit_log.json
    audit_log = os.path.join(backend_dir, "grounding_audit_log.json")
    if os.path.exists(audit_log):
        with open(audit_log, "r", encoding="utf-8") as f:
            log_data = json.load(f)
        print(f"Total entries in grounding_audit_log.json: {len(log_data)}")
        for idx, entry in enumerate(log_data):
            print(f"\nEntry {idx+1}:")
            print(f"  Claim: {entry.get('claim')}")
            print(f"  Source Title: {entry.get('source_title')}")
            print(f"  Source URL  : {entry.get('source_url')}")
            print(f"  Score       : {entry.get('support_score')}")
            print(f"  Is Supported: {entry.get('is_supported')}")
            print(f"  Agent       : {entry.get('agent')}")
    else:
        print("grounding_audit_log.json does not exist!")

    # Check for other log files
    log_files = glob.glob(os.path.join(backend_dir, "*.log"))
    print(f"\nFound log files: {log_files}")

if __name__ == "__main__":
    main()
