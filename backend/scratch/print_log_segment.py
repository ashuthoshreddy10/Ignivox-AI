import os

log_path = r"C:\Users\npsan\.gemini\antigravity-ide\brain\715c005a-2d80-4a21-ba97-f9730892de34\.system_generated\tasks\task-139.log"
with open(log_path, "r", encoding="utf-8") as f:
    printing = False
    for line in f:
        if "2026-06-23 13:17:35" in line:
            printing = True
        if "2026-06-23 13:18:15" in line:
            printing = False
        if printing:
            print(line.strip())
