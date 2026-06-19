"""Agent memory system for storing analyses and learned patterns."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class AgentMemory:
    """Persistent memory for startup analyses and user history."""

    def __init__(self) -> None:
        self._path = Path(__file__).resolve().parent.parent.parent / settings.memory_db_path
        self._path.mkdir(parents=True, exist_ok=True)
        self._history_file = self._path / "history.json"
        self._insights_file = self._path / "market_insights.json"
        self._history: list[dict] = self._load(self._history_file, [])
        self._insights: list[dict] = self._load(self._insights_file, [])

    def _load(self, path: Path, default: list) -> list:
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Failed to load %s: %s", path, e)
        return default

    def _save(self, path: Path, data: list) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def store_analysis(self, blueprint_id: str, idea: str, score: float, summary: dict[str, Any]) -> None:
        entry = {
            "id": blueprint_id,
            "idea": idea,
            "score": score,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._history.insert(0, entry)
        self._history = self._history[:100]
        self._save(self._history_file, self._history)

    def store_insight(self, category: str, insight: str, source: str) -> None:
        self._insights.append({
            "category": category,
            "insight": insight,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._insights = self._insights[-500:]
        self._save(self._insights_file, self._insights)

    def get_history(self, limit: int = 20) -> list[dict]:
        return self._history[:limit]

    def get_relevant_insights(self, query: str, limit: int = 5) -> list[dict]:
        query_lower = query.lower()
        scored = []
        for insight in self._insights:
            text = f"{insight.get('category', '')} {insight.get('insight', '')}".lower()
            score = sum(1 for word in query_lower.split() if word in text and len(word) > 3)
            if score > 0:
                scored.append((score, insight))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    def get_patterns(self) -> dict[str, Any]:
        if not self._history:
            return {"total_analyses": 0, "avg_score": 0, "top_industries": []}

        scores = [h.get("score", 0) for h in self._history]
        industries: dict[str, int] = {}
        for h in self._history:
            industry = h.get("summary", {}).get("industry", "unknown")
            industries[industry] = industries.get(industry, 0) + 1

        top = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]
        return {
            "total_analyses": len(self._history),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "top_industries": [{"industry": k, "count": v} for k, v in top],
        }


memory = AgentMemory()
