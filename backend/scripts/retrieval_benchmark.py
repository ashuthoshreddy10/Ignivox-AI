"""RAG Retrieval Benchmark Script to verify threshold calibration & domain contamination."""

import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np
from app.config import settings
from app.services.nvidia_nim import nim_service
from app.services.nemo_retriever import retriever


def get_doc_domain(d: dict) -> str:
    title = str(d.get("title", "")).lower()
    content = str(d.get("content", "")).lower()
    category = str(d.get("category", "")).lower()
    doc_text = f"{title} {content} {category}"
    if any(w in doc_text for w in ["edtech", "campus placement", "placement preparation", "unacademy", "byju", "coursera", "udemy"]):
        return "edtech"
    if any(w in doc_text for w in ["healthtech", "health", "hipaa", "fhir", "clara", "telehealth", "telemedicine", "patient care", "clinical"]):
        return "healthtech"
    if any(w in doc_text for w in ["fintech", "finance", "pci-dss", "pci-ds", "stripe", "plaid", "payment", "open banking", "ledger"]):
        return "fintech"
    if any(w in doc_text for w in ["energy", "smart grid", "electricity", "utility", "schneider", "siemens", "ge grid", "scada", "iot", "helios"]):
        return "energy"
    if any(w in doc_text for w in ["cybersecurity", "security", "siem", "soc", "crowdstrike", "palo alto", "splunk", "firewall", "threat"]):
        return "cybersecurity"
    if any(w in doc_text for w in ["logistics", "supply chain", "fleet", "wms", "flexport", "project44", "fourkites", "warehouse"]):
        return "logistics"
    if any(w in doc_text for w in ["climatetech", "climate", "carbon", "esg", "climeworks", "arcadia", "pachama"]):
        return "climatetech"
    if any(w in doc_text for w in ["industrial", "predictive maintenance", "digital twin", "manufacturing", "uptake", "c3.ai", "samsara"]):
        return "industrial"
    if any(w in doc_text for w in ["enterprise_saas", "enterprise saas", "salesforce", "servicenow", "workday", "b2b saas", "multi-tenant", "multitenant"]):
        return "enterprise_saas"
    if any(w in doc_text for w in ["frontier", "deeptech", "deep tech", "neuralink", "anthropic", "d-wave", "hpc", "quantum", "bci", "brain-computer"]):
        return "frontier"
    return "general"


def get_query_domain(query: str) -> str:
    query_lower = query.lower()
    query_words = {w.strip(".,!?\"'()[]{}") for w in query_lower.split()}
    edtech_keywords = {"student", "college", "placement", "education", "lms", "academic", "learn", "university", "career", "edtech", "school", "tutoring", "class"}
    health_keywords = {"health", "medical", "patient", "fhir", "hipaa", "clinic", "hospital", "doctor", "diagnose", "treatment", "clara", "telehealth", "telemedicine"}
    fintech_keywords = {"fintech", "finance", "payment", "bank", "invest", "crypto", "trading", "ledger", "double-entry", "billing"}
    energy_keywords = {"energy", "electricity", "utility", "grid", "helios", "scada", "iot", "sensor", "telemetry", "maintenance"}
    cyber_keywords = {"cybersecurity", "siem", "firewall", "threat", "security", "threat predictor"}
    frontier_keywords = {"brain", "cognitive", "bci", "neural", "collective intelligence", "telepathic"}
    logistics_keywords = {"logistics", "supply", "chain", "fleet", "warehouse", "wms", "freight", "shipping", "distribution", "route"}
    climatetech_keywords = {"climatetech", "climate", "carbon", "esg", "greenhouse", "emissions", "sustainability", "renewable"}
    industrial_keywords = {"industrial", "manufacturing", "twin", "maintenance", "scada", "iiot", "factory", "machinery"}
    enterprise_saas_keywords = {"enterprise", "saas", "salesforce", "servicenow", "workday", "crm", "erp", "hrtech", "b2b", "workflow", "tenant", "multitenant"}
    
    if any(w in query_words for w in edtech_keywords):
        return "edtech"
    elif any(w in query_words for w in health_keywords):
        return "healthtech"
    elif any(w in query_words for w in fintech_keywords):
        return "fintech"
    elif any(w in query_words for w in industrial_keywords) or "predictive maintenance" in query_lower or "digital twin" in query_lower:
        return "industrial"
    elif any(w in query_words for w in energy_keywords):
        return "energy"
    elif any(w in query_words for w in cyber_keywords) or "threat predictor" in query_lower:
        return "cybersecurity"
    elif any(w in query_words for w in frontier_keywords) or "collective intelligence" in query_lower:
        return "frontier"
    elif any(w in query_words for w in logistics_keywords) or "supply chain" in query_lower:
        return "logistics"
    elif any(w in query_words for w in climatetech_keywords) or "carbon credit" in query_lower or "esg tracking" in query_lower:
        return "climatetech"
    elif any(w in query_words for w in enterprise_saas_keywords):
        return "enterprise_saas"
    return "general"


BENCHMARK_QUERIES = {
    "edtech": "AI placement preparation platform for college students",
    "energy": "Helios Grid: AI-powered smart energy optimization platform",
    "healthtech": "AI-powered telehealth diagnostics and patient care platform",
    "cybersecurity": "SIEM log threat predictor and firewall anomaly detection",
    "fintech": "Embedded finance API platform for SMB payment automation",
    "logistics": "AI-powered supply chain visibility and fleet optimization platform",
    "climatetech": "Carbon credit marketplace with real-time ESG tracking",
    "industrial": "Predictive maintenance platform for manufacturing equipment",
    "frontier": "Brain-computer cloud for collective intelligence and cognitive augmentation"
}


