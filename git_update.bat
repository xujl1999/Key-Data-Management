@echo off
setlocal

D:
cd /d D:\dream_life\data-management

git pull origin main
git add -A
for /f %%i in ('git status --porcelain') do set CHANGES=1
if defined CHANGES (
  git commit -m "update data"
  git push origin main
) else (
  echo No changes to commit.
)

endlocal
