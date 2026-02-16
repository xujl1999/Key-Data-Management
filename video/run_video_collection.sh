#!/bin/bash
set -e

# Define paths
CONDA_BASE="$HOME/miniconda3"
# 默认使用 base；可通过环境变量 KDM_CONDA_ENV 覆盖
ENV_NAME="${KDM_CONDA_ENV:-base}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/get_video_ls.py"

# Activate conda
if [ -f "$CONDA_BASE/bin/activate" ]; then
    source "$CONDA_BASE/bin/activate" "$ENV_NAME"
else
    echo "Error: Conda activation script not found at $CONDA_BASE/bin/activate"
    exit 1
fi

# Run the python script with any arguments passed to this wrapper
python "$PYTHON_SCRIPT" "$@"
