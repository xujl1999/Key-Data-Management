# 上传到 GitHub 的脚本
# 使用方法: powershell -ExecutionPolicy Bypass -File upload_to_github.ps1

Write-Host "开始准备上传到 GitHub..." -ForegroundColor Green

# 检查 Git 是否安装
try {
    $gitVersion = git --version
    Write-Host "Git 已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未检测到 Git，请先安装 Git for Windows" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# 检查是否已初始化 Git 仓库
if (-not (Test-Path .git)) {
    Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
    git init
}

# 检查远程仓库是否已设置
$remoteUrl = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "设置远程仓库..." -ForegroundColor Yellow
    git remote add origin https://github.com/xujl1999/data-management.git
} else {
    Write-Host "远程仓库已设置: $remoteUrl" -ForegroundColor Green
    Write-Host "更新远程仓库地址..." -ForegroundColor Yellow
    git remote set-url origin https://github.com/xujl1999/data-management.git
}

# 从 Git 中移除敏感文件（如果已被跟踪）
Write-Host "检查并移除敏感文件..." -ForegroundColor Yellow
$filesToRemove = @("bili_cookies.json", "bilibili_authors.json", "video_ls.csv", ".mini_bilibili_server.pid", ".mini_bilibili_server.log")
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        git rm --cached $file -r -f 2>$null
    }
}

# 添加所有文件
Write-Host "添加文件到 Git..." -ForegroundColor Yellow
git add .

# 显示将要提交的文件
Write-Host "`n将要提交的文件:" -ForegroundColor Cyan
git status --short

# 提交更改
Write-Host "`n提交更改..." -ForegroundColor Yellow
$commitMessage = "更新 mini-bilibili 项目"
git commit -m $commitMessage

# 推送到 GitHub
Write-Host "`n推送到 GitHub..." -ForegroundColor Yellow
Write-Host "注意: 如果是第一次推送，可能需要输入 GitHub 用户名和密码/Token" -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 上传成功！" -ForegroundColor Green
    Write-Host "仓库地址: https://github.com/xujl1999/data-management" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ 推送失败，请检查错误信息" -ForegroundColor Red
    Write-Host "提示: 如果分支名不是 main，请使用: git push -u origin master" -ForegroundColor Yellow
}

