@echo off
setlocal

D:
call C:\Users\23711\Miniconda3\Scripts\activate.bat C:\Users\23711\Miniconda3
call conda activate base

cd /d D:\dream_life\data-management\video
python get_video_ls.py
python normalize_publish_date.py

endlocal
