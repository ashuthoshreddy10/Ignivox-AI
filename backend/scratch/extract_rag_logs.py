import os

log_path = r"C:\Users\npsan\.gemini\antigravity-ide\brain\715c005a-2d80-4a21-ba97-f9730892de34\.system_generated\tasks\task-139.log"
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        # Check if the line has the log from the later run (starts with timestamp after 13:17:00)
        if "2026-06-23 13:17" in line or "2026-06-23 13:18" in line or "2026-06-23 13:19" in line:
            if "RAG docs for" in line or "RAG Context Item" in line:
                print(line.strip())
