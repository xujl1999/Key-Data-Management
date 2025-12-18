# 苹果健康导出数据概览

本目录存放从 iOS 健康 App 一键导出的原始数据压缩包，仅供后续学习/分析使用。

## 内容结构（来自 `health/导出.zip`）
- `apple_health_export/workout-routes/*.gpx`：共 90 个 GPX 轨迹文件，对应锻炼路线。
- `apple_health_export/electrocardiograms/*.csv`：共 11 个心电（ECG）导出 CSV，文件名按日期。
- `apple_health_export/export_cda.xml`：CDA 格式的健康档案。
- `apple_health_export/蟽禄鈺澫兠р晳.xml`：文件名编码异常，推测是主导出的 `export.xml`（包含大量记录数据）；解压后可手动改名查看。

总计 103 个文件（90 GPX + 11 CSV + 2 XML）。

## 已解析的摘要结果（health/parse_export.py）
- 解析脚本：`python health/parse_export.py`（会自动从 `导出.zip` 中挑主 XML，提取记录并生成 3 个 CSV）
- 输出文件：
  - `health/steps_daily.csv`：按日汇总步数（共 724 天，范围 2023-12-26 ~ 2025-12-18）
  - `health/energy_daily.csv`：按日汇总主动能量（kcal，716 天，同日期范围）
  - `health/sleep_daily.csv`：睡眠时长按日汇总（小时），供前端趋势图使用
  - 趋势图：`health/steps_trend.png`、`health/energy_trend.png`、`health/sleep_trend.png`（由 `plot_trends.py` 生成）

### 解析规则简述
- 主 XML：自动选择压缩包中非 `cda` 的 XML（编码异常的主导出文件也会被识别），逐条流式解析 `<Record>`。
- 步数：`HKQuantityTypeIdentifierStepCount`，按 `startDate` 的日期聚合求和。
- 主动能量：`HKQuantityTypeIdentifierActiveEnergyBurned`，按日期聚合求和。
- 睡眠：`HKCategoryTypeIdentifierSleepAnalysis`，计算 (end-start) 的小时数，聚合到开始日期（小时）。

### 复现
```bash
python health/parse_export.py
# 生成 health/steps_daily.csv, energy_daily.csv, sleep_daily.csv
# 生成趋势图（如需）：python health/plot_trends.py
```

## 趋势图预览
- 步数趋势：`health/steps_trend.png`
- 主动能量趋势：`health/energy_trend.png`
- 睡眠时长趋势：`health/sleep_trend.png`

## 快速查看/解压
```bash
# 查看压缩包目录
python health/tmp_list.py  # 已生成 zip_listing.txt

# 解压到子目录（示例）
python -m zipfile -e health/导出.zip health/unpacked
```

## 后续分析建议
- **主记录解析**：解压后找到疑似的主 XML（编码异常文件），将其改名为 `export.xml`，用 `ElementTree`/`lxml` 解析各类 `<Record>` 数据；可按类型聚合（步数、能量、睡眠等）。
- **锻炼路线**：批量遍历 `workout-routes/*.gpx` 提取时间、距离、坐标序列，结合主 XML 中的 Workout 记录进行匹配。
- **ECG**：CSV 内容以中文键值对形式存储（示例仅一列 `姓名`，行里含出生日期、记录时间、分类、症状、软件版本等），建议按行解析为键值对再汇总为表格。
- **隐私合规**：数据仅供个人学习分析，不要上传到公共服务或共享给无关方。

## 常用代码片段
```python
from pathlib import Path
import zipfile
import pandas as pd

zip_path = Path("health/导出.zip")
with zipfile.ZipFile(zip_path) as zf:
    # 列出文件
    names = zf.namelist()

    # 读取一个 GPX 内容
    gpx_bytes = zf.read("apple_health_export/workout-routes/route_2025-02-19_8.31pm.gpx")

    # 读取一个 ECG CSV（需按行拆键值）
    with zf.open("apple_health_export/electrocardiograms/ecg_2025-02-24.csv") as f:
        lines = [line.decode("utf-8").strip() for line in f]
        # lines 内包含“姓名”、“出生日期”、“记录日期”、“分类”、“症状”、“软件版本”等键值行
```
