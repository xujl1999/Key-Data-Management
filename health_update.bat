@echo off
setlocal

D:
call C:\Users\23711\Miniconda3\Scripts\activate.bat C:\Users\23711\Miniconda3
call conda activate base

cd /d D:\dream_life\data-management
python health\update_from_onedrive.py --no-wait

if errorlevel 1 exit /b %errorlevel%
node health\build_sleep_schedule.js
if errorlevel 1 exit /b %errorlevel%
python health\summarize_last7.py
if errorlevel 1 exit /b %errorlevel%
python health\plot_trends.py
if errorlevel 1 exit /b %errorlevel%
python health\plot_all_metrics.py
if errorlevel 1 exit /b %errorlevel%
node health\plot_all_metrics_svg.js
if errorlevel 1 exit /b %errorlevel%

endlocal
