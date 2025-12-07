# 测试 SSH 连接并推送代码
Write-Host "正在测试 SSH 连接..." -ForegroundColor Yellow

# 测试 GitHub SSH 连接
$testResult = ssh -T git@github.com 2>&1
Write-Host $testResult

if ($testResult -match "successfully authenticated" -or $testResult -match "You've successfully authenticated") {
    Write-Host "`n✅ SSH 连接成功！" -ForegroundColor Green
    Write-Host "正在推送到 GitHub..." -ForegroundColor Yellow
    
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 代码已成功推送到 GitHub！" -ForegroundColor Green
        Write-Host "仓库地址: https://github.com/xujl1999/data-management" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ 推送失败，请检查错误信息" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ SSH 连接失败" -ForegroundColor Red
    Write-Host "请确保已将 SSH 公钥添加到 GitHub" -ForegroundColor Yellow
    Write-Host "添加地址: https://github.com/settings/keys" -ForegroundColor Cyan
    Write-Host "`n你的公钥:" -ForegroundColor Yellow
    Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"
}

