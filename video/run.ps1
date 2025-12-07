# PowerShell 版本的 run.sh
$ErrorActionPreference = "Stop"

$ROOT_DIR = $PSScriptRoot
$PORT = if ($args.Count -gt 0) { $args[0] } else { 4173 }
$PID_FILE = Join-Path $ROOT_DIR ".mini_bilibili_server.pid"
$LOG_FILE = Join-Path $ROOT_DIR ".mini_bilibili_server.log"

Set-Location $ROOT_DIR

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "[$timestamp] 开始抓取最新视频..."
python get_video_ls.py

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "[$timestamp] 视频抓取完成，准备部署静态站点..."

# 检查并关闭旧进程
if (Test-Path $PID_FILE) {
    $oldPid = Get-Content $PID_FILE
    try {
        $process = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "发现旧服务器进程 $oldPid，正在关闭..."
            Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } catch {
        # 进程不存在，忽略
    }
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
}

# 检查端口占用并释放
$portProcess = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($portProcess) {
    Write-Host "端口 $PORT 被占用，尝试释放..."
    foreach ($pid in $portProcess) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

# 启动 HTTP 服务器
$job = Start-Job -ScriptBlock {
    param($rootDir, $port, $logFile)
    Set-Location $rootDir
    python -m http.server $port *> $logFile
} -ArgumentList $ROOT_DIR, $PORT, $LOG_FILE

$jobId = $job.Id
$jobId | Out-File -FilePath $PID_FILE -Encoding utf8

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "[$timestamp] 部署完成，HTTP 服务 Job ID=$jobId, 端口=$PORT"
Write-Host "访问: http://127.0.0.1:$PORT/front/index.html"
Write-Host "日志: $LOG_FILE"

