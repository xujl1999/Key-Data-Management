# Health Data Quality Report

Generated: 2026-02-01 23:32:07

Window: last 14 days (per-file, aligned to each file's latest date)

| file | status | last_date | coverage | notes | sparkline |
| --- | --- | --- | --- | --- | --- |
| steps_daily.csv | OK | 2026-01-31 | 100% |  | █▆▅▅▆▆▅▄▅▆▅▆▇▁ |
| sleep_daily.csv | MISS(1) | 2026-01-31 | 93% | sleep_hours:max>24 | ·▃█▇█▅▃█▆▁▇▆▇▄ |
| weight_daily.csv | MISS(7) | 2026-01-30 | 50% |  | ··█▆▅▆▄·▃····▁ |
| energy_daily.csv | OK | 2026-01-31 | 100% |  | █▆▅▅▆▆▇▅▅▅▅▆▇▁ |
| heart_rate_daily.csv | OK | 2026-01-31 | 100% |  | █▅▅▅▅▅▇▄▄▄▄▅▅▁ |

## How to read
- status=MISS(n): within the recent window, n dates are missing from this csv.
- notes: basic sanity flags (missing columns / impossible bounds / 7-day flatline).
- sparkline: first important metric's recent trend; missing days shown as '·'.
