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

python health\scripts\update_from_onedrive.py --no-wait
if errorlevel 1 exit /b %errorlevel%

python health\scripts\parse_export.py
if errorlevel 1 exit /b %errorlevel%

node health\scripts\build_sleep_schedule.js
if errorlevel 1 exit /b %errorlevel%

python health\scripts\summarize_last7.py
if errorlevel 1 exit /b %errorlevel%

endlocal
