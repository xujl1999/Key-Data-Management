#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Activate conda
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniconda3}"
if [[ -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]]; then
  source "$CONDA_ROOT/etc/profile.d/conda.sh"
elif [[ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]]; then
  source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
  echo "Conda not found. Please install Miniconda/Anaconda."
  exit 1
fi
conda activate base

# OneDrive update with retry
RETRIES=3
for ((i=1; i<=RETRIES; i++)); do
  if python health/scripts/update_from_onedrive.py --no-wait; then
    break
  fi
  if ((i >= RETRIES)); then
    echo "OneDrive update failed after $RETRIES attempts. Proceeding with existing local file..."
    break
  fi
  echo "OneDrive update failed, retrying ($i/$RETRIES)..."
  sleep 5
done

python health/scripts/parse_export.py

# Node.js build_sleep_schedule
NODE_EXE="${NODE_EXE:-$(command -v node 2>/dev/null || true)}"
if [[ -n "$NODE_EXE" ]]; then
  echo "Using Node: $NODE_EXE"
  "$NODE_EXE" health/scripts/build_sleep_schedule.js || echo "Warning: build_sleep_schedule.js failed, continuing..."
else
  echo "Node.js not found. Skipping build_sleep_schedule.js"
fi

python health/scripts/summarize_last7.py
