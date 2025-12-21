@echo off
setlocal

rem Move to script directory.
cd /d "%~dp0"

if not defined GIT_EXE (
  for %%I in (git.exe) do set "GIT_EXE=%%~$PATH:I"
  if not defined GIT_EXE if exist "%ProgramFiles%\Git\cmd\git.exe" set "GIT_EXE=%ProgramFiles%\Git\cmd\git.exe"
  if not defined GIT_EXE if exist "%ProgramFiles%\Git\bin\git.exe" set "GIT_EXE=%ProgramFiles%\Git\bin\git.exe"
  if not defined GIT_EXE if exist "%ProgramFiles(x86)%\Git\cmd\git.exe" set "GIT_EXE=%ProgramFiles(x86)%\Git\cmd\git.exe"
  if not defined GIT_EXE if exist "%ProgramFiles(x86)%\Git\bin\git.exe" set "GIT_EXE=%ProgramFiles(x86)%\Git\bin\git.exe"
  if not defined GIT_EXE if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" set "GIT_EXE=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
  if not defined GIT_EXE if exist "%LOCALAPPDATA%\Programs\Git\bin\git.exe" set "GIT_EXE=%LOCALAPPDATA%\Programs\Git\bin\git.exe"
)

if not defined GIT_EXE (
  echo Git not found. Please install Git or add it to PATH.
  exit /b 1
)

"%GIT_EXE%" add -A
"%GIT_EXE%" diff --cached --quiet
if %errorlevel%==0 (
  echo No changes to commit.
) else (
  "%GIT_EXE%" commit -m "update data"
  if errorlevel 1 exit /b %errorlevel%
)

set RETRIES=5
set WAIT_SECONDS=5

set COUNT=0
:pull_retry
set /a COUNT+=1
"%GIT_EXE%" pull --rebase origin main
if %errorlevel%==0 goto pull_done
if exist ".git\\rebase-merge" goto pull_fail
if exist ".git\\rebase-apply" goto pull_fail
if %COUNT% GEQ %RETRIES% goto pull_fail
echo Pull failed, retrying (%COUNT%/%RETRIES%)...
call :sleep %WAIT_SECONDS%
goto pull_retry

:pull_done

set COUNT=0
:push_retry
set /a COUNT+=1
"%GIT_EXE%" push origin main
if %errorlevel%==0 goto push_done
if %COUNT% GEQ %RETRIES% goto push_fail
echo Push failed, retrying (%COUNT%/%RETRIES%)...
call :sleep %WAIT_SECONDS%
goto push_retry

:push_done
echo Push succeeded.
goto end

:push_fail
echo Push failed after %RETRIES% attempts.
exit /b 1

:pull_fail
echo Pull failed after %RETRIES% attempts.
exit /b 1

:sleep
set "S=%~1"
if "%S%"=="" set "S=5"
>nul 2>&1 timeout /t %S% /nobreak
if %errorlevel%==0 exit /b 0
>nul 2>&1 ping 127.0.0.1 -n %S% >nul
exit /b 0

:end
endlocal
