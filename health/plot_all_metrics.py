from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
CHARTS_DIR = ROOT / "charts"

# 配置：文件 -> 需要绘制的列及中文名、单位
DATASETS = {
    "sleep_daily.csv": [
        ("sleep_hours", "睡眠时长", "小时"),
    ],
    "weight_daily.csv": [("weight_kg", "体重", "kg")],
    "steps_daily.csv": [("steps", "步数", "步")],
    "energy_daily.csv": [
        ("active_energy", "主动能量", "kcal"),
        ("basal_energy", "基础代谢", "kcal"),
        ("physical_effort", "身体负荷指数", "AU"),
    ],
    "body_daily.csv": [
        ("weight_kg", "体重", "kg"),
        ("bmi", "BMI", "—"),
        ("body_fat_pct", "体脂率", "%"),
        ("lean_mass_kg", "去脂体重", "kg"),
        ("height_m", "身高", "m"),
    ],
    "distance_daily.csv": [
        ("distance_walk_run_km", "步行跑步距离", "km"),
        ("distance_cycling_km", "骑行距离", "km"),
    ],
    "exercise_daily.csv": [
        ("exercise_time_min", "锻炼时长", "分钟"),
        ("stand_time_min", "站立时长", "分钟"),
        ("stand_hours", "站立小时数", "小时"),
    ],
    "daylight_daily.csv": [("time_in_daylight_min", "户外日照时长", "分钟")],
    "diet_daily.csv": [
        ("dietary_kcal", "摄入热量", "kcal"),
        ("dietary_fat_g", "脂肪摄入", "g"),
        ("dietary_carb_g", "碳水摄入", "g"),
        ("dietary_protein_g", "蛋白质摄入", "g"),
        ("dietary_water", "饮水量", "mL"),
    ],
    "heart_rate_daily.csv": [
        ("hr_avg", "心率均值", "bpm"),
        ("hr_min", "心率最小值", "bpm"),
        ("hr_max", "心率最大值", "bpm"),
    ],
    "resting_hr_daily.csv": [
        ("resting_hr_avg", "静息心率均值", "bpm"),
        ("resting_hr_min", "静息心率最小值", "bpm"),
        ("resting_hr_max", "静息心率最大值", "bpm"),
    ],
    "walking_hr_daily.csv": [
        ("walk_hr_avg", "步行心率均值", "bpm"),
        ("walk_hr_min", "步行心率最小值", "bpm"),
        ("walk_hr_max", "步行心率最大值", "bpm"),
    ],
    "hrv_daily.csv": [
        ("sdnn_avg", "HRV-SDNN均值", "ms"),
        ("sdnn_min", "HRV-SDNN最小值", "ms"),
        ("sdnn_max", "HRV-SDNN最大值", "ms"),
    ],
    "respiratory_daily.csv": [
        ("resp_avg", "呼吸频率均值", "次/分"),
        ("resp_min", "呼吸频率最小值", "次/分"),
        ("resp_max", "呼吸频率最大值", "次/分"),
    ],
    "spo2_daily.csv": [
        ("spo2_avg", "血氧均值", "%"),
        ("spo2_min", "血氧最小值", "%"),
        ("spo2_max", "血氧最大值", "%"),
    ],
    "vo2max_daily.csv": [
        ("vo2max_avg", "最大摄氧量均值", "ml·kg⁻¹·min⁻¹"),
        ("vo2max_min", "最大摄氧量最小值", "ml·kg⁻¹·min⁻¹"),
        ("vo2max_max", "最大摄氧量最大值", "ml·kg⁻¹·min⁻¹"),
    ],
    "sleep_temp_daily.csv": [
        ("temp_avg", "睡眠手腕温度均值", "°C"),
        ("temp_min", "睡眠手腕温度最小值", "°C"),
        ("temp_max", "睡眠手腕温度最大值", "°C"),
    ],
    "walking_metrics_daily.csv": [
        ("walking_speed_avg", "行走速度均值", "m/s"),
        ("walking_speed_min", "行走速度最小值", "m/s"),
        ("walking_speed_max", "行走速度最大值", "m/s"),
    ],
    "walking_step_length_daily.csv": [
        ("step_length_avg", "步长均值", "m"),
        ("step_length_min", "步长最小值", "m"),
        ("step_length_max", "步长最大值", "m"),
    ],
    "walking_double_support_daily.csv": [
        ("double_support_pct_avg", "双支撑占比均值", "%"),
        ("double_support_pct_min", "双支撑占比最小值", "%"),
        ("double_support_pct_max", "双支撑占比最大值", "%"),
    ],
    "walking_asymmetry_daily.csv": [
        ("asymmetry_pct_avg", "步态不对称均值", "%"),
        ("asymmetry_pct_min", "步态不对称最小值", "%"),
        ("asymmetry_pct_max", "步态不对称最大值", "%"),
    ],
    "walking_steadiness_daily.csv": [
        ("steady_avg", "步态稳定度均值", "分"),
        ("steady_min", "步态稳定度最小值", "分"),
        ("steady_max", "步态稳定度最大值", "分"),
    ],
    "running_speed_daily.csv": [
        ("running_speed_avg", "跑步速度均值", "m/s"),
        ("running_speed_min", "跑步速度最小值", "m/s"),
        ("running_speed_max", "跑步速度最大值", "m/s"),
    ],
    "running_power_daily.csv": [
        ("running_power_avg", "跑步功率均值", "W"),
        ("running_power_min", "跑步功率最小值", "W"),
        ("running_power_max", "跑步功率最大值", "W"),
    ],
    "running_vertical_osc_daily.csv": [
        ("running_vertical_osc_avg", "跑步垂直振幅均值", "cm"),
        ("running_vertical_osc_min", "跑步垂直振幅最小值", "cm"),
        ("running_vertical_osc_max", "跑步垂直振幅最大值", "cm"),
    ],
    "running_ground_contact_daily.csv": [
        ("ground_contact_ms_avg", "着地时间均值", "ms"),
        ("ground_contact_ms_min", "着地时间最小值", "ms"),
        ("ground_contact_ms_max", "着地时间最大值", "ms"),
    ],
    "running_stride_length_daily.csv": [
        ("running_stride_len_avg", "跑步步幅均值", "m"),
        ("running_stride_len_min", "跑步步幅最小值", "m"),
        ("running_stride_len_max", "跑步步幅最大值", "m"),
    ],
    "stair_ascent_speed_daily.csv": [
        ("stair_ascent_speed_avg", "上楼速度均值", "m/s"),
        ("stair_ascent_speed_min", "上楼速度最小值", "m/s"),
        ("stair_ascent_speed_max", "上楼速度最大值", "m/s"),
    ],
    "stair_descent_speed_daily.csv": [
        ("stair_descent_speed_avg", "下楼速度均值", "m/s"),
        ("stair_descent_speed_min", "下楼速度最小值", "m/s"),
        ("stair_descent_speed_max", "下楼速度最大值", "m/s"),
    ],
    "audio_exposure_daily.csv": [
        ("env_audio_avg", "环境噪声均值", "dB"),
        ("env_audio_min", "环境噪声最小值", "dB"),
        ("env_audio_max", "环境噪声最大值", "dB"),
    ],
    "headphone_audio_daily.csv": [
        ("headphone_audio_avg", "耳机音量均值", "dB"),
        ("headphone_audio_min", "耳机音量最小值", "dB"),
        ("headphone_audio_max", "耳机音量最大值", "dB"),
    ],
}

