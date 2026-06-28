import os

log_path = r"C:\Users\npsan\.gemini\antigravity-ide\brain\715c005a-2d80-4a21-ba97-f9730892de34\.system_generated\tasks\task-139.log"
if not os.path.exists(log_path):
    print("Log path does not exist!")
    exit(1)

print("Searching log lines...")
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        # Print lines around Market Research Agent startup in the successful runs
        if "Market Research Agent is analyzing" in line or "RAG docs for" in line:
            print(line.strip())