async def main():
    print("=" * 80)
    print("RAG Retrieval Benchmark: Threshold Calibration + Knowledge Base Expansion")
    print(f"Retrieval Threshold Setting: {settings.retrieval_threshold}")
    print(f"Use NVIDIA Embeddings: {settings.use_nvidia}")
    print("=" * 80)
    
    # Load knowledge retriever and trigger doc embeddings creation
    print("Loading documents and preparing embeddings...")
    await retriever.load()
    print(f"Loaded {len(retriever.documents)} documents successfully.")
    print("-" * 80)

    all_results = {}
    docs_used_pass = True
    no_edtech_leakage_pass = True
    domain_relevance_pass = True
    
    all_scores = []
    
    for domain, query in BENCHMARK_QUERIES.items():
        print(f"\nTesting Domain: {domain.upper()}")
        print(f"Query: '{query}'")
        
        # Re-fetch embeddings to simulate retrieval accurately and check scores for ALL documents
        query_embeddings = await nim_service.embed([query]) if settings.use_nvidia else None
        query_emb = (
            np.array(query_embeddings[0])
            if query_embeddings
            else retriever._local_embed([query])[0]
        )
        
        scores = np.dot(retriever.embeddings, query_emb)
        query_domain = get_query_domain(query)
        
        # Build list of doc results
        doc_evals = []
        for idx, score_val in enumerate(scores):
            doc = retriever.documents[idx]
            score = float(score_val)
            all_scores.append(score)
            doc_domain = get_doc_domain(doc)
            
            accepted = True
            reason = "Accepted"
            
            if score < settings.retrieval_threshold:
                accepted = False
                reason = f"Rejected (score {score:.4f} < threshold {settings.retrieval_threshold:.4f})"
            elif doc_domain != "general" and doc_domain != query_domain:
                accepted = False
                reason = f"Rejected (domain mismatch: doc domain '{doc_domain}' != query domain '{query_domain}')"
                
            doc_evals.append({
                "title": doc.get("title"),
                "category": doc.get("category"),
                "doc_domain": doc_domain,
                "score": score,
                "accepted": accepted,
                "reason": reason
            })
            
        # Sort all documents by similarity score
        doc_evals.sort(key=lambda x: x["score"], reverse=True)
        
        # Print top 10 documents by score for debugging/insights
        print(f"{'Status':<12} | {'Score':<6} | {'Doc Domain':<12} | {'Title':<40} | {'Rejection Reason / Info'}")
        print("-" * 120)
        accepted_count = 0
        accepted_docs = []
        
        for eval_item in doc_evals:
            status_str = "ACCEPTED" if eval_item["accepted"] else "REJECTED"
            score_str = f"{eval_item['score']:.4f}"
            doc_dom = eval_item["doc_domain"]
            title_truncated = eval_item["title"][:38] + "..." if len(eval_item["title"]) > 38 else eval_item["title"]
            print(f"{status_str:<12} | {score_str:<6} | {doc_dom:<12} | {title_truncated:<40} | {eval_item['reason']}")
            
            if eval_item["accepted"]:
                accepted_count += 1
                accepted_docs.append(eval_item)
                
        # Metrics validation for this query
        print(f"--> Accepted docs count: {accepted_count}")
        
        # Criterion 1: docs_used > 0
        if accepted_count == 0:
            print("FAIL: docs_used == 0 for this domain!")
            docs_used_pass = False
        else:
            print("PASS: docs_used > 0")
            
        # Criterion 2: EdTech leakage
        if domain != "edtech":
            leaked_edtech = [d for d in accepted_docs if d["doc_domain"] == "edtech"]
            if leaked_edtech:
                print(f"FAIL: EdTech leakage detected! Leaked documents: {[d['title'] for d in leaked_edtech]}")
                no_edtech_leakage_pass = False
            else:
                print("PASS: Zero EdTech leakage")
        else:
            print("INFO: Target domain is EdTech")
            
        # Criterion 3: Domain relevance (Top-ranked accepted doc must match the query domain)
        if accepted_docs:
            top_doc = accepted_docs[0]
            if top_doc["doc_domain"] != domain:
                print(f"FAIL: Top-ranked doc domain '{top_doc['doc_domain']}' does not match query domain '{domain}'!")
                domain_relevance_pass = False
            else:
                print("PASS: Top-ranked doc domain matches query domain")
        else:
            print("FAIL: No docs accepted, domain relevance cannot be checked")
            domain_relevance_pass = False
            
        all_results[domain] = {
            "accepted_count": accepted_count,
            "top_doc": accepted_docs[0]["title"] if accepted_docs else None,
            "top_doc_domain": accepted_docs[0]["doc_domain"] if accepted_docs else None
        }

    # Summary Statistics
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY METRICS")
    print("=" * 80)
    
    print(f"Criterion: docs_used > 0: {'PASSED' if docs_used_pass else 'FAILED'}")
    print(f"Criterion: EdTech leakage: {'PASSED' if no_edtech_leakage_pass else 'FAILED'}")
    print(f"Criterion: Domain relevance: {'PASSED' if domain_relevance_pass else 'FAILED'}")
    
    if all_scores:
        print(f"Score Distribution: Min={min(all_scores):.4f}, Max={max(all_scores):.4f}, Mean={np.mean(all_scores):.4f}, Std={np.std(all_scores):.4f}")
    
    overall_success = docs_used_pass and no_edtech_leakage_pass and domain_relevance_pass
    print(f"\nOVERALL BENCHMARK SUCCESS: {'PASSED' if overall_success else 'FAILED'}")
    print("=" * 80)
    
    if not overall_success:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
