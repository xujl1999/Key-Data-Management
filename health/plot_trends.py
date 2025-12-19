from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
STEPS_CSV = ROOT / "steps_daily.csv"
ENERGY_CSV = ROOT / "energy_daily.csv"
SLEEP_CSV = ROOT / "sleep_daily.csv"

OUT_STEPS = ROOT / "steps_trend.png"
OUT_ENERGY = ROOT / "energy_trend.png"
OUT_SLEEP = ROOT / "sleep_trend.png"
OUT_SLEEP_WEEKLY = ROOT / "sleep_weekly.png"
OUT_SLEEP_MONTHLY = ROOT / "sleep_monthly.png"


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
    df = pd.read_csv(SLEEP_CSV, parse_dates=["date"])
    df.sort_values("date", inplace=True)
    daily = df.copy()

    # 全量日趋势
    plt.figure(figsize=(10, 4))
    plt.plot(daily["date"], daily["sleep_hours"], label="Sleep Hours", color="#22c55e")
    plt.title("Daily Sleep Duration")
    plt.xlabel("Date")
    plt.ylabel("Sleep Hours")
    plt.tight_layout()
    plt.savefig(OUT_SLEEP, dpi=150)
    plt.close()

    # 近三个月按周
    last_date = daily["date"].max()
    cutoff_90 = last_date - pd.Timedelta(days=90)
    recent_90 = daily[daily["date"] >= cutoff_90].set_index("date")
    weekly = recent_90["sleep_hours"].resample("W-MON").sum().reset_index()
    plt.figure(figsize=(10, 4))
    plt.plot(weekly["date"], weekly["sleep_hours"], color="#22c55e")
    plt.title("Sleep Hours (Weekly, Last 3 Months)")
    plt.xlabel("Week (Mon)")
    plt.ylabel("Sleep Hours")
    plt.tight_layout()
    plt.savefig(OUT_SLEEP_WEEKLY, dpi=150)
    plt.close()

    # 近一年按月
    cutoff_365 = last_date - pd.Timedelta(days=365)
    recent_365 = daily[daily["date"] >= cutoff_365].set_index("date")
    monthly = recent_365["sleep_hours"].resample("M").sum().reset_index()
    plt.figure(figsize=(10, 4))
    plt.plot(monthly["date"], monthly["sleep_hours"], color="#a855f7")
    plt.title("Sleep Hours (Monthly, Last 12 Months)")
    plt.xlabel("Month")
    plt.ylabel("Sleep Hours")
    plt.tight_layout()
    plt.savefig(OUT_SLEEP_MONTHLY, dpi=150)
    plt.close()


def main():
    plot_steps()
    plot_energy()
    plot_sleep()
    print("Saved:", OUT_STEPS, OUT_ENERGY, OUT_SLEEP, OUT_SLEEP_WEEKLY, OUT_SLEEP_MONTHLY)


if __name__ == "__main__":
    main()
