D:
call C:\Users\23711\Miniconda3\Scripts\activate.bat C:\Users\23711\Miniconda3
call conda activate base
cd D:\dream_life\data-management\video
python get_video_ls.py
python normalize_publish_date.py
cd D:\dream_life\data-management
git branch
git pull origin main
git add -A
git commit -m "test"
git push origin main
