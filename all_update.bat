@echo off
setlocal

call D:\dream_life\data-management\health_update.bat
if errorlevel 1 exit /b %errorlevel%

call D:\dream_life\data-management\video_update.bat
if errorlevel 1 exit /b %errorlevel%

call D:\dream_life\data-management\git_update.bat

endlocal
