D:
call C:\Users\23711\Miniconda3\Scripts\activate.bat C:\Users\23711\Miniconda3
call conda activate base
cd D:\dream_life\data-management\video
python get_video_ls.py
cd D:\dream_life\data-management\web
git branch
git pull origin master
git add .
git commit -m "test"
git push origin master
pause