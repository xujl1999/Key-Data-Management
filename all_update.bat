@echo off
setlocal

rem Move to script directory.
cd /d "%~dp0"

call "%~dp0health_update.bat"
if errorlevel 1 goto error

call "%~dp0video_update.bat"
if errorlevel 1 goto error

call "%~dp0git_update.bat"
if errorlevel 1 goto error

echo.
echo === All updates completed successfully ===
goto end

:error
echo.
echo === Update failed with error ===

:end
endlocal
