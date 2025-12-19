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

# 统一中文字体与减号显示
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

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
    recent_90 = daily[daily["date"] >= cutoff_90]

    # 方案1：深色背景 + 霓虹线条 + 柔和渐变，突出波动，不强制零基线
    def render_series(dates, values, title, outfile, color_line, color_fill):
        fig, ax = plt.subplots(figsize=(10, 4.2))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#0f172a")

        min_y = values.min()
        max_y = values.max()
        pad = max((max_y - min_y) * 0.1, 0.2)
        lower = min_y - pad
        upper = max_y + pad

        ax.plot(
            dates,
            values,
            color=color_line,
            linewidth=2.6,
            solid_capstyle="round",
            label="7日滚动均值",
        )
        ax.fill_between(dates, values, lower, color=color_fill, alpha=0.16)
        ax.set_ylim(lower, upper)

        ax.set_title(title, color="#e2e8f0", pad=12)
        ax.set_xlabel("")
        ax.set_ylabel("睡眠时长（7日均值，小时）", color="#cbd5f5")
        ax.tick_params(colors="#cbd5f5", labelsize=9)
        ax.grid(True, color="#94a3b8", alpha=0.18, linewidth=0.8, linestyle="--")
        legend = ax.legend(
            loc="upper left",
            frameon=True,
            facecolor="#0f172a",
            edgecolor="#1f2937",
            labelcolor="#cbd5f5",
        )
        if legend:
            legend.get_frame().set_alpha(0.6)
        for spine in ax.spines.values():
            spine.set_color("#1f2937")
        fig.tight_layout()
        fig.savefig(outfile, dpi=180, facecolor=fig.get_facecolor())
        plt.close(fig)

    render_series(
        recent_90["date"],
        recent_90["sleep_ma7"],
        "近三个月睡眠时长（滑动7日均值）",
        OUT_SLEEP_WEEKLY,
        "#22c55e",
        "#22c55e",
    )


def main():
    plot_steps()
    plot_energy()
    plot_sleep()
    print("Saved charts.")


if __name__ == "__main__":
    main()
