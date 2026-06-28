import json

with open('custom_blueprint.json', 'r', encoding='utf-8') as f:
    bp = json.load(f)

eq = bp.get('validation_report', {}).get('evidence_quality_report', {})
score = eq.get('evidence_quality_score')
trusted_sources = eq.get('trusted_sources_count')
direct_competitors = len(bp.get('competitor_analysis', {}).get('competitors', {}).get('direct_competitors', []))

print(f"Score: {score}")
print(f"Verified Sources: {trusted_sources}")
print(f"Competitors: {direct_competitors}")
