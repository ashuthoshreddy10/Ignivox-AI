import asyncio
import json
import sys

import websockets


async def test(uri: str, timeout: float = 600) -> int:
    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri, open_timeout=10) as ws:
            # Send the realistic industrial utility monitoring startup idea
            idea = "Sentinel Nexus: AI-powered infrastructure monitoring, SCADA sensor anomaly detection, and predictive maintenance for utility grids"
            await ws.send(json.dumps({"idea": idea}))
            print("Sent Sentinel Nexus idea, waiting for events...")
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
                    print(f"\nSUCCESS: workflow completed | score={score}")
                    
                    # 1. Verify Novelty Classification
                    novelty = bp.get("novelty_detection", {}).get("content", {})
                    print("\n--- NOVELTY DETECTION VERIFICATION ---")
                    print(f"Novelty Score: {novelty.get('novelty_score')}/100")
                    print(f"Market Type: {novelty.get('market_classification')}")
                    assert 35 <= novelty.get("novelty_score") <= 70, f"Expected Novelty Score to be between 35 and 70, got {novelty.get('novelty_score')}"
                    assert novelty.get("market_classification") == "Emerging Market", f"Expected Emerging Market, got {novelty.get('market_classification')}"
                    print("PASS: Novelty Detection classified correctly as Emerging Market (65/100).")

                    # 2. Verify Competitors
                    competitors = bp.get("competitor_analysis", {}).get("content", {}).get("competitors", {})
                    print("\n--- COMPETITOR HALLUCINATION VERIFICATION ---")
                    all_competitor_names = []
                    for cat, comps in competitors.items():
                        for comp in comps:
                            all_competitor_names.append(comp.get("name"))
                    print(f"Generated Competitor Names: {all_competitor_names}")
                    
                    # Ensure no competitor name contains "Sentinel"
                    for name in all_competitor_names:
                        assert "sentinel" not in name.lower(), f"Competitor name '{name}' contains the startup name 'Sentinel'!"
                    print("PASS: No fake competitor names contain the startup name 'Sentinel'.")

                    # 3. Verify Tech Stack Customization
                    tech_stack = bp.get("technical_architecture", {}).get("content", {}).get("tech_stack", {})
                    print("\n--- TECHNICAL ARCHITECTURE VERIFICATION ---")
                    frontend = tech_stack.get("frontend", {}).get("claim", "")
                    backend = tech_stack.get("backend", {}).get("claim", "")
                    database = tech_stack.get("database", {}).get("claim", "")
                    print(f"Frontend: {frontend}")
                    print(f"Backend: {backend}")
                    print(f"Database: {database}")
                    
                    assert "TimescaleDB" in database or "InfluxDB" in database, "Expected TimescaleDB/InfluxDB in the database stack!"
                    assert "Three.js" in frontend or "WebGL" in frontend, "Expected WebGL/Three.js in the frontend stack!"
                    assert "Kafka" in backend or "RabbitMQ" in backend, "Expected Kafka/RabbitMQ in the backend stack!"
                    print("PASS: Domain-specific industrial/energy architecture generated successfully.")
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
