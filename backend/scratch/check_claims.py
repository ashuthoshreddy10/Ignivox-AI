import json

blueprint_path = "blueprint_run_c7e54e84-e630-4744-b272-62176347c351.json"
with open(blueprint_path, "r", encoding="utf-8") as f:
    bp = json.load(f)

print("Blueprint keys:", list(bp.keys()))
for k in bp.keys():
    if k not in ("id", "idea", "created_at", "status", "score", "recommendations", "validation", "evidence_quality_report", "confidence_scores"):
        val = bp[k]
        if isinstance(val, dict):
            print(f"Key: {k} | Content keys: {list(val.get('content', {}).keys())}")
