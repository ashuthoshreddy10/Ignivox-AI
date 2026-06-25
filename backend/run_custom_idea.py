import asyncio
import json
import sys
from pathlib import Path
import websockets

async def run_idea(idea: str, uri: str, timeout: float = 600):
    print(f"Connecting to server at: {uri}")
    print(f"Running startup idea: {idea}\n")
    try:
        async with websockets.connect(uri, open_timeout=15) as ws:
            await ws.send(json.dumps({"idea": idea}))
            print("Request sent. Analyzing steps...")
            
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                data = json.loads(msg)
                event_type = data.get("type")
                progress = data.get("progress", 0)
                message = str(data.get("message", ""))
                
                if event_type == "agent_working":
                    print(f"  [WORKING] {message} (Progress: {progress:.0f}%)")
                elif event_type == "agent_complete":
                    print(f"  [COMPLETE] {message} (Progress: {progress:.0f}%)")
                elif event_type == "workflow_start":
                    print(f"  [START] {message}")
                elif event_type == "workflow_complete":
                    print(f"  [FINISH] {message}")
                elif event_type == "result":
                    bp = data.get("blueprint", {})
                    score = bp.get("score", {}).get("overall")
                    print(f"\nSUCCESS: Startup Blueprint generated successfully!")
                    print(f"Overall Feasibility Score: {score}/100\n")
                    
                    # Save the full blueprint JSON
                    out_path = Path("custom_blueprint.json")
                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(bp, f, indent=2)
                    print(f"Saved complete blueprint JSON to: {out_path.resolve()}")
                    return 0
                elif event_type == "error":
                    print(f"\nERROR received from server: {message}")
                    return 1
                else:
                    print(f"  [{event_type.upper()}] {message}")
    except Exception as e:
        print(f"\nExecution failed: {type(e).__name__}: {e}")
        return 1

if __name__ == "__main__":
    idea = sys.argv[1] if len(sys.argv) > 1 else "AI placement preparation platform for college students"
    uri = "ws://127.0.0.1:8000/api/ws/generate"
    sys.exit(asyncio.run(run_idea(idea, uri)))
