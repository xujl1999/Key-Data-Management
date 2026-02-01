#!/bin/bash
set -e

echo "Starting Data Management Container..."

# 1. Rclone Sync (Only if configured)
# Check if rclone config exists (mounted volume)
if [ -f "/root/.config/rclone/rclone.conf" ]; then
    echo "Rclone config found. Attempting to sync from OneDrive..."
    # Sync from 'onedrive:DATA' to a temp directory to avoid overwriting blindly
    # We will sync to /tmp/onedrive_sync
    echo "Syncing from OneDrive..."
    rclone sync "onedrive:DATA" "/tmp/onedrive_sync" --include "导出*.zip" --verbose || echo "Rclone sync failed (non-fatal if files exist)..."

    # Use the existing python script to pick the latest zip from /tmp/onedrive_sync and copy it to /app/health/导出.zip
    echo "Selecting latest export file..."
    python health/scripts/update_from_onedrive.py --source-dir "/tmp/onedrive_sync" --no-wait --delete-source
else
    echo "No rclone config found. Skipping OneDrive sync."
fi

# 2. Run Data Processing
# update_from_onedrive.py already runs parse_export.py if successful, but we can run it explicitly to be sure
# or just rely on update_from_onedrive.py's internal call. 
# Let's run it explicitly to handle cases where update_from_onedrive.py didn't run (no new files).
echo "Running parse_export.py (idempotent)..."
python health/scripts/parse_export.py

echo "Running build_sleep_schedule.js..."
# Check if node_modules exists, otherwise install (should be pre-installed if in image, but just in case of volume mount overrides)
# Actually, node dependencies might be minimal or just standard lib? 
# build_sleep_schedule.js seems to use standard fs stuff or simple logic.
# Let's check if package.json exists, if so install.
if [ -f "package.json" ]; then
    npm install
fi
node health/scripts/build_sleep_schedule.js

echo "Running summarize_last7.py..."
python health/scripts/summarize_last7.py

# 3. Start API Server
echo "Starting Local API Server on port 8001..."
python local_api.py
