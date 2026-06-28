import json
import os
from urllib.parse import urlparse

# Define the exact mapping of domains to their root/stable paths and titles
domain_mappings = {
    "unesco.org": ("https://en.unesco.org/themes/education", "UNESCO Education"),
    "nces.ed.gov": ("https://nces.ed.gov/programs", "NCES Programs"),
    "www.sec.gov": ("https://www.sec.gov/divisions/investment", "SEC Investment"),
    "ieeexplore.ieee.org": ("https://ieeexplore.ieee.org", "IEEE Xplore"),
    "spectrum.ieee.org": ("https://ieeexplore.ieee.org", "IEEE Xplore"),
    "platform.openai.com": ("https://platform.openai.com", "OpenAI Developer Platform"),
    "www.eia.gov": ("https://www.eia.gov/electricity", "EIA Electricity"),
    "www.ferc.gov": ("https://www.ferc.gov/industries-data/electric", "FERC Electric Industries"),
    "www.epri.com": ("https://www.epri.com", "EPRI Research"),
    "www.who.int": ("https://www.who.int/health-topics/digital-health", "WHO Digital Health"),
    "www.cms.gov": ("https://www.cms.gov/medicare", "CMS Medicare"),
    "www.ncbi.nlm.nih.gov": ("https://www.nih.gov/health-information", "NIH Health Information"),
    "www.cisa.gov": ("https://www.cisa.gov/resources-tools", "CISA Resources and Tools"),
    "csrc.nist.gov": ("https://www.nist.gov/cybersecurity", "NIST Cybersecurity"),
    "www.nist.gov": ("https://www.nist.gov/cybersecurity", "NIST Cybersecurity"),
    "www.bis.org": ("https://www.bis.org/publ", "BIS Publications"),
    "www.consumerfinance.gov": ("https://www.consumerfinance.gov/data-research", "CFPB Data and Research"),
    "www.worldbank.org": ("https://data.worldbank.org", "World Bank Open Data"),
    "www.transportation.gov": ("https://www.transportation.gov/research", "DOT Research"),
    "www.epa.gov": ("https://www.epa.gov/climate-change", "EPA Climate Change"),
    "www.ipcc.ch": ("https://www.ipcc.ch/reports", "IPCC Reports"),
    "www.iso.org": ("https://www.iso.org/standards", "ISO Standards"),
    "arxiv.org": ("https://arxiv.org/list/cs.AI/recent", "arXiv cs.AI Recent"),
    "www.cncf.io": ("https://www.cncf.io/reports", "CNCF Reports"),
}

file_path = r"c:\Users\npsan\ignivox-ai\backend\knowledge\startup_knowledge.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} documents.")

updated_count = 0
for idx, doc in enumerate(data):
    original_url = doc.get("source_url", "")
    parsed = urlparse(original_url)
    domain = parsed.netloc
    
    if domain in domain_mappings:
        target_url, target_title = domain_mappings[domain]
        # Check if actually different to count updates
        if doc.get("source_url") != target_url or doc.get("source_title") != target_title:
            doc["source_url"] = target_url
            doc["source_title"] = target_title
            updated_count += 1
    else:
        print(f"Warning: Domain '{domain}' not in mappings (URL: {original_url})")

# Save the updated JSON back to file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Successfully updated {updated_count} documents.")

# Show the first 5 updated documents as confirmation
print("\n--- First 5 Updated Documents ---")
for i in range(min(5, len(data))):
    print(f"\nDocument {i+1}:")
    print(f"  Title: {data[i].get('title')}")
    print(f"  Category: {data[i].get('category')}")
    print(f"  Source URL: {data[i].get('source_url')}")
    print(f"  Source Title: {data[i].get('source_title')}")
