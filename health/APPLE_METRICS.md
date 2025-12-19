# Apple 健康数据解析概览

当前解析脚本：`health/parse_export.py`  
数据来源：`health/导出.zip`（Apple 健康导出包），解析后输出到 `health/` 目录。

## 已解析并落地的指标
- `sleep_daily.csv`
  - `date`: 日期（本地时区）
  - `sleep_hours`: 每日睡眠总时长（小时），来自 `HKCategoryTypeIdentifierSleepAnalysis` 累加。
- `steps_daily.csv`
  - `date`
  - `steps`: 步数，来自 `HKQuantityTypeIdentifierStepCount` 累加。
- `energy_daily.csv`
  - `date`
  - `active_energy`: 主动消耗能量（kcal），来自 `HKQuantityTypeIdentifierActiveEnergyBurned` 累加。
- `weight_daily.csv`
  - `date`
  - `weight_kg`: 体重（kg），同一天多次记录取平均，来自 `HKQuantityTypeIdentifierBodyMass`。

## 可视化使用的派生文件
- `sleep_weekly.png`：睡眠 7 日滚动均值趋势（近一年），含目标/预警线。
- `weight_trend.png`：体重 7 日滚动均值趋势（近一年），含目标/预警线。

## 解析要点
- 时区偏移会被规范化（`+0800` → `+08:00`），避免解析异常。
- 仅生成聚合数据，不输出原始片段，保护隐私与体积。
- 体重多次测量取日均值，方便趋势分析。

## 未来可扩展的指标（未解析）
- 心率（静息/平均/区间）、心率变异性
- 运动记录：距离、配速、心率区间、分部位力量训练频率
- 血糖/动态血糖仪数据
- 呼吸率、血氧、体温
- 营养/饮食成分（如碳水/蛋白质/脂肪）

如需新增指标，可在 `parse_export.py` 中对对应的 `HKQuantityTypeIdentifier*` 或 `HKCategoryTypeIdentifier*` 进行累加/聚合并输出为新的 CSV。***
