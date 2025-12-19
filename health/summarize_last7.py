from pathlib import Path
from datetime import timedelta
import pandas as pd


def main():
    root = Path(__file__).resolve().parent
    files = [
        p
        for p in root.glob("*.csv")
        if p.name.endswith("_daily.csv") or p.name in {"sleep_daily.csv", "steps_daily.csv", "energy_daily.csv", "weight_daily.csv"}
    ]

    units = {
        "steps": "步",
        "active_energy": "kcal",
        "basal_energy": "kcal",
        "physical_effort": "AU",
        "sleep_hours": "小时",
        "weight_kg": "kg",
        "bmi": "—",
        "body_fat_pct": "%",
        "lean_mass_kg": "kg",
        "height_m": "m",
        "distance_walk_run_km": "km",
        "distance_cycling_km": "km",
        "exercise_time_min": "分钟",
        "stand_time_min": "分钟",
        "stand_hours": "小时",
        "time_in_daylight_min": "分钟",
        "dietary_kcal": "kcal",
        "dietary_fat_g": "g",
        "dietary_carb_g": "g",
        "dietary_protein_g": "g",
        "dietary_water": "mL",
        "hr_avg": "bpm",
        "hr_min": "bpm",
        "hr_max": "bpm",
        "resting_hr_avg": "bpm",
        "resting_hr_min": "bpm",
        "resting_hr_max": "bpm",
        "walk_hr_avg": "bpm",
        "walk_hr_min": "bpm",
        "walk_hr_max": "bpm",
        "sdnn_avg": "ms",
        "sdnn_min": "ms",
        "sdnn_max": "ms",
        "resp_avg": "次/分",
        "resp_min": "次/分",
        "resp_max": "次/分",
        "spo2_avg": "%",
        "spo2_min": "%",
        "spo2_max": "%",
        "vo2max_avg": "ml·kg⁻¹·min⁻¹",
        "vo2max_min": "ml·kg⁻¹·min⁻¹",
        "vo2max_max": "ml·kg⁻¹·min⁻¹",
        "temp_avg": "°C",
        "temp_min": "°C",
        "temp_max": "°C",
        "steady_avg": "分",
        "steady_min": "分",
        "steady_max": "分",
        "walking_speed_avg": "m/s",
        "walking_speed_min": "m/s",
        "walking_speed_max": "m/s",
        "step_length_avg": "m",
        "step_length_min": "m",
        "step_length_max": "m",
        "double_support_pct_avg": "%",
        "double_support_pct_min": "%",
        "double_support_pct_max": "%",
        "asymmetry_pct_avg": "%",
        "asymmetry_pct_min": "%",
        "asymmetry_pct_max": "%",
        "running_speed_avg": "m/s",
        "running_speed_min": "m/s",
        "running_speed_max": "m/s",
        "running_power_avg": "W",
        "running_power_min": "W",
        "running_power_max": "W",
        "running_vertical_osc_avg": "cm",
        "running_vertical_osc_min": "cm",
        "running_vertical_osc_max": "cm",
        "ground_contact_ms_avg": "ms",
        "ground_contact_ms_min": "ms",
        "ground_contact_ms_max": "ms",
        "running_stride_len_avg": "m",
        "running_stride_len_min": "m",
        "running_stride_len_max": "m",
        "stair_ascent_speed_avg": "m/s",
        "stair_ascent_speed_min": "m/s",
        "stair_ascent_speed_max": "m/s",
        "stair_descent_speed_avg": "m/s",
        "stair_descent_speed_min": "m/s",
        "stair_descent_speed_max": "m/s",
        "env_audio_avg": "dB",
        "env_audio_min": "dB",
        "env_audio_max": "dB",
        "headphone_audio_avg": "dB",
        "headphone_audio_min": "dB",
        "headphone_audio_max": "dB",
    }

    lines = []
    for p in sorted(files):
        df = pd.read_csv(p, parse_dates=["date"])
        df = df.sort_values("date")
        if df.empty:
            continue
        last_date = df["date"].max()
        cutoff = last_date - timedelta(days=6)
        recent = df[df["date"] >= cutoff]
        cols = [c for c in df.columns if c != "date"]
        for col in cols:
            val = recent[col].mean()
            lines.append(
                (
                    p.name,
                    col,
                    units.get(col, "(原始单位)"),
                    f"{cutoff.date()} 至 {last_date.date()}",
                    f"{val:.3f}" if pd.notna(val) else "--",
                )
            )

    out_path = root / "_last7_summary.md"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("| 文件 | 指标 | 取值/单位 | 最近7天区间 | 最近7天日均值 |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for row in lines:
            f.write("| " + " | ".join(row) + " |\n")
    print(f"written {out_path}")


if __name__ == "__main__":
    main()
