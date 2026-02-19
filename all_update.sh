#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

bash "$(dirname "$0")/health_update.sh"
bash "$(dirname "$0")/video_update.sh"
bash "$(dirname "$0")/git_update.sh"

echo ""
echo "=== All updates completed successfully ==="
