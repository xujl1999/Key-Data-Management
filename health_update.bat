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

set "NODE_EXE=node"
where node >nul 2>nul
if %errorlevel%==0 (
    echo Found node in PATH
    goto run_node
)

if exist "%ProgramFiles%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if exist "%ProgramFiles(x86)%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles(x86)%\nodejs\node.exe"
if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" set "NODE_EXE=%LOCALAPPDATA%\Programs\nodejs\node.exe"

:run_node
echo Using Node: "%NODE_EXE%"
"%NODE_EXE%" health\scripts\build_sleep_schedule.js
if errorlevel 1 (
    echo Failed to run build_sleep_schedule.js
    exit /b %errorlevel%
)

python health\scripts\summarize_last7.py
if errorlevel 1 exit /b %errorlevel%

endlocal
goto end

:onedrive_fail
echo OneDrive update failed after %RETRIES% attempts. Proceeding with existing local file...
goto onedrive_done

:end
