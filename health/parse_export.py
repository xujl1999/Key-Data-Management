from __future__ import annotations

import datetime as dt
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Optional

import pandas as pd

EXPORT_ZIP = Path(__file__).resolve().parent / "导出.zip"
OUTPUT_DIR = Path(__file__).resolve().parent


def find_main_xml(zf: zipfile.ZipFile) -> str:
    candidates = [
        name
        for name in zf.namelist()
        if name.lower().endswith(".xml") and "cda" not in name.lower()
    ]
    if not candidates:
        raise FileNotFoundError("未在压缩包中找到主 XML 文件")
    candidates.sort(key=lambda x: (not ("export" in x.lower()), len(x)))
    return candidates[0]


def normalize_offset(s: str) -> str:
    s = s.strip()
    if " +" in s:
        s = s.replace(" +", "+")
    if "+" in s:
        date_part, offset = s.split("+", 1)
        if len(offset) == 4:
            offset = offset[:2] + ":" + offset[2:]
        s = f"{date_part}+{offset}"
    return s


def parse_datetime(val: str) -> Optional[dt.datetime]:
    if not val:
        return None
    val = normalize_offset(val)
    for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(val, fmt)
        except ValueError:
            continue
    try:
        return dt.datetime.fromisoformat(val)
    except Exception:
        return None


def parse_export():
    if not EXPORT_ZIP.exists():
        raise FileNotFoundError(f"未找到文件: {EXPORT_ZIP}")

    steps = defaultdict(float)
    active_energy = defaultdict(float)
    sleep_daily = defaultdict(float)

    with zipfile.ZipFile(EXPORT_ZIP) as zf:
        xml_name = find_main_xml(zf)
        with zf.open(xml_name) as f:
            context = ET.iterparse(f, events=("end",))
            for _, elem in context:
                if elem.tag != "Record":
                    elem.clear()
                    continue

                record_type = elem.attrib.get("type", "")
                value = elem.attrib.get("value", "")
                start_raw = elem.attrib.get("startDate", "")
                end_raw = elem.attrib.get("endDate", "")
                start_dt = parse_datetime(start_raw)
                end_dt = parse_datetime(end_raw)

                if record_type == "HKQuantityTypeIdentifierStepCount":
                    if start_dt and value:
                        try:
                            steps[start_dt.date()] += float(value)
                        except Exception:
                            pass

                elif record_type == "HKQuantityTypeIdentifierActiveEnergyBurned":
                    if start_dt and value:
                        try:
                            active_energy[start_dt.date()] += float(value)
                        except Exception:
                            pass

                elif record_type == "HKCategoryTypeIdentifierSleepAnalysis":
                    if start_dt and end_dt:
                        duration_hours = (end_dt - start_dt).total_seconds() / 3600
                        sleep_daily[start_dt.date()] += duration_hours

                elem.clear()

    if steps:
        df_steps = (
            pd.DataFrame({"date": list(steps.keys()), "steps": steps.values()})
            .sort_values("date")
            .reset_index(drop=True)
        )
        df_steps.to_csv(OUTPUT_DIR / "steps_daily.csv", index=False, encoding="utf-8")

    if active_energy:
        df_energy = (
            pd.DataFrame(
                {"date": list(active_energy.keys()), "active_energy": active_energy.values()}
            )
            .sort_values("date")
            .reset_index(drop=True)
        )
        df_energy.to_csv(OUTPUT_DIR / "energy_daily.csv", index=False, encoding="utf-8")

    if sleep_daily:
        df_sleep = (
            pd.DataFrame({"date": list(sleep_daily.keys()), "sleep_hours": sleep_daily.values()})
            .sort_values("date")
            .reset_index(drop=True)
        )
        df_sleep.to_csv(OUTPUT_DIR / "sleep_daily.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    parse_export()
    print("解析完成，输出聚合数据（不含原始睡眠片段）")
