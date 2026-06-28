import json

file_path = r"c:\Users\npsan\ignivox-ai\backend\knowledge\startup_knowledge.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total documents: {len(data)}")
for i, doc in enumerate(data):
    print(f"{i}: URL={doc.get('source_url')} | TITLE={doc.get('source_title')}")
