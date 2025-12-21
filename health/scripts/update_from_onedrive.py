from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HEALTH_DIR = SCRIPT_DIR.parent
DEFAULT_SOURCE_DIR = Path(r"C:\Users\23711\OneDrive\DATA")
DEFAULT_PATTERN = "导出*.zip"
DEST_ZIP = HEALTH_DIR / "导出.zip"
PARSE_SCRIPT = SCRIPT_DIR / "parse_export.py"


def pick_latest_zip(source_dir: Path, pattern: str) -> Path | None:
    candidates = list(source_dir.glob(pattern))
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda path: (path.stat().st_mtime, path.stat().st_size, path.name),
    )


def wait_for_stable_file(path: Path, timeout: int, interval: float, stable_checks: int) -> bool:
    start = time.time()
    last = None
    stable = 0
    while time.time() - start <= timeout:
        try:
            stat = path.stat()
        except FileNotFoundError:
            time.sleep(interval)
            continue

        current = (stat.st_size, stat.st_mtime)
        if current == last:
            stable += 1
        else:
            stable = 0
            last = current

        if stable >= stable_checks:
            return True
        time.sleep(interval)
    return False


def copy_zip(source: Path, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()
    shutil.copy2(source, tmp)
    os.replace(tmp, dest)


def run_parse(script: Path) -> None:
    subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy latest Apple Health export zip from OneDrive, replace local export, and parse it."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="OneDrive directory that contains export zips.",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help="Glob pattern for export zips (default: 导出*.zip).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Seconds to wait for the file to stabilize (default: 600).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds (default: 2).",
    )
    parser.add_argument(
        "--stable-checks",
        type=int,
        default=3,
        help="How many consecutive stable checks before proceeding.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Skip waiting for OneDrive sync; use latest by last write time.",
    )
    parser.add_argument(
        "--delete-source",
        action="store_true",
        help="Delete source zip after successful copy.",
    )
    args = parser.parse_args()

    source_dir = args.source_dir
    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return 2

    latest = pick_latest_zip(source_dir, args.pattern)
    if not latest:
        print(f"No zip found in {source_dir} with pattern: {args.pattern}")
        return 2

    print(f"Selected source zip: {latest}")
    if not args.no_wait:
        ok = wait_for_stable_file(latest, args.timeout, args.interval, args.stable_checks)
        if not ok:
            print(f"File did not stabilize in time: {latest}")
            return 3

    copy_zip(latest, DEST_ZIP)
    print(f"Copied to: {DEST_ZIP}")

    if args.delete_source:
        try:
            latest.unlink()
            print(f"Deleted source zip: {latest}")
        except Exception as exc:
            print(f"Failed to delete source zip: {exc}")

    if not PARSE_SCRIPT.exists():
        print(f"Parse script not found: {PARSE_SCRIPT}")
        return 4

    run_parse(PARSE_SCRIPT)
    print("Parse complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
