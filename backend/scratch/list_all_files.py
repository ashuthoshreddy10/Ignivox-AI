import os

for root, dirs, files in os.walk(r"c:\Users\npsan\ignivox-ai"):
    # ignore .git and venv
    dirs[:] = [d for d in dirs if d not in [".git", "venv", "node_modules", ".pytest_cache"]]
    for file in files:
        print(os.path.join(root, file))
