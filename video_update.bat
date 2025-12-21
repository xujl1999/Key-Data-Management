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

pushd "%~dp0video"
python get_video_ls.py
if errorlevel 1 (
  popd
  exit /b %errorlevel%
)
python normalize_publish_date.py
if errorlevel 1 (
  popd
  exit /b %errorlevel%
)
popd

endlocal
