import pandas as pd
from datetime import datetime, timedelta
import sys

def analyze():
    try:
        df = pd.read_csv("health/data/workouts_daily.csv")
    except FileNotFoundError:
        print("workouts_daily.csv not found.")
        return

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    recent = df[df['date'] >= cutoff]
    
    if recent.empty:
        print("No workouts found in the last 30 days.")
        return

    
    # Aggregation
    grouped = recent.groupby(['workout_type', 'source']).agg({
        'duration_min': 'sum',
        'energy_kcal': 'sum',
        'date': 'count'
    }).rename(columns={'date': 'count'}).reset_index()
    
    # Sort
    grouped = grouped.sort_values('duration_min', ascending=False)
    
    with open("analysis_output.md", "w", encoding="utf-8") as f:
        f.write(f"### 最近30天运动数据分析 ({cutoff.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')})\n\n")
        
        # Format Table
        f.write("| 运动类型 | 来源 | 次数 | 总时长(分) | 总消耗(kcal) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for _, row in grouped.iterrows():
            f.write(f"| {row['workout_type']} | {row['source']} | {row['count']} | {row['duration_min']:.1f} | {row['energy_kcal']:.1f} |\n")

        print("Analysis written to analysis_output.md")
        
        f.write("\n\n### 明细数据 (最近10条)\n")
        f.write("| 日期 | 类型 | 来源 | 时长(分) | 消耗(kcal) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        recent_sorted = recent.sort_values('date', ascending=False).head(10)
        for _, row in recent_sorted.iterrows():
             f.write(f"| {row['date'].strftime('%Y-%m-%d %H:%M')} | {row['workout_type']} | {row['source']} | {row['duration_min']:.1f} | {row['energy_kcal']:.1f} |\n")

if __name__ == "__main__":
    analyze()
