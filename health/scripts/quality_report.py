"""Health data quality report.

Goal
----
Generate a lightweight markdown report that answers:
- What is the latest date for each metric file?
- Are we missing days in the recent window?
- Any obvious anomalies (flatlines / impossible values)?

This script is intentionally dependency-light (pandas only).

Usage
-----
python health/scripts/quality_report.py --days 14

Outputs
-------
health/_data_quality.md

"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
HEALTH_DIR = SCRIPT_DIR.parent
DATA_DIR = HEALTH_DIR / "data"
DEFAULT_OUT = HEALTH_DIR / "_data_quality.md"


SPARK_CHARS = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float | None]) -> str:
    clean = [v for v in values if v is not None]
    if not clean:
        return ""
    vmin = min(clean)
    vmax = max(clean)
    if vmax == vmin:
        return SPARK_CHARS[0] * len(values)

    out = []
    for v in values:
        if v is None:
            out.append("·")
            continue
        t = (v - vmin) / (vmax - vmin)
        idx = int(round(t * (len(SPARK_CHARS) - 1)))
        idx = max(0, min(idx, len(SPARK_CHARS) - 1))
        out.append(SPARK_CHARS[idx])
    return "".join(out)


@dataclass(frozen=True)
class FileCheck:
    filename: str
    important_cols: tuple[str, ...]
    # Optional sanity bounds per column: (min, max)
    bounds: dict[str, tuple[float | None, float | None]]


CHECKS: list[FileCheck] = [
    FileCheck(
        filename="steps_daily.csv",
        important_cols=("steps",),
        bounds={"steps": (0, 200_000)},
    ),
    FileCheck(
        filename="sleep_daily.csv",
        important_cols=("sleep_hours",),
        bounds={"sleep_hours": (0, 24)},
    ),
    FileCheck(
        filename="sleep_sessions.csv",
        important_cols=("duration_hours",),
        bounds={"duration_hours": (0, 24)},
    ),
    FileCheck(
        filename="weight_daily.csv",
        important_cols=("weight_kg",),
        bounds={"weight_kg": (20, 300)},
    ),
    FileCheck(
        filename="energy_daily.csv",
        important_cols=("active_energy", "basal_energy"),
        bounds={"active_energy": (0, 10_000), "basal_energy": (0, 10_000)},
    ),
    FileCheck(
        filename="heart_rate_daily.csv",
        important_cols=("hr_avg", "hr_min", "hr_max"),
        bounds={"hr_avg": (20, 250), "hr_min": (20, 250), "hr_max": (20, 250)},
    ),
]


def _read_daily_csv(path: Path) -> pd.DataFrame:
    """Read a *daily* csv that has a `date` column."""
    df = pd.read_csv(path)
    if "date" not in df.columns:
        raise ValueError(f"missing 'date' column: {path}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df.sort_values("date")


def _read_sessions_csv(path: Path) -> pd.DataFrame:
    """Read a sessions csv (e.g. sleep_sessions.csv) that has start/end timestamps."""
    df = pd.read_csv(path)
    for c in ("start", "end"):
        if c not in df.columns:
            raise ValueError(f"missing '{c}' column: {path}")
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"] = pd.to_datetime(df["end"], errors="coerce")
    # Define per-day bucket by start date.
    df["date"] = df["start"].dt.date
    return df.sort_values("start")


def _recent_window(end: date, days: int) -> list[date]:
    start = end - timedelta(days=days - 1)
    return [start + timedelta(days=i) for i in range(days)]


def _missing_dates(present: set[date], window: Iterable[date]) -> list[date]:
    return [d for d in window if d not in present]


def _find_flatlines(series: pd.Series, window: int = 7) -> bool:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < window:
        return False
    tail = s.iloc[-window:]
    return float(tail.max()) == float(tail.min())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate health data quality markdown report")
    parser.add_argument("--days", type=int, default=14, help="recent window length (default: 14)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output markdown path")
    args = parser.parse_args()

    if not DATA_DIR.exists():
        raise SystemExit(f"data dir not found: {DATA_DIR}")

    now = pd.Timestamp.now().to_pydatetime()

    rows = []
    for check in CHECKS:
        path = DATA_DIR / check.filename
        if not path.exists():
            rows.append((check.filename, "MISSING", "", "", ""))
            continue

        if check.filename.endswith("_sessions.csv"):
            df = _read_sessions_csv(path)
        else:
            df = _read_daily_csv(path)
        if df.empty:
            rows.append((check.filename, "EMPTY", "", "", ""))
            continue

        last_day: date = df["date"].max()
        window = _recent_window(last_day, args.days)
        present = set(df["date"].tolist())
        miss = _missing_dates(present, window)

        coverage = (args.days - len(miss)) / args.days
        status = "OK" if not miss else f"MISS({len(miss)})"

        notes = []
        for col in check.important_cols:
            if col not in df.columns:
                notes.append(f"no_col:{col}")
                continue
            series = pd.to_numeric(df[col], errors="coerce")
            if series.notna().any():
                vmin = series.min(skipna=True)
                vmax = series.max(skipna=True)
                bmin, bmax = check.bounds.get(col, (None, None))
                if bmin is not None and vmin < bmin:
                    notes.append(f"{col}:min<{bmin}")
                if bmax is not None and vmax > bmax:
                    notes.append(f"{col}:max>{bmax}")
                if _find_flatlines(series):
                    notes.append(f"{col}:flat7")

        # sparkline for the first important column
        spark = ""
        if check.important_cols and check.important_cols[0] in df.columns:
            col0 = check.important_cols[0]
            recent_df = df[df["date"].isin(window)].set_index("date")
            vals = []
            for d in window:
                if d not in recent_df.index:
                    vals.append(None)
                    continue
                v = pd.to_numeric(recent_df.loc[d, col0], errors="coerce")
                if isinstance(v, pd.Series):
                    v = v.iloc[0]
                vals.append(None if pd.isna(v) else float(v))
            spark = _sparkline(vals)

        rows.append(
            (
                check.filename,
                status,
                str(last_day),
                f"{coverage:.0%}",
                (", ".join(notes) if notes else ""),
                spark,
            )
        )

    out = args.out
    with out.open("w", encoding="utf-8") as f:
        f.write("# Health Data Quality Report\n\n")
        f.write(f"Generated: {now:%Y-%m-%d %H:%M:%S}\n\n")
        f.write(f"Window: last {args.days} days (per-file, aligned to each file's latest date)\n\n")
        f.write("| file | status | last_date | coverage | notes | sparkline |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for r in rows:
            f.write("| " + " | ".join(r) + " |\n")

        f.write("\n## How to read\n")
        f.write("- status=MISS(n): within the recent window, n dates are missing from this csv.\n")
        f.write("- notes: basic sanity flags (missing columns / impossible bounds / 7-day flatline).\n")
        f.write("- sparkline: first important metric's recent trend; missing days shown as '·'.\n")

    print(f"written {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
