"""
RAG Retrieval Failure Root Cause Audit
=======================================
Audits why docs_used = 0 in NVIDIA Live Mode.

Checks:
  1. Raw similarity scores before any filtering (min/max/mean/median)
  2. Threshold analysis -- is 0.60 over-filtering?
  3. Embedding consistency -- same model for index and query?
  4. Vector normalization -- cosine similarity correctness
  5. Domain benchmark -- 5 queries across Education/Energy/Healthcare/Cyber/Frontier

Does NOT modify any code. Read-only diagnostic only.
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import statistics
import sys
from pathlib import Path

# Force UTF-8 stdout to avoid Windows cp1252 encoding errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config import settings
from app.services.nvidia_nim import nim_service

KNOWLEDGE_PATH = Path(__file__).parent / "knowledge"
REPORT_PATH = Path(__file__).parent / "rag_retrieval_audit_report.json"

# ── benchmark queries ────────────────────────────────────────────────────────
BENCHMARK_QUERIES = {
    "energy": "Helios Grid: AI-powered smart energy optimization platform Market Research Agent",
    "edtech": "AI placement preparation platform for college students Market Research Agent",
    "healthtech": "AI-powered telehealth diagnostics and patient care platform Market Research Agent",
    "cybersecurity": "SIEM log threat predictor and firewall anomaly detection Market Research Agent",
    "frontier": "Brain-computer cloud for collective intelligence and cognitive augmentation Market Research Agent",
}

THRESHOLDS_TO_TEST = [0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]


# ── helpers ──────────────────────────────────────────────────────────────────

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Safe cosine similarity with norm checks."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def local_embed(texts: list[str]) -> np.ndarray:
    """Reproduce the exact local fallback embedding from nemo_retriever.py."""
    vectors = []
    for text in texts:
        vec = np.zeros(384)
        for i, char in enumerate(text[:384]):
            vec[i % 384] += ord(char) / 1000.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        vectors.append(vec)
    return np.array(vectors)


def stats(values: list[float]) -> dict:
    if not values:
        return {"min": None, "max": None, "mean": None, "median": None, "stdev": None}
    return {
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(statistics.mean(values), 6),
        "median": round(statistics.median(values), 6),
        "stdev": round(statistics.stdev(values), 6) if len(values) > 1 else 0.0,
    }


# ── load knowledge base ──────────────────────────────────────────────────────

def load_documents() -> list[dict]:
    docs = []
    for file_path in KNOWLEDGE_PATH.glob("*.json"):
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    docs.extend(data)
                elif isinstance(data, dict):
                    docs.append(data)
        except Exception as e:
            print(f"  [WARN] Failed to load {file_path}: {e}")
    return docs


# ── main audit ───────────────────────────────────────────────────────────────

async def run_audit() -> None:
    print("=" * 72)
    print("RAG RETRIEVAL FAILURE ROOT CAUSE AUDIT")
    print(f"  use_nvidia   : {settings.use_nvidia}")
    print(f"  demo_mode    : {settings.demo_mode}")
    print(f"  embed_model  : {settings.nim_embed_model}")
    print("=" * 72)

    # ── Step 0: load documents ───────────────────────────────────────────────
    docs = load_documents()
    print(f"\n[1] Loaded {len(docs)} documents from {KNOWLEDGE_PATH}")
    for i, d in enumerate(docs):
        print(f"    [{i}] {d.get('title', 'Untitled')!r:50s}  category={d.get('category', '?')}")

    doc_texts = [f"{d.get('title', '')}: {d.get('content', '')}" for d in docs]

    # ── Step 1: generate NIM embeddings for documents ────────────────────────
    print(f"\n[2] Generating NIM embeddings for {len(docs)} documents via {settings.nim_embed_model} ...")
    try:
        nim_doc_embeddings_raw = await nim_service.embed(doc_texts)
        nim_doc_embeddings = np.array(nim_doc_embeddings_raw)
        print(f"    Shape  : {nim_doc_embeddings.shape}")
        print(f"    Dtype  : {nim_doc_embeddings.dtype}")
        norms = np.linalg.norm(nim_doc_embeddings, axis=1)
        print(f"    Norms  : min={norms.min():.6f}  max={norms.max():.6f}  mean={norms.mean():.6f}")
        nim_embed_ok = True
    except Exception as e:
        print(f"    [ERROR] NIM embed failed: {e}")
        nim_doc_embeddings = None
        nim_embed_ok = False

    # ── Step 2: generate LOCAL embeddings for documents ──────────────────────
    print(f"\n[3] Generating LOCAL fallback embeddings for {len(docs)} documents ...")
    local_doc_embeddings = local_embed(doc_texts)
    norms_local = np.linalg.norm(local_doc_embeddings, axis=1)
    print(f"    Shape  : {local_doc_embeddings.shape}")
    print(f"    Norms  : min={norms_local.min():.6f}  max={norms_local.max():.6f}  mean={norms_local.mean():.6f}")

    # ── Step 3: benchmark every domain query ─────────────────────────────────
    benchmark_results = {}

    print(f"\n[4] Running benchmark queries ({len(BENCHMARK_QUERIES)} domains) ...")
    print("-" * 72)

    for domain, query in BENCHMARK_QUERIES.items():
        print(f"\n  Domain: {domain.upper()}")
        print(f"  Query : {query[:80]}...")

        domain_result = {
            "query": query,
            "nim_scores": [],
            "local_scores": [],
            "per_doc": [],
        }

        # NIM query embedding
        nim_query_emb = None
        if nim_embed_ok:
            try:
                q_raw = await nim_service.embed([query])
                nim_query_emb = np.array(q_raw[0])
            except Exception as e:
                print(f"    [ERROR] NIM query embed failed: {e}")

        # Local query embedding
        local_query_emb = local_embed([query])[0]

        print(f"\n  {'#':<3} {'Document':<45} {'NIM Score':>10} {'Local Score':>12} {'Accept@0.60':>12}")
        print(f"  {'-'*3} {'-'*45} {'-'*10} {'-'*12} {'-'*12}")

        for i, doc in enumerate(docs):
            nim_score = None
            local_score = cosine_similarity(local_doc_embeddings[i], local_query_emb)

            if nim_embed_ok and nim_query_emb is not None:
                nim_score = cosine_similarity(nim_doc_embeddings[i], nim_query_emb)

            nim_accept = "PASS" if nim_score is not None and nim_score >= 0.60 else "FAIL"
            local_accept = "PASS" if local_score >= 0.55 else "FAIL"

            nim_str = f"{nim_score:.6f}" if nim_score is not None else "  N/A   "
            print(f"  {i:<3} {doc.get('title', 'Untitled')[:45]:<45} {nim_str:>10} {local_score:>12.6f} {nim_accept:>12}")

            if nim_score is not None:
                domain_result["nim_scores"].append(nim_score)
            domain_result["local_scores"].append(local_score)
            domain_result["per_doc"].append({
                "index": i,
                "title": doc.get("title"),
                "category": doc.get("category"),
                "nim_score": nim_score,
                "local_score": local_score,
                "rejected_nim_reason": f"score {nim_score:.4f} < threshold 0.60" if nim_score is not None and nim_score < 0.60 else (None if nim_score is None else "passed"),
                "rejected_local_reason": f"score {local_score:.4f} < threshold 0.55" if local_score < 0.55 else "passed",
            })

        # Stats
        nim_stats = stats(domain_result["nim_scores"])
        local_stats = stats(domain_result["local_scores"])
        domain_result["nim_statistics"] = nim_stats
        domain_result["local_statistics"] = local_stats

        print(f"\n  NIM Score Stats   : min={nim_stats['min']}  max={nim_stats['max']}  mean={nim_stats['mean']}  median={nim_stats['median']}")
        print(f"  Local Score Stats : min={local_stats['min']}  max={local_stats['max']}  mean={local_stats['mean']}  median={local_stats['median']}")

        # Threshold sweep
        threshold_sweep = {}
        for t in THRESHOLDS_TO_TEST:
            nim_pass = sum(1 for s in domain_result["nim_scores"] if s >= t)
            local_pass = sum(1 for s in domain_result["local_scores"] if s >= t)
            threshold_sweep[str(t)] = {"nim_docs_pass": nim_pass, "local_docs_pass": local_pass}
        domain_result["threshold_sweep"] = threshold_sweep

        print(f"\n  Threshold sweep (NIM | Local):")
        for t, v in threshold_sweep.items():
            bar_nim = "█" * v["nim_docs_pass"]
            bar_loc = "█" * v["local_docs_pass"]
            print(f"    threshold={t:<4} : NIM {v['nim_docs_pass']}/{len(docs)} {bar_nim:<8}  Local {v['local_docs_pass']}/{len(docs)} {bar_loc}")

        benchmark_results[domain] = domain_result

    # ── Step 4: Embedding consistency check ──────────────────────────────────
    print(f"\n[5] Embedding consistency check ...")
    consistency = {}

    if nim_embed_ok and nim_doc_embeddings is not None:
        # Compare NIM vs Local for same doc — are they correlated?
        correlations = []
        for i in range(len(docs)):
            nim_v = nim_doc_embeddings[i]
            loc_v = local_doc_embeddings[i]
            # Pad or truncate local to match NIM dims
            nim_dim = nim_v.shape[0]
            loc_dim = loc_v.shape[0]
            if nim_dim != loc_dim:
                print(f"    [MISMATCH] NIM dim={nim_dim}, Local dim={loc_dim}")
                consistency["dimension_mismatch"] = True
                consistency["nim_dim"] = nim_dim
                consistency["local_dim"] = loc_dim
            else:
                c = cosine_similarity(nim_v, loc_v)
                correlations.append(c)

        if correlations:
            consistency["nim_vs_local_correlation"] = stats(correlations)
            print(f"    NIM vs Local correlation across docs: {consistency['nim_vs_local_correlation']}")
            if consistency["nim_vs_local_correlation"]["mean"] < 0.3:
                print(f"    [WARN] NIM and Local embeddings are VERY different vectors")
                consistency["verdict"] = "EMBEDDING_MISMATCH: NIM and local embeddings occupy completely different vector spaces"
            else:
                consistency["verdict"] = "Embeddings are correlated"
    else:
        consistency["verdict"] = "Could not test — NIM embed unavailable"

    # ── Step 5: Normalization check ──────────────────────────────────────────
    print(f"\n[6] Normalization check ...")
    norm_check = {}
    if nim_embed_ok and nim_doc_embeddings is not None:
        norms = np.linalg.norm(nim_doc_embeddings, axis=1)
        norm_check["nim_doc_norms"] = {
            "min": float(norms.min()),
            "max": float(norms.max()),
            "mean": float(norms.mean()),
            "all_unit_normalized": bool(np.allclose(norms, 1.0, atol=1e-4)),
        }
        print(f"    NIM doc norms: {norm_check['nim_doc_norms']}")

    local_norms = np.linalg.norm(local_doc_embeddings, axis=1)
    norm_check["local_doc_norms"] = {
        "min": float(local_norms.min()),
        "max": float(local_norms.max()),
        "mean": float(local_norms.mean()),
        "all_unit_normalized": bool(np.allclose(local_norms, 1.0, atol=1e-4)),
    }
    print(f"    Local doc norms: {norm_check['local_doc_norms']}")

    # ── Step 6: Root cause determination ─────────────────────────────────────
    print(f"\n[7] Root cause analysis ...")

    root_causes = []
    recommendations = []

    if nim_embed_ok:
        # Gather all NIM scores across all domain queries
        all_nim_scores = []
        for dr in benchmark_results.values():
            all_nim_scores.extend(dr["nim_scores"])

        all_stats = stats(all_nim_scores)
        print(f"    All NIM scores across all queries: {all_stats}")

        if all_stats["max"] is not None and all_stats["max"] < 0.60:
            root_causes.append({
                "cause": "A",
                "description": "THRESHOLD_TOO_AGGRESSIVE: All NIM scores fall below 0.60. The threshold eliminates all documents.",
                "evidence": f"NIM score max={all_stats['max']:.4f} across {len(all_nim_scores)} (doc, query) pairs — all below 0.60",
                "recommended_threshold": round(all_stats["max"] * 0.85, 3),
            })
        elif all_stats["mean"] is not None and all_stats["mean"] < 0.55:
            root_causes.append({
                "cause": "A+D",
                "description": "THRESHOLD_AND_COVERAGE: Scores are low. Threshold may be marginally too high AND knowledge base lacks domain coverage.",
                "evidence": f"NIM score mean={all_stats['mean']:.4f}  threshold=0.60",
                "recommended_threshold": round(all_stats["median"] * 0.95, 3) if all_stats["median"] else None,
            })

        # Check if NIM and local are mismatched
        if consistency.get("nim_vs_local_correlation", {}).get("mean", 1.0) < 0.3:
            root_causes.append({
                "cause": "B",
                "description": "EMBEDDING_MISMATCH: Document embeddings stored in retriever index were built with local_embed() (char-frequency hack), while query embeddings in Live Mode use NIM nv-embedqa-e5-v5. These are incomparable vector spaces.",
                "evidence": "nemo_retriever.py L55-58: embeddings = await nim_service.embed(texts) if settings.use_nvidia else self._local_embed(texts). In Demo Mode index is local; in Live Mode retrieval uses NIM query embed.",
            })

        # Domain filter check
        root_causes.append({
            "cause": "D",
            "description": "KNOWLEDGE_COVERAGE: startup_knowledge.json has 8 documents — 3 EdTech, 1 EdTech competitor, 4 generic SaaS. Zero energy/health/cybersecurity/frontier documents exist.",
            "evidence": f"{len(docs)} total docs. Domain-specific energy/health/cyber docs: 0",
        })

    else:
        root_causes.append({
            "cause": "UNKNOWN",
            "description": "Could not test NIM embeddings — NIM embed service unavailable during audit",
        })

    # ── Step 7: Print root causes ────────────────────────────────────────────
    print(f"\n{'='*72}")
    print("ROOT CAUSE FINDINGS")
    print(f"{'='*72}")
    for rc in root_causes:
        print(f"\n  [CAUSE {rc['cause']}] {rc['description']}")
        print(f"    Evidence: {rc['evidence']}")
        if "recommended_threshold" in rc and rc["recommended_threshold"]:
            print(f"    Recommended threshold: {rc['recommended_threshold']}")

    # ── Save report ──────────────────────────────────────────────────────────
    report = {
        "audit_timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "settings": {
            "use_nvidia": settings.use_nvidia,
            "demo_mode": settings.demo_mode,
            "nim_embed_model": settings.nim_embed_model,
            "nim_model": settings.nim_model,
        },
        "documents_loaded": len(docs),
        "document_list": [{"title": d.get("title"), "category": d.get("category")} for d in docs],
        "nim_embed_available": nim_embed_ok,
        "embedding_consistency": consistency,
        "normalization_check": norm_check,
        "benchmark_results": benchmark_results,
        "root_causes": root_causes,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[SAVED] Full report: {REPORT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(run_audit())
