"""Live research layer for external web retrieval and source grounding."""

import logging
import re
import urllib.parse
from typing import Any

import httpx

from app.services.evidence_utils import MAX_SNIPPET_LENGTH, MAX_URL_LENGTH, normalize_url, utc_now_iso

logger = logging.getLogger(__name__)


class LiveResearchService:
    """Service to fetch real-time startup/industry context and ground claims in evidence."""

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
            timeout=15.0,
        )

    def clean_url(self, url: str) -> str:
        """Resolve DuckDuckGo redirect links, strip tracking parameters, and truncate long URLs."""
        return normalize_url(url, max_length=MAX_URL_LENGTH)

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Run query against live search engine and parse results. Returns empty list on failure."""
        results = []
        try:
            logger.info("Executing live research query: %s", query)
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Regex patterns to extract titles, urls, and snippets from DDG HTML
            # Results look like: <a class="result__snippet" href="..."> ... </a>
            # or <a class="result__url" href="..."> ... </a>
            html_content = response.text
            
            # Simple parsing block
            matches = re.findall(
                r'<a class="result__snippet"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                html_content,
                re.DOTALL
            )
            
            title_matches = re.findall(
                r'<a class="result__title"[^>]*>(.*?)</a>',
                html_content,
                re.DOTALL
            )

            for i, match in enumerate(matches[:top_k]):
                raw_url = match[0]
                # Decouple DDG proxy links if present
                if "uddg=" in raw_url:
                    parsed = urllib.parse.urlparse(raw_url)
                    qs = urllib.parse.parse_qs(parsed.query)
                    url_val = qs.get("uddg", [raw_url])[0]
                else:
                    url_val = raw_url

                url_val = self.clean_url(url_val)
                snippet = re.sub(r'<[^>]*>', '', match[1]).strip()
                snippet = snippet[:MAX_SNIPPET_LENGTH]
                title = "Search Result"
                if i < len(title_matches):
                    title = re.sub(r'<[^>]*>', '', title_matches[i]).strip()

                results.append({
                    "title": title or f"Research Analysis from {urllib.parse.urlparse(url_val).netloc}",
                    "url": url_val,
                    "snippet": snippet,
                    "timestamp": utc_now_iso(),
                    "confidence_score": 0.85
                })
            
            if results:
                logger.info("Live research success. Found %d sources.", len(results))
                return results

        except Exception as e:
            logger.warning("Live search query failed (%s). Returning empty research logs.", e)
        
        return []

live_researcher = LiveResearchService()
