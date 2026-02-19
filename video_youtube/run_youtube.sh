#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== YouTube Video Collection & Summarization ==="
echo ""

# 1. Fetch video list
echo "[1/2] Fetching YouTube video list..."
python3 "$SCRIPT_DIR/get_youtube_ls.py" "$@"
echo ""

# 2. Summarize new videos
echo "[2/2] Summarizing new videos..."
python3 "$SCRIPT_DIR/summarize_videos.py"
echo ""

echo "=== Done ==="
