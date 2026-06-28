import json
import glob
import os
import re

logs_path = r"C:\Users\npsan\.gemini\antigravity-ide\brain\d72d42f8-1790-482f-9951-fcbd8efd4722\.system_generated"

# Search transcript.jsonl
transcript_file = os.path.join(logs_path, "logs", "transcript.jsonl")
if os.path.exists(transcript_file):
    print("Searching transcript.jsonl...")
    with open(transcript_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                content = data.get("content", "")
                if not content:
                    continue
                # Search for mentions of multiple ideas
                if "ClearLedger" in content or "ideas" in content:
                    # Let's print sections of content
                    print(f"\n--- Transcript Line {i} ---")
                    lines = content.split("\n")
                    for line in lines:
                        if any(term in line for term in ["ClearLedger", "ideas", "BNPL", "idea"]):
                            print(line[:120])
            except Exception as e:
                pass

# Search messages/*.json
messages_pattern = os.path.join(logs_path, "messages", "*.json")
print("\nSearching messages...")
for msg_file in glob.glob(messages_pattern):
    try:
        with open(msg_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            content = str(data)
            if "ClearLedger" in content or "ideas" in content:
                print(f"\nFound in message: {os.path.basename(msg_file)}")
                for line in content.split("\n"):
                    if any(term in line for term in ["ClearLedger", "ideas", "BNPL"]):
                        print(line[:120])
    except Exception as e:
        pass
