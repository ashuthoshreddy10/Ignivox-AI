import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with open("rag_retrieval_audit_report.json", encoding="utf-8") as f:
    r = json.load(f)

print("\n=== FULL NIM SCORE TABLE BY DOMAIN ===\n")
for domain, dr in r["benchmark_results"].items():
    print(f"=== {domain.upper()} ===")
    for d in dr["per_doc"]:
        nim = d["nim_score"]
        loc = d["local_score"]
        nim_str = f"{nim:.6f}" if nim is not None else "    N/A "
        print(f"  [{d['index']}] {d['title'][:50]:50s}  NIM={nim_str}  Local={loc:.6f}")
    s = dr["nim_statistics"]
    print(f"  NIM Stats: min={s['min']}  max={s['max']}  mean={s['mean']}  median={s['median']}")
    print(f"  Threshold sweep:")
    for t, v in dr["threshold_sweep"].items():
        print(f"    t={t}  NIM={v['nim_docs_pass']}/8  Local={v['local_docs_pass']}/8")
    print()

# Overall stats
all_nim = []
for dr in r["benchmark_results"].values():
    for d in dr["per_doc"]:
        if d["nim_score"] is not None:
            all_nim.append(d["nim_score"])

import statistics
print("=== GLOBAL NIM SCORE SUMMARY (all docs x all queries) ===")
print(f"  Count  : {len(all_nim)}")
print(f"  Min    : {min(all_nim):.6f}")
print(f"  Max    : {max(all_nim):.6f}")
print(f"  Mean   : {statistics.mean(all_nim):.6f}")
print(f"  Median : {statistics.median(all_nim):.6f}")
print(f"  Stdev  : {statistics.stdev(all_nim):.6f}")
print()
print(f"  Docs passing at t=0.40 : {sum(1 for s in all_nim if s >= 0.40)}/{len(all_nim)}")
print(f"  Docs passing at t=0.45 : {sum(1 for s in all_nim if s >= 0.45)}/{len(all_nim)}")
print(f"  Docs passing at t=0.50 : {sum(1 for s in all_nim if s >= 0.50)}/{len(all_nim)}")
print(f"  Docs passing at t=0.55 : {sum(1 for s in all_nim if s >= 0.55)}/{len(all_nim)}")
print(f"  Docs passing at t=0.60 : {sum(1 for s in all_nim if s >= 0.60)}/{len(all_nim)}")

print()
print("=== EMBEDDING CONSISTENCY ===")
print(f"  {r['embedding_consistency']}")
print()
print("=== NORMALIZATION ===")
print(f"  NIM   : {r['normalization_check'].get('nim_doc_norms')}")
print(f"  Local : {r['normalization_check'].get('local_doc_norms')}")
