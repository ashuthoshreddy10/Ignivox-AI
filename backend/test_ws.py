import asyncio
import json
import sys

import websockets


async def test(uri: str, timeout: float = 300) -> int:
    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri, open_timeout=10) as ws:
            await ws.send(json.dumps({"idea": "AI placement prep for college students"}))
            print("Sent idea, waiting for events...")
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                data = json.loads(msg)
                event_type = data.get("type")
                progress = data.get("progress", 0)
                message = str(data.get("message", ""))[:80]
                print(f"  {event_type} | progress={progress:.0f} | {message}")
                if event_type == "result":
                    score = data.get("blueprint", {}).get("score", {}).get("overall")
                    print(f"SUCCESS: workflow completed | score={score}")
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
