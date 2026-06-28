import json
with open("knowledge/startup_knowledge.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

print("Unique categories in startup_knowledge.json:", set(d.get("category") for d in docs))

# Let's search for "health" in title, content, or category
health_docs = []
for d in docs:
    text = f"{d.get('title', '')} {d.get('content', '')} {d.get('category', '')}".lower()
    if "health" in text:
        health_docs.append(d)

print(f"Count of Health-related documents: {len(health_docs)}")
for d in health_docs:
    has_url = "yes" if "source_url" in d else "no"
    print(f"- Title: {d.get('title')}")
    print(f"  Category: {d.get('category')}")
    print(f"  Source URL Exists: {has_url}")
    print(f"  Source URL: {d.get('source_url', 'N/A')}")
