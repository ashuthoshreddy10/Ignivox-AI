import json

with open("knowledge/startup_knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i, d in enumerate(data):
    print(f"{i}: {d.get('title')} | Category: {d.get('category')} | URL: {d.get('source_url')}")
