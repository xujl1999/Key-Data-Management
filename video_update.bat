@echo off
setlocal

rem Move to script directory.
cd /d "%~dp0"

set "CONDA_ROOT=%USERPROFILE%\Miniconda3"

if not exist "%CONDA_ROOT%\Scripts\activate.bat" goto no_conda
call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ROOT%"
goto conda_active

:no_conda
echo Conda activate.bat not found at "%CONDA_ROOT%\Scripts\activate.bat".
exit /b 1

:conda_active
call conda activate base
if errorlevel 1 exit /b %errorlevel%

pushd "%~dp0video"

echo Running get_video_ls.py...
python get_video_ls.py
if errorlevel 1 goto py_error

echo Running normalize_publish_date.py...
python normalize_publish_date.py
if errorlevel 1 goto py_error

popd
endlocal
exit /b 0

:py_error
popd
echo Python script failed.
exit /b 1
