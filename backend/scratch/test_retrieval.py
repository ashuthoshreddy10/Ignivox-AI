import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.live_research import live_researcher

async def test():
    query = "Helios Grid: AI-powered smart energy optimization platform Competitor"
    print(f"Searching for: {query}")
    results = await live_researcher.search(query, top_k=5)
    for i, res in enumerate(results):
        print(f"\n[{i+1}] Title: {res.get('title')}")
        print(f"    URL: {res.get('url')}")
        print(f"    Snippet: {res.get('snippet')}")

if __name__ == "__main__":
    asyncio.run(test())
