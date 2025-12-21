@echo off
setlocal

rem Move to script directory.
cd /d "%~dp0"

git add -A
git diff --cached --quiet
if %errorlevel%==0 (
  echo No changes to commit.
) else (
  git commit -m "update data"
  if errorlevel 1 exit /b %errorlevel%
)

git pull --rebase origin main
if errorlevel 1 exit /b %errorlevel%

set RETRIES=5
set COUNT=0
:push_retry
set /a COUNT+=1
git push origin main
if %errorlevel%==0 goto push_done
if %COUNT% GEQ %RETRIES% goto push_fail
echo Push failed, retrying (%COUNT%/%RETRIES%)...
timeout /t 5 /nobreak >nul
goto push_retry

:push_done
echo Push succeeded.
goto end

:push_fail
echo Push failed after %RETRIES% attempts.
exit /b 1

:end
endlocal
