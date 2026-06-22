import re
import json

def compute_jaccard_similarity(text1: str, text2: str) -> float:
    t1 = str(text1).lower().strip()
    t2 = str(text2).lower().strip()
    if not t1 or not t2:
        return 0.0
        
    def get_trigrams(text: str) -> set[str]:
        cleaned = re.sub(r"[^a-z0-9]", "", text)
        if len(cleaned) < 3:
            return {cleaned} if cleaned else set()
        return {cleaned[i:i+3] for i in range(len(cleaned)-2)}

    def get_tokens(text: str) -> set[str]:
        words = re.findall(r"\b[a-z0-9]{3,}\b", text)
        stopwords = {
            "and", "or", "but", "the", "with", "for", "from", "their", "our", "your",
            "this", "that", "these", "those", "have", "has", "had", "been", "should", "would",
            "are", "was", "were", "is", "its", "it", "to", "in", "at", "by", "of"
        }
        return {w for w in words if w not in stopwords}

    tg1 = get_trigrams(t1)
    tg2 = get_trigrams(t2)
    tok1 = get_tokens(t1)
    tok2 = get_tokens(t2)
    
    tg_sim = len(tg1.intersection(tg2)) / len(tg1.union(tg2)) if tg1 and tg2 else 0.0
    tok_sim = len(tok1.intersection(tok2)) / len(tok1.union(tok2)) if tok1 and tok2 else 0.0
    return 0.5 * tg_sim + 0.5 * tok_sim

def compute_overlap_similarity(text1: str, text2: str) -> float:
    t1 = str(text1).lower().strip()
    t2 = str(text2).lower().strip()
    if not t1 or not t2:
        return 0.0
        
    def get_trigrams(text: str) -> set[str]:
        cleaned = re.sub(r"[^a-z0-9]", "", text)
        if len(cleaned) < 3:
            return {cleaned} if cleaned else set()
        return {cleaned[i:i+3] for i in range(len(cleaned)-2)}

    def get_tokens(text: str) -> set[str]:
        words = re.findall(r"\b[a-z0-9]{3,}\b", text)
        stopwords = {
            "and", "or", "but", "the", "with", "for", "from", "their", "our", "your",
            "this", "that", "these", "those", "have", "has", "had", "been", "should", "would",
            "are", "was", "were", "is", "its", "it", "to", "in", "at", "by", "of"
        }
        return {w for w in words if w not in stopwords}

    tg1 = get_trigrams(t1)
    tg2 = get_trigrams(t2)
    tok1 = get_tokens(t1)
    tok2 = get_tokens(t2)
    
    tg_sim = len(tg1.intersection(tg2)) / min(len(tg1), len(tg2)) if tg1 and tg2 else 0.0
    tok_sim = len(tok1.intersection(tok2)) / min(len(tok1), len(tok2)) if tok1 and tok2 else 0.0
    return 0.5 * tg_sim + 0.5 * tok_sim

with open("grounding_audit_log.json", "r", encoding="utf-8") as f:
    log = json.load(f)

for i, entry in enumerate(log[:10]):
    c = entry.get('claim')
    sn = entry.get('source_snippet')
    js = compute_jaccard_similarity(c, sn)
    os_val = compute_overlap_similarity(c, sn)
    print(f"\n[{i+1}] Claim: {c}")
    print(f"    Snippet: {sn[:100]}...")
    print(f"    Jaccard Similarity : {js:.4f}")
    print(f"    Overlap Similarity : {os_val:.4f}")
