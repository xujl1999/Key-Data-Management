@echo off
if "%SHORTCUT_TOKEN%"=="" set "SHORTCUT_TOKEN=demo-token"
if "%QWEN_API_KEY%"=="" (
  for /f "tokens=2,*" %%A in ('C:\Windows\System32\reg.exe query HKCU\Environment /v QWEN_API_KEY 2^>NUL') do set "QWEN_API_KEY=%%B"
)
"%LocalAppData%\\Programs\\Python\\Python312\\python.exe" -m uvicorn food_service.app:app --host 127.0.0.1 --port 8787
