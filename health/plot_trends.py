from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
STEPS_CSV = ROOT / "steps_daily.csv"
ENERGY_CSV = ROOT / "energy_daily.csv"
SLEEP_CSV = ROOT / "sleep_daily.csv"

OUT_STEPS = ROOT / "steps_trend.png"
OUT_ENERGY = ROOT / "energy_trend.png"

SLEEP_WEEKLY_OPTS = [
    ROOT / "sleep_weekly_opt1.png",
    ROOT / "sleep_weekly_opt2.png",
    ROOT / "sleep_weekly_opt3.png",
]
SLEEP_MONTHLY_OPTS = [
    ROOT / "sleep_monthly_opt1.png",
    ROOT / "sleep_monthly_opt2.png",
    ROOT / "sleep_monthly_opt3.png",
]


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
    daily["sleep_ma7"] = daily["sleep_hours"].rolling(window=7, min_periods=1).mean()

    last_date = daily["date"].max()
    cutoff_90 = last_date - pd.Timedelta(days=90)
    cutoff_365 = last_date - pd.Timedelta(days=365)

    recent_90 = daily[daily["date"] >= cutoff_90].set_index("date")
    weekly = recent_90["sleep_ma7"].resample("W-MON").mean().reset_index()

    recent_365 = daily[daily["date"] >= cutoff_365].set_index("date")
    monthly = recent_365["sleep_ma7"].resample("ME").mean().reset_index()

    # 方案1：简洁线 + 渐变填充
    plt.figure(figsize=(10, 4))
    plt.plot(weekly["date"], weekly["sleep_ma7"], color="#22c55e", linewidth=2)
    plt.fill_between(
        weekly["date"], weekly["sleep_ma7"], color="#22c55e", alpha=0.15
    )
    plt.title("Sleep (Weekly Avg, Last 3 Months)")
    plt.xlabel("Week (Mon)")
    plt.ylabel("Hours (7d MA)")
    plt.tight_layout()
    plt.savefig(SLEEP_WEEKLY_OPTS[0], dpi=150)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.plot(monthly["date"], monthly["sleep_ma7"], color="#6366f1", linewidth=2)
    plt.fill_between(
        monthly["date"], monthly["sleep_ma7"], color="#6366f1", alpha=0.15
    )
    plt.title("Sleep (Monthly Avg, Last 12 Months)")
    plt.xlabel("Month")
    plt.ylabel("Hours (7d MA)")
    plt.tight_layout()
    plt.savefig(SLEEP_MONTHLY_OPTS[0], dpi=150)
    plt.close()

    # 方案2：面积图 + 标记
    plt.figure(figsize=(10, 4))
    plt.fill_between(
        weekly["date"], weekly["sleep_ma7"], color="#0ea5e9", alpha=0.25
    )
    plt.plot(weekly["date"], weekly["sleep_ma7"], color="#0ea5e9", linewidth=2.5)
    plt.scatter(weekly["date"], weekly["sleep_ma7"], color="#0ea5e9", s=18, alpha=0.9)
    plt.title("Sleep (Weekly, Last 3 Months)")
    plt.xlabel("Week (Mon)")
    plt.ylabel("Hours (7d MA)")
    plt.tight_layout()
    plt.savefig(SLEEP_WEEKLY_OPTS[1], dpi=150)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.fill_between(
        monthly["date"], monthly["sleep_ma7"], color="#ec4899", alpha=0.25
    )
    plt.plot(monthly["date"], monthly["sleep_ma7"], color="#ec4899", linewidth=2.5)
    plt.scatter(monthly["date"], monthly["sleep_ma7"], color="#ec4899", s=18, alpha=0.9)
    plt.title("Sleep (Monthly, Last 12 Months)")
    plt.xlabel("Month")
    plt.ylabel("Hours (7d MA)")
    plt.tight_layout()
    plt.savefig(SLEEP_MONTHLY_OPTS[1], dpi=150)
    plt.close()

    # 方案3：柱状 + 线条叠加
    plt.figure(figsize=(10, 4))
    plt.bar(weekly["date"], weekly["sleep_ma7"], color="#f97316", alpha=0.7)
    plt.plot(weekly["date"], weekly["sleep_ma7"], color="#1f2937", linewidth=1.8)
    plt.title("Sleep (Weekly Bars, Last 3 Months)")
    plt.xlabel("Week (Mon)")
    plt.ylabel("Hours (7d MA)")
    plt.tight_layout()
    plt.savefig(SLEEP_WEEKLY_OPTS[2], dpi=150)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.bar(monthly["date"], monthly["sleep_ma7"], color="#22c55e", alpha=0.7)
    plt.plot(monthly["date"], monthly["sleep_ma7"], color="#1f2937", linewidth=1.8)
    plt.title("Sleep (Monthly Bars, Last 12 Months)")
    plt.xlabel("Month")
    plt.ylabel("Hours (7d MA)")
    plt.tight_layout()
    plt.savefig(SLEEP_MONTHLY_OPTS[2], dpi=150)
    plt.close()


def main():
    plot_steps()
    plot_energy()
    plot_sleep()
    print("Saved charts.")


if __name__ == "__main__":
    main()
