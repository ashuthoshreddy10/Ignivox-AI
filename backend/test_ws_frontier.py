import asyncio
import json
import sys

import websockets


async def test(uri: str, timeout: float = 300) -> int:
    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri, open_timeout=10) as ws:
            # Idea containing 'brain' to trigger Frontier Mode (novelty_score = 88 > 70)
            await ws.send(json.dumps({"idea": "Brain-Computer Cloud interface for telepathic data exchange"}))
            print("Sent frontier idea, waiting for events...")
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                data = json.loads(msg)
                event_type = data.get("type")
                progress = data.get("progress", 0)
                message = str(data.get("message", ""))[:80]
                print(f"  {event_type} | progress={progress:.0f} | {message}")
                if event_type == "result":
                    bp = data.get("blueprint", {})
                    score = bp.get("score", {}).get("overall")
                    novelty = bp.get("novelty_detection", {}).get("content", {})
                    print(f"SUCCESS: workflow completed | score={score}")
                    print(f"Novelty Score: {novelty.get('novelty_score')}/100")
                    print(f"Market Type: {novelty.get('market_classification')}")
                    print(f"Evidence Coverage: {novelty.get('evidence_coverage_est')}")
                    print(f"Speculative Content: {novelty.get('speculative_content_ratio')}")
                    
                    # Verify Competitor Analysis keys under Frontier Mode
                    competitor = bp.get("competitor_analysis", {}).get("content", {})
                    print("Competitor keys:", list(competitor.keys()))
                    return 0
                if event_type == "error":
                    print("ERROR:", data.get("message"))
                    return 1
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ws://127.0.0.1:8000/api/ws/generate"
    raise SystemExit(asyncio.run(test(target)))
