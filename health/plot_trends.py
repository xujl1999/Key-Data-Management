from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
STEPS_CSV = ROOT / "steps_daily.csv"
ENERGY_CSV = ROOT / "energy_daily.csv"
SLEEP_CSV = ROOT / "sleep_sessions.csv"

OUT_STEPS = ROOT / "steps_trend.png"
OUT_ENERGY = ROOT / "energy_trend.png"
OUT_SLEEP = ROOT / "sleep_trend.png"


def plot_steps():
    df = pd.read_csv(STEPS_CSV, parse_dates=["date"])
    df.sort_values("date", inplace=True)
    plt.figure(figsize=(10, 4))
    plt.plot(df["date"], df["steps"], label="Steps", color="#60a5fa")
    plt.title("Daily Steps")
    plt.xlabel("Date")
    plt.ylabel("Steps")
    plt.tight_layout()
    OUT_STEPS.parent.mkdir(exist_ok=True)
    plt.savefig(OUT_STEPS, dpi=150)
    plt.close()


def plot_energy():
    df = pd.read_csv(ENERGY_CSV, parse_dates=["date"])
    df.sort_values("date", inplace=True)
    plt.figure(figsize=(10, 4))
    plt.plot(df["date"], df["active_energy"], label="Active Energy", color="#f97316")
    plt.title("Daily Active Energy")
    plt.xlabel("Date")
    plt.ylabel("Active Energy (kcal)")
    plt.tight_layout()
    plt.savefig(OUT_ENERGY, dpi=150)
    plt.close()


def plot_sleep():
    df = pd.read_csv(SLEEP_CSV, parse_dates=["start", "end"])
    # 按开始日期汇总睡眠时长
    df["date"] = df["start"].dt.date
    daily = df.groupby("date")["duration_hours"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily.sort_values("date", inplace=True)
    plt.figure(figsize=(10, 4))
    plt.plot(daily["date"], daily["duration_hours"], label="Sleep Hours", color="#22c55e")
    plt.title("Daily Sleep Duration")
    plt.xlabel("Date")
    plt.ylabel("Sleep Hours")
    plt.tight_layout()
    plt.savefig(OUT_SLEEP, dpi=150)
    plt.close()


def main():
    plot_steps()
    plot_energy()
    plot_sleep()
    print("Saved:", OUT_STEPS, OUT_ENERGY, OUT_SLEEP)


if __name__ == "__main__":
    main()
