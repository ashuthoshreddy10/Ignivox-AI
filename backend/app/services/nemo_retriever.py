"""NeMo Retriever-style RAG knowledge retrieval."""

import json
import logging
from pathlib import Path

import numpy as np

from app.config import settings
from app.services.nvidia_nim import nim_service
from app.services.evidence_utils import utc_now_iso

logger = logging.getLogger(__name__)


class RetrievalList(list):
    """Subclass of list to hold RAG filtering metadata."""
    def __init__(self, items, total_retrieved=0, docs_filtered=0):
        super().__init__(items)
        self.total_retrieved = total_retrieved
        self.docs_filtered = docs_filtered


class NeMoRetriever:
    """RAG knowledge base using NVIDIA embeddings + vector search."""

    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.embeddings: np.ndarray | None = None
        self._loaded = False
        self._initializing = False
        self._mode = "uninitialized"

    @property
    def retriever_mode(self) -> str:
        """Returns the current operating mode of the retriever: 'nim_embeddings', 'local_fallback', or 'uninitialized'."""
        return self._mode

    def _knowledge_path(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / settings.knowledge_dir

    async def force_reinitialize(self) -> bool:
        """Retry NIM embedding initialization by clearing cache/state and loading again."""
        if self._initializing:
            return False  # already in progress, skip

        self._initializing = True
        try:
            logger.info("Forcing re-initialization of NeMoRetriever...")
            self._loaded = False
            self.documents = []
            self.embeddings = None
            self._mode = "uninitialized"
            await self._initialize_embeddings()
            return True
        finally:
            self._initializing = False

    async def load(self) -> None:
        if self._loaded:
            return
        if self._initializing:
            return  # already loading, skip duplicate

        self._initializing = True
        try:
            await self._initialize_embeddings()
        finally:
            self._initializing = False

    async def _initialize_embeddings(self) -> None:
        """Internal method to load knowledge docs and generate embeddings."""
        knowledge_path = self._knowledge_path()
        if not knowledge_path.exists():
            knowledge_path.mkdir(parents=True, exist_ok=True)

        for file_path in knowledge_path.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.documents.extend(data)
                    elif isinstance(data, dict):
                        self.documents.append(data)
            except Exception as e:
                logger.warning("Failed to load %s: %s", file_path, e)

        if self.documents:
            texts = [f"{d.get('title', '')}: {d.get('content', '')}" for d in self.documents]
            if settings.use_nvidia:
                try:
                    embeddings = await nim_service.embed(texts)
                    if embeddings:
                        self.embeddings = np.array(embeddings)
                        self._mode = "nim_embeddings"
                    else:
                        logger.warning("NIM embedding API returned empty results. Falling back to local embeddings.")
                        self.embeddings = self._local_embed(texts)
                        self._mode = "local_fallback"
                except Exception as e:
                    logger.warning("NIM embedding API failed: %s. Falling back to local embeddings.", e)
                    self.embeddings = self._local_embed(texts)
                    self._mode = "local_fallback"
            else:
                self.embeddings = self._local_embed(texts)
                self._mode = "local_fallback"
        else:
            self.embeddings = None
            self._mode = "local_fallback"

        self._loaded = True
        logger.info("Loaded %d knowledge documents. Mode: %s", len(self.documents), self._mode)

    def _local_embed(self, texts: list[str]) -> np.ndarray:
        """Fallback local embeddings for demo mode."""
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

    def _query_embed(self, query: str) -> np.ndarray:
        if settings.use_nvidia:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return self._local_embed([query])[0]
            embeddings = loop.run_until_complete(nim_service.embed([query]))
            return np.array(embeddings[0])
        return self._local_embed([query])[0]

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        await self.load()

        if not self.documents or self.embeddings is None:
            return []

        query_embeddings = await nim_service.embed([query]) if settings.use_nvidia else None
        query_emb = (
            np.array(query_embeddings[0])
            if query_embeddings
            else self._local_embed([query])[0]
        )

        # Check for dimension alignment to prevent matrix dot product exceptions
        if self.embeddings.shape[1] != query_emb.shape[0]:
            expected_dim = self.embeddings.shape[1]
            actual_dim = query_emb.shape[0]

            warning_data = {
                "expected_dim": expected_dim,
                "actual_dim": actual_dim,
                "fallback_method": "character_hash",
                "timestamp": utc_now_iso()
            }
            logger.warning("Dimension mismatch detected: %s", json.dumps(warning_data))

            self._mode = "local_fallback"
            self._loaded = False
            await self.load()
            
            if self.embeddings.shape[1] != query_emb.shape[0]:
                logger.warning("Dimension mismatch persists after reload. Forcing local fallback embeddings for both database and query.")
                texts = [f"{d.get('title', '')}: {d.get('content', '')}" for d in self.documents]
                self.embeddings = self._local_embed(texts)
                query_emb = self._local_embed([query])[0]

        # Determine current threshold based on retriever mode
        threshold = 0.35
        if self._mode == "local_fallback":
            threshold = 0.20
            logger.info("Operating in local_fallback mode. Adjusted relevance threshold from 0.35 to 0.20.")

        scores = np.dot(self.embeddings, query_emb)
        
        # Determine current idea domain based on query keywords (checking whole words to prevent false substring matches like 'class' in 'classifies')
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
        
        idea_domain = "general"
        if any(w in query_words for w in edtech_keywords):
            idea_domain = "edtech"
        elif any(w in query_words for w in health_keywords):
            idea_domain = "healthtech"
        elif any(w in query_words for w in fintech_keywords):
            idea_domain = "fintech"
        elif any(w in query_words for w in industrial_keywords) or "predictive maintenance" in query_lower or "digital twin" in query_lower:
            idea_domain = "industrial"
        elif any(w in query_words for w in energy_keywords):
            idea_domain = "energy"
        elif any(w in query_words for w in cyber_keywords) or "threat predictor" in query_lower:
            idea_domain = "cybersecurity"
        elif any(w in query_words for w in frontier_keywords) or "collective intelligence" in query_lower:
            idea_domain = "frontier"
        elif any(w in query_words for w in logistics_keywords) or "supply chain" in query_lower:
            idea_domain = "logistics"
        elif any(w in query_words for w in climatetech_keywords) or "carbon credit" in query_lower or "esg tracking" in query_lower:
            idea_domain = "climatetech"
        elif any(w in query_words for w in enterprise_saas_keywords):
            idea_domain = "enterprise_saas"
            
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

        filtered_candidates = []
        total_retrieved = len(scores)
        docs_filtered = 0

        for idx, score_val in enumerate(scores):
            doc = self.documents[idx].copy()
            doc["source_url"] = self.documents[idx].get("source_url", "")
            doc["source_title"] = self.documents[idx].get("source_title", "")
            score = float(score_val)
            doc["relevance_score"] = score
            
            # 1. Relevance score threshold check
            if score < threshold:
                docs_filtered += 1
                continue
                
            # 2. Domain matching check
            if idea_domain != "general":
                doc_domain = get_doc_domain(doc)
                if doc_domain != "general" and doc_domain != idea_domain:
                    docs_filtered += 1
                    continue
                
            filtered_candidates.append(doc)

        # Sort remaining candidates by similarity score descending
        filtered_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        results = filtered_candidates[:top_k]

        for doc in results:
            logger.info(
                "RAG Retrieval Audit | Query: '%s' | Document: '%s' | Category: '%s' | Similarity Score: %.4f",
                query,
                doc.get("title", "Untitled"),
                doc.get("category", "general"),
                doc.get("relevance_score", 0.0),
            )
        return RetrievalList(results, total_retrieved=total_retrieved, docs_filtered=docs_filtered)

    async def retrieve_for_context(self, query: str, top_k: int = 5) -> str:
        docs = await self.retrieve(query, top_k)
        if not docs:
            return "No relevant knowledge base entries found."
        parts = []
        for doc in docs:
            parts.append(
                f"[{doc.get('category', 'general')}] {doc.get('title', 'Untitled')}: "
                f"{doc.get('content', '')} (relevance: {doc.get('relevance_score', 0):.2f})"
            )
        return "\n".join(parts)


retriever = NeMoRetriever()
