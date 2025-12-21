@echo off
setlocal

D:
cd /d D:\dream_life\data-management

git pull origin main
git add -A
for /f %%i in ('git status --porcelain') do set CHANGES=1
if defined CHANGES (
  git commit -m "update data"
) else (
  echo No changes to commit.
)

set RETRIES=3
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
