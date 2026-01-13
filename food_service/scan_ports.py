import requests

ports = [9999, 8000, 8080, 8181, 11434, 1234, 5000, 3000]
print("Scanning for local LLM APIs...")
found = None
for port in ports:
    try:
        # Try OpenAI style /v1/models
        url = f"http://127.0.0.1:{port}/v1/models"
        resp = requests.get(url, timeout=0.5)
        if resp.status_code == 200:
            print(f"FOUND API AT: http://127.0.0.1:{port}/v1")
            found = f"http://127.0.0.1:{port}/v1"
            break
    except:
        pass
    
    try:
        # Try root
        url = f"http://127.0.0.1:{port}/"
        resp = requests.get(url, timeout=0.5)
        if resp.status_code == 200:
            print(f"Service active at: http://127.0.0.1:{port}/")
    except:
        pass

if not found:
    print("No standard OpenAI-compatible API found.")
