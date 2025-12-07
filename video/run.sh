#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-4173}"
PID_FILE="$ROOT_DIR/.mini_bilibili_server.pid"
LOG_FILE="$ROOT_DIR/.mini_bilibili_server.log"

cd "$ROOT_DIR"

echo "[$(date '+%F %T')] 开始抓取最新视频..."
python3 get_video_ls.py

echo "[$(date '+%F %T')] 视频抓取完成，准备部署静态站点..."

if [[ -f "$PID_FILE" ]]; then
  old_pid="$(cat "$PID_FILE")"
  if kill -0 "$old_pid" >/dev/null 2>&1; then
    echo "发现旧服务器进程 $old_pid ，正在关闭..."
    kill "$old_pid" || true
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

# 若端口仍被占用，尝试强制释放
if lsof -ti :"$PORT" >/dev/null 2>&1; then
  echo "端口 $PORT 被占用，尝试释放..."
  lsof -ti :"$PORT" | xargs kill -9 || true
fi

(cd "$ROOT_DIR" && python3 -m http.server "$PORT" >"$LOG_FILE" 2>&1 & echo $! >"$PID_FILE")

echo "[$(date '+%F %T')] 部署完成，HTTP 服务 PID=$(cat "$PID_FILE"), 端口=$PORT"
echo "访问: http://127.0.0.1:$PORT/front/index.html"
echo "日志: $LOG_FILE"
