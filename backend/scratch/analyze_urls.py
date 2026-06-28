import json
import os
from urllib.parse import urlparse

file_path = r"c:\Users\npsan\ignivox-ai\backend\knowledge\startup_knowledge.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total documents: {len(data)}")
domains = {}
for i, doc in enumerate(data):
    url = doc.get("source_url", "")
    parsed = urlparse(url)
    domain = parsed.netloc
    domains.setdefault(domain, []).append((i, url, doc.get("source_title", "")))

for domain, urls in sorted(domains.items()):
    print(f"\nDomain: {domain} ({len(urls)} docs)")
    for i, url, title in urls[:3]:
        print(f"  [{i}] {url} -> {title}")
    if len(urls) > 3:
        print("  ...")
