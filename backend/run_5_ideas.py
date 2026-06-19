import asyncio
import json
import sys
import websockets

IDEAS = [
    "AI placement preparation platform for college students",
    "Smart grid anomaly detection telemetry and SCADA monitoring",
    "Secure patient portals and medical diagnostics with HIPAA audit logging",
    "SIEM log threat predictor and firewall anomaly detection",
    "Brain-Computer Interface cloud controller for telepathic data exchange"
]

async def run_idea(idea: str, uri: str):
    print(f"\n==================================================")
    print(f"RUNNING IDEA: {idea}")
    print(f"==================================================")
    try:
        async with websockets.connect(uri, open_timeout=15) as ws:
            await ws.send(json.dumps({"idea": idea}))
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=120)
                data = json.loads(msg)
                event_type = data.get("type")
                message = str(data.get("message", ""))
                
                if event_type == "agent_complete":
                    print(f"  [COMPLETE] {data.get('agent')} analysis completed.")
                elif event_type == "result":
                    bp = data.get("blueprint", {})
                    score = bp.get("score", {}).get("overall")
                    print(f"SUCCESS: Blueprint completed. Overall Score: {score}")
                    return
                elif event_type == "error":
                    print(f"ERROR: {message}")
                    return
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

async def main():
    uri = "ws://127.0.0.1:8000/api/ws/generate"
    for idea in IDEAS:
        await run_idea(idea, uri)

if __name__ == "__main__":
    asyncio.run(main())
