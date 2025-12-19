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

    metric_names = {
        "steps": "步数",
        "active_energy": "主动能量",
        "basal_energy": "基础代谢",
        "physical_effort": "身体负荷指数",
        "sleep_hours": "睡眠时长",
        "weight_kg": "体重",
        "bmi": "BMI",
        "body_fat_pct": "体脂率",
        "lean_mass_kg": "去脂体重",
        "height_m": "身高",
        "distance_walk_run_km": "步行跑步距离",
        "distance_cycling_km": "骑行距离",
        "exercise_time_min": "锻炼时长",
        "stand_time_min": "站立时长",
        "stand_hours": "站立小时数",
        "time_in_daylight_min": "户外日照时长",
        "dietary_kcal": "摄入热量",
        "dietary_fat_g": "脂肪摄入",
        "dietary_carb_g": "碳水摄入",
        "dietary_protein_g": "蛋白质摄入",
        "dietary_water": "饮水量",
        "hr_avg": "心率均值",
        "hr_min": "心率最小值",
        "hr_max": "心率最大值",
        "resting_hr_avg": "静息心率均值",
        "resting_hr_min": "静息心率最小值",
        "resting_hr_max": "静息心率最大值",
        "walk_hr_avg": "步行心率均值",
        "walk_hr_min": "步行心率最小值",
        "walk_hr_max": "步行心率最大值",
        "sdnn_avg": "HRV-SDNN均值",
        "sdnn_min": "HRV-SDNN最小值",
        "sdnn_max": "HRV-SDNN最大值",
        "resp_avg": "呼吸频率均值",
        "resp_min": "呼吸频率最小值",
        "resp_max": "呼吸频率最大值",
        "spo2_avg": "血氧均值",
        "spo2_min": "血氧最小值",
        "spo2_max": "血氧最大值",
        "vo2max_avg": "最大摄氧量均值",
        "vo2max_min": "最大摄氧量最小值",
        "vo2max_max": "最大摄氧量最大值",
        "temp_avg": "睡眠手腕温度均值",
        "temp_min": "睡眠手腕温度最小值",
        "temp_max": "睡眠手腕温度最大值",
        "steady_avg": "步态稳定度均值",
        "steady_min": "步态稳定度最小值",
        "steady_max": "步态稳定度最大值",
        "walking_speed_avg": "行走速度均值",
        "walking_speed_min": "行走速度最小值",
        "walking_speed_max": "行走速度最大值",
        "step_length_avg": "步长均值",
        "step_length_min": "步长最小值",
        "step_length_max": "步长最大值",
        "double_support_pct_avg": "双支撑占比均值",
        "double_support_pct_min": "双支撑占比最小值",
        "double_support_pct_max": "双支撑占比最大值",
        "asymmetry_pct_avg": "步态不对称均值",
        "asymmetry_pct_min": "步态不对称最小值",
        "asymmetry_pct_max": "步态不对称最大值",
        "running_speed_avg": "跑步速度均值",
        "running_speed_min": "跑步速度最小值",
        "running_speed_max": "跑步速度最大值",
        "running_power_avg": "跑步功率均值",
        "running_power_min": "跑步功率最小值",
        "running_power_max": "跑步功率最大值",
        "running_vertical_osc_avg": "跑步垂直振幅均值",
        "running_vertical_osc_min": "跑步垂直振幅最小值",
        "running_vertical_osc_max": "跑步垂直振幅最大值",
        "ground_contact_ms_avg": "着地时间均值",
        "ground_contact_ms_min": "着地时间最小值",
        "ground_contact_ms_max": "着地时间最大值",
        "running_stride_len_avg": "跑步步幅均值",
        "running_stride_len_min": "跑步步幅最小值",
        "running_stride_len_max": "跑步步幅最大值",
        "stair_ascent_speed_avg": "上楼速度均值",
        "stair_ascent_speed_min": "上楼速度最小值",
        "stair_ascent_speed_max": "上楼速度最大值",
        "stair_descent_speed_avg": "下楼速度均值",
        "stair_descent_speed_min": "下楼速度最小值",
        "stair_descent_speed_max": "下楼速度最大值",
        "env_audio_avg": "环境噪声均值",
        "env_audio_min": "环境噪声最小值",
        "env_audio_max": "环境噪声最大值",
        "headphone_audio_avg": "耳机音量均值",
        "headphone_audio_min": "耳机音量最小值",
        "headphone_audio_max": "耳机音量最大值",
        "count": "样本数",
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
                    metric_names.get(col, col),
                    units.get(col, "(原始单位)"),
                    f"{cutoff.date()} 至 {last_date.date()}",
                    f"{val:.3f}" if pd.notna(val) else "--",
                )
            )

    out_path = root / "_last7_summary.md"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("| 文件 | 指标 | 指标中文名 | 取值/单位 | 最近7天区间 | 最近7天日均值 |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for row in lines:
            f.write("| " + " | ".join(row) + " |\n")
    print(f"written {out_path}")


if __name__ == "__main__":
    main()
