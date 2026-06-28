import json
with open('custom_blueprint.json') as f:
    bp = json.load(f)

comp_output = bp.get("competitor_analysis", {})
comp = comp_output.get("content", {})
print("Keys in content:", list(comp.keys()))
for k, v in comp.get("competitors", {}).items():
    print(f"Category: {k}")
    if isinstance(v, list):
        print(f"  Count: {len(v)}")
        for item in v:
            print(f"    - {item.get('name')}")
    else:
        print(f"  Value: {v}")

