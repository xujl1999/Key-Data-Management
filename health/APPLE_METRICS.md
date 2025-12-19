# Apple 健康数据解析概览

当前解析脚本：`health/parse_export.py`  
数据来源：`health/导出.zip`（Apple 健康导出包），解析后输出到 `health/` 目录。

## 已解析并落地的指标

### 基础运动 / 能量
- `steps_daily.csv`: `steps`
- `energy_daily.csv`: `active_energy`, `basal_energy`, `physical_effort`
- `distance_daily.csv`: `distance_walk_run_km`, `distance_cycling_km`
- `exercise_daily.csv`: `exercise_time_min`, `stand_time_min`, `stand_hours`
- `flights_daily.csv`: `flights_climbed`
- `daylight_daily.csv`: `time_in_daylight_min`

### 睡眠
- `sleep_daily.csv`: `sleep_hours`
- `sleep_temp_daily.csv`: 手腕温度均值/极值（睡眠相关）
- `sleep_weekly.png`: 睡眠 7 日滚动均值趋势（近一年，含目标/预警线）

### 体重 / 体成分
- `weight_daily.csv`: `weight_kg`
- `body_daily.csv`: `weight_kg`, `bmi`, `body_fat_pct`, `lean_mass_kg`, `height_m`
- `weight_trend.png`: 体重 7 日滚动均值趋势（近一年，含目标/预警线）

### 心血管 / 呼吸
- `heart_rate_daily.csv`: 日均/极值/样本数（心率）
- `resting_hr_daily.csv`: 静息心率均值/极值
- `walking_hr_daily.csv`: 步行平均心率均值/极值
- `hrv_daily.csv`: 心率变异性 SDNN 均值/极值
- `respiratory_daily.csv`: 呼吸频率均值/极值
- `spo2_daily.csv`: 血氧均值/极值
- `vo2max_daily.csv`: 最大摄氧量均值/极值

### 步态 / 运动质量
- `walking_metrics_daily.csv`: 行走速度均值/极值
- `walking_step_length_daily.csv`: 步长均值/极值
- `walking_double_support_daily.csv`: 双支撑百分比均值/极值
- `walking_asymmetry_daily.csv`: 步态不对称度均值/极值
- `walking_steadiness_daily.csv`: 稳定度评分均值/极值
- `running_speed_daily.csv`: 跑步速度均值/极值
- `running_power_daily.csv`: 跑步功率均值/极值
- `running_vertical_osc_daily.csv`: 垂直振幅均值/极值
- `running_ground_contact_daily.csv`: 接地时间均值/极值
- `running_stride_length_daily.csv`: 步幅均值/极值
- `stair_ascent_speed_daily.csv` / `stair_descent_speed_daily.csv`: 爬/下楼速度均值/极值

### 营养 / 饮水
- `diet_daily.csv`: `dietary_kcal`, `dietary_fat_g`, `dietary_carb_g`, `dietary_protein_g`, `dietary_water`

### 环境 / 音频暴露
- `audio_exposure_daily.csv`: 环境噪声均值/极值
- `headphone_audio_daily.csv`: 耳机音量暴露均值/极值

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
