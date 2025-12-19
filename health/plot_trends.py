from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
STEPS_CSV = ROOT / "steps_daily.csv"
ENERGY_CSV = ROOT / "energy_daily.csv"
SLEEP_CSV = ROOT / "sleep_daily.csv"
OUT_STEPS = ROOT / "steps_trend.png"
OUT_ENERGY = ROOT / "energy_trend.png"
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
    daily["sleep_ma7"] = daily["sleep_hours"].rolling(window=7, min_periods=1).mean()

    last_date = daily["date"].max()
    cutoff_90 = last_date - pd.Timedelta(days=90)
    cutoff_365 = last_date - pd.Timedelta(days=365)

    recent_90 = daily[daily["date"] >= cutoff_90].set_index("date")
    weekly = recent_90["sleep_ma7"].resample("W-MON").mean().reset_index()

    recent_365 = daily[daily["date"] >= cutoff_365].set_index("date")
    monthly = recent_365["sleep_ma7"].resample("ME").mean().reset_index()

    # 方案：线条+渐变，使用 7 日均值，视觉贴合深色主题，不强制零基线
    def render_series(dates, values, title, outfile, color_line, color_fill):
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#0f172a")

        ax.plot(dates, values, color=color_line, linewidth=2.2)
        min_y = values.min()
        max_y = values.max()
        pad = max((max_y - min_y) * 0.1, 0.2)
        ax.fill_between(dates, values, min_y - pad, color=color_fill, alpha=0.2)
        ax.set_ylim(min_y - pad, max_y + pad)
        ax.set_title(title, color="#e2e8f0")
        ax.set_xlabel("")
        ax.set_ylabel("小时 (7日均值)", color="#cbd5f5")
        ax.tick_params(colors="#cbd5f5")
        for spine in ax.spines.values():
            spine.set_color("#1e293b")
        fig.tight_layout()
        fig.savefig(outfile, dpi=150, facecolor=fig.get_facecolor())
        plt.close(fig)

    render_series(
        weekly["date"],
        weekly["sleep_ma7"],
        "近三个月睡眠时长（按周，7日均值）",
        OUT_SLEEP_WEEKLY,
        "#22c55e",
        "#22c55e",
    )
    render_series(
        monthly["date"],
        monthly["sleep_ma7"],
        "近一年睡眠时长（按月，7日均值）",
        OUT_SLEEP_MONTHLY,
        "#6366f1",
        "#6366f1",
    )


def main():
    plot_steps()
    plot_energy()
    plot_sleep()
    print("Saved charts.")


if __name__ == "__main__":
    main()
