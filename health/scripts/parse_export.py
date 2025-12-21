from __future__ import annotations

import csv
import datetime as dt
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Optional

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
HEALTH_DIR = SCRIPT_DIR.parent
ROOT = HEALTH_DIR / "data"  # 数据输出目录
ROOT.mkdir(exist_ok=True)

EXPORT_ZIP = HEALTH_DIR / "导出.zip"
if not EXPORT_ZIP.exists():
    alt = HEALTH_DIR / "å¯¼å‡º.zip"  # 兼容历史编码
    if alt.exists():
        EXPORT_ZIP = alt


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
    basal_energy = defaultdict(float)
    physical_effort = defaultdict(float)
    sleep_daily = defaultdict(float)
    sleep_sessions = []
    weight_daily = defaultdict(list)
    bmi_daily = defaultdict(list)
    bodyfat_daily = defaultdict(list)
    leanmass_daily = defaultdict(list)
    height_daily = defaultdict(list)

    distance_walk_run = defaultdict(float)
    distance_cycling = defaultdict(float)
    exercise_time = defaultdict(float)
    stand_time = defaultdict(float)
    stand_hours = defaultdict(int)
    daylight_time = defaultdict(float)

    heart_rate = defaultdict(list)
    resting_hr = defaultdict(list)
    walking_hr = defaultdict(list)
    hrv_sdnn = defaultdict(list)
    respiratory_rate = defaultdict(list)
    spo2 = defaultdict(list)
    vo2max = defaultdict(list)
    sleep_wrist_temp = defaultdict(list)
    walking_steadiness = defaultdict(list)

    walking_speed = defaultdict(list)
    walking_step_length = defaultdict(list)
    walking_double_support = defaultdict(list)
    walking_asymmetry = defaultdict(list)
    running_speed = defaultdict(list)
    running_power = defaultdict(list)
    running_vertical_osc = defaultdict(list)
    running_ground_contact = defaultdict(list)
    running_stride_length = defaultdict(list)

    stair_ascent_speed = defaultdict(list)
    stair_descent_speed = defaultdict(list)
    flights_climbed = defaultdict(float)

    dietary_energy = defaultdict(float)
    dietary_fat = defaultdict(float)
    dietary_carb = defaultdict(float)
    dietary_protein = defaultdict(float)
    dietary_water = defaultdict(float)

    audio_env = defaultdict(list)
    audio_headphone = defaultdict(list)

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

                if start_dt and value:
                    try:
                        val = float(value)
                    except Exception:
                        val = None
                else:
                    val = None

                if record_type == "HKQuantityTypeIdentifierStepCount" and val is not None:
                    steps[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierActiveEnergyBurned" and val is not None:
                    active_energy[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierBasalEnergyBurned" and val is not None:
                    basal_energy[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierPhysicalEffort" and val is not None:
                    physical_effort[start_dt.date()] += val

                elif record_type == "HKCategoryTypeIdentifierSleepAnalysis" and start_dt and end_dt:
                    duration_hours = (end_dt - start_dt).total_seconds() / 3600
                    sleep_daily[start_dt.date()] += duration_hours
                    sleep_sessions.append(
                        (
                            start_dt,
                            end_dt,
                            duration_hours,
                            value,
                            elem.attrib.get("sourceName", ""),
                        )
                    )

                elif record_type == "HKQuantityTypeIdentifierBodyMass" and val is not None:
                    weight_daily[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierBodyMassIndex" and val is not None:
                    bmi_daily[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierBodyFatPercentage" and val is not None:
                    bodyfat_daily[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierLeanBodyMass" and val is not None:
                    leanmass_daily[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierHeight" and val is not None:
                    height_daily[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierDistanceWalkingRunning" and val is not None:
                    distance_walk_run[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierDistanceCycling" and val is not None:
                    distance_cycling[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierAppleExerciseTime" and val is not None:
                    exercise_time[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierAppleStandTime" and val is not None:
                    stand_time[start_dt.date()] += val

                elif record_type == "HKCategoryTypeIdentifierAppleStandHour":
                    # 记录一个小时内站立过即可计数
                    if start_dt:
                        stand_hours[start_dt.date()] += 1

                elif record_type == "HKQuantityTypeIdentifierTimeInDaylight" and val is not None:
                    daylight_time[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierHeartRate" and val is not None:
                    heart_rate[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRestingHeartRate" and val is not None:
                    resting_hr[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierWalkingHeartRateAverage" and val is not None:
                    walking_hr[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN" and val is not None:
                    hrv_sdnn[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRespiratoryRate" and val is not None:
                    respiratory_rate[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierOxygenSaturation" and val is not None:
                    spo2[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierVO2Max" and val is not None:
                    vo2max[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierAppleSleepingWristTemperature" and val is not None:
                    sleep_wrist_temp[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierAppleWalkingSteadiness" and val is not None:
                    walking_steadiness[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierWalkingSpeed" and val is not None:
                    walking_speed[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierWalkingStepLength" and val is not None:
                    walking_step_length[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierWalkingDoubleSupportPercentage" and val is not None:
                    walking_double_support[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierWalkingAsymmetryPercentage" and val is not None:
                    walking_asymmetry[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRunningSpeed" and val is not None:
                    running_speed[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRunningPower" and val is not None:
                    running_power[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRunningVerticalOscillation" and val is not None:
                    running_vertical_osc[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRunningGroundContactTime" and val is not None:
                    running_ground_contact[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierRunningStrideLength" and val is not None:
                    running_stride_length[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierStairAscentSpeed" and val is not None:
                    stair_ascent_speed[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierStairDescentSpeed" and val is not None:
                    stair_descent_speed[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierFlightsClimbed" and val is not None:
                    flights_climbed[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierDietaryEnergyConsumed" and val is not None:
                    dietary_energy[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierDietaryFatTotal" and val is not None:
                    dietary_fat[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierDietaryCarbohydrates" and val is not None:
                    dietary_carb[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierDietaryProtein" and val is not None:
                    dietary_protein[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierDietaryWater" and val is not None:
                    dietary_water[start_dt.date()] += val

                elif record_type == "HKQuantityTypeIdentifierEnvironmentalAudioExposure" and val is not None:
                    audio_env[start_dt.date()].append(val)

                elif record_type == "HKQuantityTypeIdentifierHeadphoneAudioExposure" and val is not None:
                    audio_headphone[start_dt.date()].append(val)

                elem.clear()

    def write_sum_dict(path: Path, mapping: dict, columns: tuple[str, str]):
        if not mapping:
            return
        df = pd.DataFrame({"date": list(mapping.keys()), columns[1]: mapping.values()})
        df = df.sort_values("date").reset_index(drop=True)
        df.to_csv(path, index=False, encoding="utf-8")

    def write_avg_dict(path: Path, mapping: dict, columns: list[str]):
        if not mapping:
            return
        rows = []
        for day, values in mapping.items():
            if not values:
                continue
            vals = list(values)
            rows.append(
                (
                    day,
                    sum(vals) / len(vals),
                    min(vals),
                    max(vals),
                    len(vals),
                )
            )
        if not rows:
            return
        df = pd.DataFrame(rows, columns=["date", *columns])
        df = df.sort_values("date").reset_index(drop=True)
        df.to_csv(path, index=False, encoding="utf-8")

    write_sum_dict(ROOT / "steps_daily.csv", steps, ("date", "steps"))

    if active_energy or basal_energy or physical_effort:
        df_energy = pd.DataFrame(
            {
                "date": list(set(active_energy.keys()) | set(basal_energy.keys()) | set(physical_effort.keys())),
            }
        )
        df_energy["active_energy"] = df_energy["date"].map(active_energy).fillna(0)
        df_energy["basal_energy"] = df_energy["date"].map(basal_energy).fillna(0)
        df_energy["physical_effort"] = df_energy["date"].map(physical_effort).fillna(0)
        df_energy = df_energy.sort_values("date").reset_index(drop=True)
        df_energy.to_csv(ROOT / "energy_daily.csv", index=False, encoding="utf-8")

    write_sum_dict(ROOT / "sleep_daily.csv", sleep_daily, ("date", "sleep_hours"))
    if sleep_sessions:
        sleep_sessions.sort(key=lambda x: x[0])
        with (ROOT / "sleep_sessions.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["start", "end", "duration_hours", "value", "source"])
            for start_dt, end_dt, duration_hours, value, source in sleep_sessions:
                writer.writerow(
                    [
                        start_dt.isoformat(),
                        end_dt.isoformat(),
                        f"{duration_hours:.3f}",
                        value,
                        source,
                    ]
                )

    if weight_daily or bmi_daily or bodyfat_daily or leanmass_daily or height_daily:
        rows = []
        all_dates = set(weight_daily.keys()) | set(bmi_daily.keys()) | set(bodyfat_daily.keys()) | set(
            leanmass_daily.keys()
        ) | set(height_daily.keys())
        for day in all_dates:
            w_vals = weight_daily.get(day, [])
            bmi_vals = bmi_daily.get(day, [])
            fat_vals = bodyfat_daily.get(day, [])
            lean_vals = leanmass_daily.get(day, [])
            h_vals = height_daily.get(day, [])

            def avg(lst):
                return sum(lst) / len(lst) if lst else None

            rows.append(
                (
                    day,
                    avg(w_vals),
                    avg(bmi_vals),
                    avg(fat_vals),
                    avg(lean_vals),
                    avg(h_vals),
                )
            )
        df_body = pd.DataFrame(
            rows,
            columns=["date", "weight_kg", "bmi", "body_fat_pct", "lean_mass_kg", "height_m"],
        ).sort_values("date")
        df_body.to_csv(ROOT / "body_daily.csv", index=False, encoding="utf-8")

    # 单独输出 weight_daily.csv（前端直接引用）
    if weight_daily:
        weight_rows = []
        for day, vals in weight_daily.items():
            if vals:
                weight_rows.append((day, sum(vals) / len(vals)))
        if weight_rows:
            df_weight = pd.DataFrame(weight_rows, columns=["date", "weight_kg"]).sort_values("date")
            df_weight.to_csv(ROOT / "weight_daily.csv", index=False, encoding="utf-8")

    if distance_walk_run or distance_cycling:
        df_dist = pd.DataFrame(
            {
                "date": list(set(distance_walk_run.keys()) | set(distance_cycling.keys())),
            }
        )
        df_dist["distance_walk_run_km"] = df_dist["date"].map(distance_walk_run).fillna(0) / 1000
        df_dist["distance_cycling_km"] = df_dist["date"].map(distance_cycling).fillna(0) / 1000
        df_dist = df_dist.sort_values("date").reset_index(drop=True)
        df_dist.to_csv(ROOT / "distance_daily.csv", index=False, encoding="utf-8")

    if exercise_time or stand_time or stand_hours:
        df_ex = pd.DataFrame({"date": list(set(exercise_time.keys()) | set(stand_time.keys()) | set(stand_hours.keys()))})
        df_ex["exercise_time_min"] = df_ex["date"].map(exercise_time).fillna(0)
        df_ex["stand_time_min"] = df_ex["date"].map(stand_time).fillna(0)
        df_ex["stand_hours"] = df_ex["date"].map(stand_hours).fillna(0)
        df_ex = df_ex.sort_values("date").reset_index(drop=True)
        df_ex.to_csv(ROOT / "exercise_daily.csv", index=False, encoding="utf-8")

    if daylight_time:
        write_sum_dict(ROOT / "daylight_daily.csv", daylight_time, ("date", "time_in_daylight_min"))

    write_avg_dict(ROOT / "heart_rate_daily.csv", heart_rate, ["hr_avg", "hr_min", "hr_max", "hr_count"])
    write_avg_dict(ROOT / "resting_hr_daily.csv", resting_hr, ["resting_hr_avg", "resting_hr_min", "resting_hr_max", "count"])
    write_avg_dict(ROOT / "walking_hr_daily.csv", walking_hr, ["walk_hr_avg", "walk_hr_min", "walk_hr_max", "count"])
    write_avg_dict(ROOT / "hrv_daily.csv", hrv_sdnn, ["sdnn_avg", "sdnn_min", "sdnn_max", "count"])
    write_avg_dict(ROOT / "respiratory_daily.csv", respiratory_rate, ["resp_avg", "resp_min", "resp_max", "count"])
    write_avg_dict(ROOT / "spo2_daily.csv", spo2, ["spo2_avg", "spo2_min", "spo2_max", "count"])
    write_avg_dict(ROOT / "vo2max_daily.csv", vo2max, ["vo2max_avg", "vo2max_min", "vo2max_max", "count"])
    write_avg_dict(ROOT / "sleep_temp_daily.csv", sleep_wrist_temp, ["temp_avg", "temp_min", "temp_max", "count"])
    write_avg_dict(ROOT / "walking_steadiness_daily.csv", walking_steadiness, ["steady_avg", "steady_min", "steady_max", "count"])

    write_avg_dict(ROOT / "walking_metrics_daily.csv", walking_speed, ["walking_speed_avg", "walking_speed_min", "walking_speed_max", "count"])
    write_avg_dict(ROOT / "walking_step_length_daily.csv", walking_step_length, ["step_length_avg", "step_length_min", "step_length_max", "count"])
    write_avg_dict(
        ROOT / "walking_double_support_daily.csv",
        walking_double_support,
        ["double_support_pct_avg", "double_support_pct_min", "double_support_pct_max", "count"],
    )
    write_avg_dict(
        ROOT / "walking_asymmetry_daily.csv",
        walking_asymmetry,
        ["asymmetry_pct_avg", "asymmetry_pct_min", "asymmetry_pct_max", "count"],
    )

    write_avg_dict(ROOT / "running_speed_daily.csv", running_speed, ["running_speed_avg", "running_speed_min", "running_speed_max", "count"])
    write_avg_dict(ROOT / "running_power_daily.csv", running_power, ["running_power_avg", "running_power_min", "running_power_max", "count"])
    write_avg_dict(
        ROOT / "running_vertical_osc_daily.csv",
        running_vertical_osc,
        ["running_vertical_osc_avg", "running_vertical_osc_min", "running_vertical_osc_max", "count"],
    )
    write_avg_dict(
        ROOT / "running_ground_contact_daily.csv",
        running_ground_contact,
        ["ground_contact_ms_avg", "ground_contact_ms_min", "ground_contact_ms_max", "count"],
    )
    write_avg_dict(
        ROOT / "running_stride_length_daily.csv",
        running_stride_length,
        ["running_stride_len_avg", "running_stride_len_min", "running_stride_len_max", "count"],
    )

    write_avg_dict(ROOT / "stair_ascent_speed_daily.csv", stair_ascent_speed, ["stair_ascent_speed_avg", "stair_ascent_speed_min", "stair_ascent_speed_max", "count"])
    write_avg_dict(ROOT / "stair_descent_speed_daily.csv", stair_descent_speed, ["stair_descent_speed_avg", "stair_descent_speed_min", "stair_descent_speed_max", "count"])
    write_sum_dict(ROOT / "flights_daily.csv", flights_climbed, ("date", "flights_climbed"))

    if dietary_energy or dietary_fat or dietary_carb or dietary_protein or dietary_water:
        df_diet = pd.DataFrame(
            {
                "date": list(
                    set(dietary_energy.keys())
                    | set(dietary_fat.keys())
                    | set(dietary_carb.keys())
                    | set(dietary_protein.keys())
                    | set(dietary_water.keys())
                )
            }
        )
        df_diet["dietary_kcal"] = df_diet["date"].map(dietary_energy).fillna(0)
        df_diet["dietary_fat_g"] = df_diet["date"].map(dietary_fat).fillna(0)
        df_diet["dietary_carb_g"] = df_diet["date"].map(dietary_carb).fillna(0)
        df_diet["dietary_protein_g"] = df_diet["date"].map(dietary_protein).fillna(0)
        df_diet["dietary_water"] = df_diet["date"].map(dietary_water).fillna(0)
        df_diet = df_diet.sort_values("date").reset_index(drop=True)
        df_diet.to_csv(ROOT / "diet_daily.csv", index=False, encoding="utf-8")

    write_avg_dict(
        ROOT / "audio_exposure_daily.csv",
        audio_env,
        ["env_audio_avg", "env_audio_min", "env_audio_max", "count"],
    )
    write_avg_dict(
        ROOT / "headphone_audio_daily.csv",
        audio_headphone,
        ["headphone_audio_avg", "headphone_audio_min", "headphone_audio_max", "count"],
    )


if __name__ == "__main__":
    parse_export()
    print("解析完成，输出聚合数据（不含原始睡眠片段）")
