@echo off
setlocal

rem Move to script directory.
cd /d "%~dp0"

set "CONDA_ROOT=%USERPROFILE%\Miniconda3"
if exist "%CONDA_ROOT%\Scripts\activate.bat" (
  call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ROOT%"
) else (
  echo Conda activate.bat not found at "%CONDA_ROOT%\Scripts\activate.bat".
  exit /b 1
)

call conda activate base
if errorlevel 1 exit /b %errorlevel%

set RETRIES=3
set COUNT=0
:onedrive_retry
set /a COUNT+=1
python health\scripts\update_from_onedrive.py --no-wait
if %errorlevel%==0 goto onedrive_done
if %COUNT% GEQ %RETRIES% goto onedrive_fail
echo OneDrive update failed, retrying (%COUNT%/%RETRIES%)...
timeout /t 5 /nobreak >nul
goto onedrive_retry

:onedrive_done

python health\scripts\parse_export.py
if errorlevel 1 exit /b %errorlevel%

rem Find Node.js - check WinGet path first (where it was actually installed)
set "NODE_EXE="

rem Check WinGet installation path
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\OpenJS.NodeJS*") do (
    for /d %%N in ("%%D\node-*") do (
        if exist "%%N\node.exe" set "NODE_EXE=%%N\node.exe"
    )
)

rem Fallback to standard locations
if not defined NODE_EXE if exist "%ProgramFiles%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if not defined NODE_EXE if exist "%ProgramFiles(x86)%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles(x86)%\nodejs\node.exe"
if not defined NODE_EXE if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" set "NODE_EXE=%LOCALAPPDATA%\Programs\nodejs\node.exe"

rem Final fallback - try PATH
if not defined NODE_EXE (
    for %%I in (node.exe) do set "NODE_EXE=%%~$PATH:I"
)

if not defined NODE_EXE (
    echo Node.js not found. Skipping build_sleep_schedule.js
    goto skip_node
)

echo Using Node: "%NODE_EXE%"
"%NODE_EXE%" health\scripts\build_sleep_schedule.js
if errorlevel 1 (
    echo Warning: build_sleep_schedule.js failed, continuing...
)

:skip_node

python health\scripts\summarize_last7.py
if errorlevel 1 exit /b %errorlevel%

endlocal
goto end

:onedrive_fail
echo OneDrive update failed after %RETRIES% attempts. Proceeding with existing local file...
goto onedrive_done

:end
