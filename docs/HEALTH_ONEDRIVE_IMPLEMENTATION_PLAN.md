# Health 数据链路实施计划（iPad -> OneDrive -> Mac 自动入库校验）

## 1. 目标与原则

目标：把“手动导出+手动处理”升级为**准自动、可追溯、可告警**的数据流水线。

原则：
- 幂等：同一份导出文件不会重复入库污染。
- 可观测：每次运行都有状态与日志。
- 可恢复：失败后可重跑、可定位。
- 最小入侵：复用现有 `health/scripts/*.py`。

---

## 2. 端到端流程

```text
iPad 快捷指令（定时）
  -> 生成 Apple Health 导出 zip（文件名含日期）
  -> 存入 OneDrive /DATA/
  -> Mac 定时任务触发 update_from_onedrive.py
  -> 解析为 health/data/*.csv
  -> 生成 _last7_summary.md + _data_quality.md
  -> 质量闸门判定（成功/失败）
  -> 失败时发送告警
```

---

## 3. 文件格式与目录约定

## 3.1 OneDrive 输入约定

- 目录：`OneDrive/DATA/`
- 文件名：`导出_YYYYMMDD_HHMM.zip`（建议）
- 保底兼容：`导出*.zip`（现脚本已支持）

## 3.2 仓库内约定

- 原始包（当前处理对象）：`health/导出.zip`
- 聚合输出：`health/data/*.csv`
- 质量报告：`health/_data_quality.md`
- 近7天摘要：`health/_last7_summary.md`
- 运行日志（新增建议）：`health/logs/health_pipeline.log`
- 运行清单（新增建议）：`health/logs/ingest_manifest.csv`

---

## 4. 幂等策略

建议在 `update_from_onedrive.py` 增加（或外层脚本实现）以下策略：

1. **内容指纹去重**
   - 计算输入 zip 的 SHA256。
   - 若 `ingest_manifest.csv` 已存在同 hash 且状态 success，则直接跳过。
2. **原子替换**
   - 继续保持当前 `tmp -> os.replace` 方式（已具备）。
3. **单实例锁**
   - 创建 `health/.pipeline.lock`；任务开始加锁，结束释放。
   - 避免双触发并发写同一批 CSV。

---

## 5. 质量闸门（Quality Gates）

每次入库后执行下列闸门，任一失败即标记 run=failed：

- Gate-1：`health/data/steps_daily.csv` 存在且非空。
- Gate-2：核心文件最新日期 >= (今天-2天)。
  - 核心：`steps_daily.csv`、`sleep_daily.csv`、`energy_daily.csv`。
- Gate-3：`quality_report.py --days 14` 执行成功。
- Gate-4：无明显异常边界值（脚本已有基础边界校验）。

---

## 6. 失败告警方案

优先级从低到高：

1. 本地日志落盘（必须）
2. 终端通知（macOS `osascript`）
3. IM 通知（可后续接入 OpenClaw `message`）

建议告警内容：
- 失败阶段（拉取/解析/质量）
- 输入文件名 + hash
- 错误摘要 + 最近 30 行日志路径

---

## 7. 可执行步骤（落地顺序）

## Step A：iPad 快捷指令

- 定时（每日 06:30 或睡前）执行：
  - 导出健康数据
  - 保存到 OneDrive/DATA
- 文件名模板：`导出_当前日期_当前时间.zip`

## Step B：Mac 自动任务（launchd）

示例每 30 分钟跑一次：

```bash
python3 health/scripts/update_from_onedrive.py --no-wait
python3 health/scripts/quality_report.py --days 14
```

## Step C：质量闸门脚本（新增建议）

- 新增 `health/scripts/health_gate.py`
- 检查上述 Gate-1~4
- 失败返回非零并写日志

## Step D：失败告警（新增建议）

- 先本地通知，后续可扩展到 IM。

---

## 8. 运维命令清单

```bash
# 手动触发全流程
python3 health/scripts/update_from_onedrive.py --no-wait

# 只做质量报告
python3 health/scripts/quality_report.py --days 14

# 查看最近报告
cat health/_data_quality.md
cat health/_last7_summary.md
```

---

## 9. 风险与应对

- 风险1：OneDrive 文件未完全同步就被处理
  - 应对：保留并加强“稳定性检查”（size+mtime 多次一致）
- 风险2：重复触发导致并发冲突
  - 应对：锁文件 + 单实例
- 风险3：Apple 导出格式变更
  - 应对：`parse_export.py` 增加异常指标日志与回退策略
- 风险4：静默失败无人知晓
  - 应对：manifest + 告警 + 每日摘要

---

## 10. 验收标准

- 连续 7 天无需人工介入，日常自动完成入库。
- 至少核心三表（steps/sleep/energy）持续更新。
- 任一失败可在 5 分钟内定位到具体阶段与错误。