# 图表样式
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def render_series(dates, values, title: str, outfile: Path, ylabel: str):
    fig, ax = plt.subplots(figsize=(9.5, 4))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")

    min_y = values.min()
    max_y = values.max()
    pad = max((max_y - min_y) * 0.1, 0.1)
    lower = min_y - pad
    upper = max_y + pad

    ax.plot(
        dates,
        values,
        color="#60a5fa",
        linewidth=2.1,
        solid_capstyle="round",
        label="7日滚动均值",
    )
    ax.fill_between(dates, values, lower, color="#60a5fa", alpha=0.16)
    ax.set_ylim(lower, upper)

    ax.set_title(title, color="#e2e8f0", pad=10)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel, color="#cbd5f5")
    ax.tick_params(colors="#cbd5f5", labelsize=9)
    ax.grid(True, color="#94a3b8", alpha=0.18, linewidth=0.8, linestyle="--")
    for spine in ax.spines.values():
        spine.set_color("#1f2937")

    fig.tight_layout()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outfile, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def process_file(csv_name: str, columns: List[tuple[str, str, str]]):
    path = ROOT / csv_name
    if not path.exists():
        return
    df = pd.read_csv(path, parse_dates=["date"])
    if df.empty:
        return
    df.sort_values("date", inplace=True)
    last_date = df["date"].max()
    cutoff = last_date - pd.Timedelta(days=365)
    df = df[df["date"] >= cutoff]
    if df.empty:
        df = df.iloc[-60:]  # fallback

    for col, cname, unit in columns:
        if col not in df.columns:
            continue
        series = df[["date", col]].dropna()
        if series.empty:
            continue
        series["ma7"] = series[col].rolling(window=7, min_periods=1).mean()
        outfile = CHARTS_DIR / f"{path.stem}__{col}.png"
        render_series(series["date"], series["ma7"], f"{cname}（7日均值）", outfile, unit)


def main():
    for csv_name, cols in DATASETS.items():
        process_file(csv_name, cols)
    print("Charts generated into", CHARTS_DIR)


if __name__ == "__main__":
    main()
