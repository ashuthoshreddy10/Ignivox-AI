import json

# Check 1: HealthTech docs in knowledge base
with open('knowledge/startup_knowledge.json') as f:
    kb = json.load(f)

health_docs = [d for d in kb if 'health' in d.get('category','').lower() 
               or 'health' in d.get('title','').lower()]
print(f'HealthTech docs in knowledge base: {len(health_docs)}')
for d in health_docs:
    print(f'  - {d["title"]}')
    print(f'    source_url: {d.get("source_url", "MISSING")}')
    print(f'    source_title: {d.get("source_title", "MISSING")}')

# Check 2: What made it into the blueprint evidence registry
with open('custom_blueprint.json') as f:
    bp = json.load(f)

registry = bp.get('evidence_registry', {})
print(f'\nEvidence registry entries: {len(registry)}')
for url, entry in list(registry.items())[:10]:
    print(f'  URL: {url}')
    print(f'  support_score: {entry.get("support_score")}')

# Check 3: Claim lineage - what sources were referenced
lineage = bp.get('claim_lineage', [])
print(f'\nClaim lineage entries: {len(lineage)}')
for item in lineage[:5]:
    print(f'  claim: {str(item.get("claim",""))[:60]}')
    print(f'  sources: {item.get("sources", [])}')

# Check 4: Validation report
val = bp.get('validation_report', {})
if not val:
    # Let's check validation key as well
    val = bp.get('validation', {}).get('content', {})
eq = val.get('evidence_quality_report', {})
print(f'\nEvidence Quality Score: {eq.get("evidence_quality_score")}')
print(f'Verified Sources: {eq.get("trusted_sources_count")}')
print(f'Total Claims Verified: {eq.get("total_claims_verified")}')
