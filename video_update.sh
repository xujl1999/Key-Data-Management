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

echo "Running get_video_ls.py..."
python video/get_video_ls.py

echo "Running normalize_publish_date.py..."
python video/normalize_publish_date.py
