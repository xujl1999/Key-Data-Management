#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Health pipeline doctor.

A small orchestrator that runs common integrity checks and produces a single,
operator-friendly output.

Goals
-----
- One command to validate the health data area.
- Fast, dependency-light (pandas only via quality_report).
- CI-friendly exit codes.

Usage
-----
python health/scripts/doctor.py --days 14

Checks
------
1) `quality_report.py` generates `health/_data_quality.md`
2) Validate `health/dashboard_data.json` is valid JSON and has required keys.

Exit codes
----------
0 = ok
2 = quality report found missing days / anomalies
3 = dashboard json invalid or missing required keys
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
HEALTH_DIR = SCRIPT_DIR.parent
REPO_ROOT = HEALTH_DIR.parent

QUALITY_SCRIPT = SCRIPT_DIR / "quality_report.py"
QUALITY_OUT = HEALTH_DIR / "_data_quality.md"
DASHBOARD_JSON = HEALTH_DIR / "dashboard_data.json"


REQUIRED_DASHBOARD_KEYS = [
    "updated_at",
    "weather",
    "markets",
    "ai_news",
]


def _run_quality(days: int) -> tuple[int, str]:
    cmd = [sys.executable, str(QUALITY_SCRIPT), "--days", str(days), "--out", str(QUALITY_OUT)]
    p = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        return (3, out.strip() or f"quality_report failed (code={p.returncode})")

    # Parse the markdown output for red flags. We keep this intentionally simple:
    # any status != OK or any non-empty notes => warn.
    try:
        text = QUALITY_OUT.read_text(encoding="utf-8")
    except Exception as e:
        return (3, f"cannot read {QUALITY_OUT}: {type(e).__name__}: {e}")

    warn = False
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if line.startswith("| file ") or line.startswith("| ---"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 6:
            continue
        _file, status, _last_date, _coverage, notes, _spark = parts[:6]
        if status != "OK":
            warn = True
        if notes:
            warn = True

    return (2 if warn else 0, "")


def _check_dashboard() -> tuple[int, str]:
    if not DASHBOARD_JSON.exists():
        return (3, f"missing {DASHBOARD_JSON}")

    try:
        data = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        return (3, f"invalid json: {DASHBOARD_JSON} ({type(e).__name__}: {e})")

    missing = [k for k in REQUIRED_DASHBOARD_KEYS if k not in data]
    if missing:
        return (3, f"dashboard_data.json missing keys: {', '.join(missing)}")

    if not isinstance(data.get("weather"), dict):
        return (3, "dashboard_data.json weather should be object")

    return (0, "")


def main() -> int:
    ap = argparse.ArgumentParser(description="Health pipeline doctor")
    ap.add_argument("--days", type=int, default=14, help="recent window length (default: 14)")
    args = ap.parse_args()

    exit_code = 0

    qc, qmsg = _run_quality(days=args.days)
    if qmsg:
        print(qmsg)
    exit_code = max(exit_code, qc)

    dc, dmsg = _check_dashboard()
    if dmsg:
        print(dmsg)
    exit_code = max(exit_code, dc)

    if exit_code == 0:
        print("OK: health doctor checks passed")
    elif exit_code == 2:
        print("WARN: health doctor found data quality issues (see health/_data_quality.md)")
    else:
        print("FAIL: health doctor failed")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
