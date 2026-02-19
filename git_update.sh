#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

GIT_EXE="${GIT_EXE:-$(command -v git 2>/dev/null || true)}"
if [[ -z "$GIT_EXE" ]]; then
  echo "Git not found. Please install Git or add it to PATH."
  exit 1
fi

"$GIT_EXE" add -A
if "$GIT_EXE" diff --cached --quiet; then
  echo "No changes to commit."
else
  "$GIT_EXE" commit -m "update data"
fi

RETRIES=5
WAIT=5

# Pull with retry
for ((i=1; i<=RETRIES; i++)); do
  if "$GIT_EXE" pull --rebase origin main; then
    break
  fi
  if [[ -d ".git/rebase-merge" || -d ".git/rebase-apply" ]]; then
    echo "Pull failed — rebase conflict detected."
    exit 1
  fi
  if ((i >= RETRIES)); then
    echo "Pull failed after $RETRIES attempts."
    exit 1
  fi
  echo "Pull failed, retrying ($i/$RETRIES)..."
  sleep "$WAIT"
done

# Push with retry
for ((i=1; i<=RETRIES; i++)); do
  if "$GIT_EXE" push origin main; then
    echo "Push succeeded."
    exit 0
  fi
  if ((i >= RETRIES)); then
    echo "Push failed after $RETRIES attempts."
    exit 1
  fi
  echo "Push failed, retrying ($i/$RETRIES)..."
  sleep "$WAIT"
done
