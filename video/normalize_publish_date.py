from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


CSV_PATH = Path(__file__).resolve().parent / "video_ls.csv"


def parse_publish_date(text: str, now: Optional[datetime] = None) -> Tuple[Optional[datetime], str]:
    """Parse publish_date into datetime and yyyy-mm-dd string.
    Returns (datetime_or_None, normalized_string_or_original).
    """
    if now is None:
        now = datetime.now()
    original = text or ""
    cleaned = original.strip()
    if not cleaned:
        return None, original

    # Replace dots with dashes to help parsing
    normalized = cleaned.replace(".", "-")

    # Absolute date (yyyy-mm-dd or yyyy/mm/dd)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(normalized, fmt)
            return dt, dt.date().isoformat()
        except ValueError:
            pass

    # MM-DD (optionally MM/D or M-DD, M-D)
    try:
        if "-" in normalized and len(normalized.split("-")) == 2:
            month_str, day_str = normalized.split("-")
            month = int(month_str)
            day = int(day_str)
            year = now.year
            dt = datetime(year, month, day)
            # 如果超前于今天，推测上一年
            if dt.date() > now.date():
                dt = dt.replace(year=year - 1)
            return dt, dt.date().isoformat()
    except Exception:
        pass

    # 相对时间：X小时前
    if cleaned.endswith("小时前"):
        try:
            hours = int(cleaned.replace("小时前", "").strip())
            dt = now - timedelta(hours=hours)
            return dt, dt.date().isoformat()
        except Exception:
            pass

    # 相对时间：X分钟前
    if cleaned.endswith("分钟前"):
        try:
            minutes = int(cleaned.replace("分钟前", "").strip())
            dt = now - timedelta(minutes=minutes)
            return dt, dt.date().isoformat()
        except Exception:
            pass

    # 昨天 HH:MM 或 昨天
    if cleaned.startswith("昨天"):
        try:
            parts = cleaned.split()
            dt = now - timedelta(days=1)
            if len(parts) >= 2 and ":" in parts[1]:
                hh, mm = parts[1].split(":")
                dt = dt.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
            return dt, dt.date().isoformat()
        except Exception:
            pass

    # HH:MM 当天时间
    if ":" in cleaned and cleaned.replace(":", "").isdigit():
        try:
            hh, mm = cleaned.split(":")
            dt = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
            return dt, dt.date().isoformat()
        except Exception:
            pass

    # 刚刚
    if cleaned == "刚刚":
        return now, now.date().isoformat()

    # 无法解析，保留原始
    return None, original


def normalize_csv(path: Path = CSV_PATH) -> None:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(path)
    timestamps = []
    normalized_dates = []
    now = datetime.now()

    for value in df["publish_date"].fillna(""):
        dt, normalized = parse_publish_date(str(value), now=now)
        timestamps.append(dt.timestamp() if dt else float("-inf"))
        normalized_dates.append(normalized)

    df["_ts"] = timestamps
    df["publish_date"] = normalized_dates

    df.sort_values(by="_ts", ascending=False, inplace=True)
    df.drop(columns=["_ts"], inplace=True)
    df.to_csv(path, index=False, encoding="utf-8")


if __name__ == "__main__":
    normalize_csv()
    print(f"Normalized and sorted CSV saved to {CSV_PATH}")
