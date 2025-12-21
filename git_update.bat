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

"%GIT_EXE%" pull --rebase origin main
if errorlevel 1 exit /b %errorlevel%

set RETRIES=5
set COUNT=0
:push_retry
set /a COUNT+=1
"%GIT_EXE%" push origin main
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
