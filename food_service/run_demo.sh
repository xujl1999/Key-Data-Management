#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export SHORTCUT_TOKEN="${SHORTCUT_TOKEN:-demo-token}"
export QWEN_API_KEY="${QWEN_API_KEY:-}"

python -m uvicorn food_service.app:app --host 127.0.0.1 --port 8787
