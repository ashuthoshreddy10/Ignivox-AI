"""Live research layer for external web retrieval and source grounding."""

import asyncio
import logging
import random
import re
import sys
import urllib.parse
from typing import Any

import httpx

from app.config import settings
from app.services.evidence_utils import MAX_SNIPPET_LENGTH, MAX_URL_LENGTH, normalize_url, utc_now_iso

logger = logging.getLogger(__name__)

REALISTIC_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]


class DuckDuckGoBlockedError(Exception):
    """Exception raised when DuckDuckGo appears to block or rate-limit the request."""
    pass


class LiveResearchResult(list):
    """Subclass of list to hold search results and optional fallback/error metadata."""
    def __init__(self, items=None, fallback: bool = False, reason: str | None = None) -> None:
        super().__init__(items or [])
        self.fallback = fallback
        self.reason = reason


def detect_ddg_block(response: httpx.Response) -> None:
    """Inspects the HTTP response for signs of blocking (status 202, CAPTCHA body text, zero results)
    and raises a specific DuckDuckGoBlockedError if any are found.
    """
    if response.status_code == 202:
        raise DuckDuckGoBlockedError("DuckDuckGo returned status code 202 (Accepted/Challenged)")
    
    body_lower = response.text.lower()
    captcha_keywords = [
        "captcha", "ddg-captcha", "checking your browser", 
        "ddg-lms", "automated requests", "robot"
    ]
    if any(kw in body_lower for kw in captcha_keywords):
        raise DuckDuckGoBlockedError("DuckDuckGo CAPTCHA or robot challenge page detected in response body")
    
    # Check for zero results. When DDG blocks/fails or has no results, "result__snippet" won't be in the body.
    if "result__snippet" not in response.text:
        raise DuckDuckGoBlockedError("No search results found in the DuckDuckGo response")


class LiveResearchService:
    """Service to fetch real-time startup/industry context and ground claims in evidence."""

    def __init__(self) -> None:
        self._force_jitter_sleep_for_testing = False
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

    async def _execute_scrape(self, url: str, user_agent: str, top_k: int) -> list[dict[str, Any]]:
        """Scrapes DuckDuckGo with the provided user-agent and parses results. Raises DuckDuckGoBlockedError on block."""
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://duckduckgo.com/",
            "DNT": "1",
        }
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()

        detect_ddg_block(response)

        html_content = response.text
        
        # Regex patterns to extract titles, urls, and snippets from DDG HTML
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

        results = []
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

        return results

    async def search(self, query: str, top_k: int = 5) -> LiveResearchResult:
        """Run query against live search engine and parse results. Returns LiveResearchResult."""
        if settings.demo_mode:
            logger.info("Demo mode active. Returning mock search results for query: %s", query)
            return LiveResearchResult([
                {
                    "title": f"Demo Research: {query}",
                    "url": "https://example.com/demo-research",
                    "snippet": f"This is a mocked demo research snippet for the query '{query}'.",
                    "timestamp": utc_now_iso(),
                    "confidence_score": 0.85
                }
            ])

        # Dynamic jitter handling based on pytest bypass rule
        if "pytest" not in sys.modules or self._force_jitter_sleep_for_testing:
            await asyncio.sleep(random.uniform(1.5, 3.5))

        logger.info("Executing live research query: %s", query)
        
        ua_primary = random.choice(REALISTIC_AGENTS)
        remaining = [ua for ua in REALISTIC_AGENTS if ua != ua_primary]
        ua_fallback = random.choice(remaining) if remaining else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        # First attempt
        try:
            results = await self._execute_scrape(url, ua_primary, top_k)
            logger.info("Live research success on first attempt. Found %d sources.", len(results))
            return LiveResearchResult(results)
        except Exception as e:
            logger.warning("First live search attempt failed: %s. Initiating fallback...", e, exc_info=True)
            last_exception = e

        # Fallback 1: Retry once with a 2-second delay and a different User-Agent
        try:
            await asyncio.sleep(2.0)
            results = await self._execute_scrape(url, ua_fallback, top_k)
            logger.info("Live research success on second attempt. Found %d sources.", len(results))
            return LiveResearchResult(results)
        except Exception as e:
            logger.warning("Second live search attempt failed: %s.", e, exc_info=True)
            last_exception = e

        # Fallback 2: both failed, return an empty live_sources list with metadata
        return LiveResearchResult(fallback=True, reason=str(last_exception))


live_researcher = LiveResearchService()
