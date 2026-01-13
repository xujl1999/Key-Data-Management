import os

print("Checking environment variables...")
for key, value in os.environ.items():
    if "API" in key or "URL" in key or "PROXY" in key or "TOKEN" in key:
        print(f"{key}: {value}")
