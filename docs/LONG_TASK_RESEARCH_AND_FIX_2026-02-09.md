# 长任务研究与修复设计报告（2026-02-09）

## 0. 结论摘要

- 已完成 `video/`、`health/`、`docs/` 全面审阅，并整理当前链路图。
- 已对 `video/get_video_ls.py` 做**最小可回滚改动**：
  - 保留原选择器主逻辑；
  - 增加多选择器兜底；
  - 增加失败原因日志（JSONL）；
  - 增加单作者 smoke test 参数。
- 已本地验证单作者可抓到数据：`rows=1`（非 mock）。
- 已补充 health 链路实施计划（见 `docs/HEALTH_ONEDRIVE_IMPLEMENTATION_PLAN.md`）。

---

## 1) 项目结构审阅与当前链路图

## 1.1 关键目录现状

- `video/`
  - `get_video_ls.py`：B站 UP 主视频抓取主脚本（Selenium + Edge）
  - `normalize_publish_date.py`：发布时间标准化
  - `config.yaml`：抓取配置（authors、headless、输出等）
  - `video_ls.csv`：抓取结果
- `health/`
  - `scripts/update_from_onedrive.py`：OneDrive 拉取 + 解析 + 质量报告编排
  - `scripts/parse_export.py`：解析 `导出.zip`，落地 `health/data/*.csv`
  - `scripts/quality_report.py`：质量报告 `health/_data_quality.md`
  - `scripts/summarize_last7.py`：近7天摘要
  - `scripts/watch_onedrive.ps1`：PowerShell 监听自动触发
  - `data/*.csv`：指标日级聚合结果
- `docs/`
  - `APPLE_HEALTH_PIPELINE.md`
  - `WZRY_DATA_COLLECTION.md`

## 1.2 当前链路图

### A. 视频链路

```text
config/bilibili_authors.json
        |
        v
video/get_video_ls.py (Selenium 抓取)
        |
        +--> video/video_ls.csv
        +--> web/video_ls.csv
        |
        v
前端读取 CSV 展示
```

### B. 健康链路（现有）

```text
iPad/iPhone 健康App 导出 zip
        |
        v
OneDrive\DATA\导出*.zip
        |
        v
health/scripts/update_from_onedrive.py
  ├─ 选最新 zip
  ├─ 等待文件稳定
  ├─ 拷贝到 health/导出.zip
  ├─ 调 parse_export.py
  ├─ 调 summarize_last7.py
  └─ 调 quality_report.py
        |
        v
health/data/*.csv + _last7_summary.md + _data_quality.md
```

---

## 2) video/get_video_ls.py rows=0 原因分析与修复

## 2.1 可复现现象

在本地 headless 采集单作者时，出现过：
- `rows 0`
- 页面标题：`出错啦! - bilibili.com`
- URL 仍为 `/upload/video`

也出现过正常页面但列表异步加载慢，原逻辑直接按固定深层 CSS 定位，首条失败即 `break`，导致整作者 0 条。

## 2.2 具体根因归类

1. **选择器脆弱**（深层 `nth-child` + 长路径）
   - 页面结构轻微变化即失效。
2. **页面状态波动**（出错页/风控页/临时异常）
   - 标题可能为“出错啦”。
3. **异步渲染时序问题**
   - 原逻辑无显式等待卡片加载，只靠 sleep。
4. **登录态影响（潜在）**
   - 页面源码出现“登录/创作中心”相关片段，说明状态敏感；虽然本次非强依赖登录，但需在失败日志里明确分类。

## 2.3 最小改动 patch（已实施）

文件：`video/get_video_ls.py`

改动原则：
- 保留原抓取逻辑路径（第一优先）；
- 仅在失败时进入兜底；
- 增加可诊断日志，不改变现有输出协议。

已增加：
1. **多选择器兜底抓取**
   - 卡片容器：`.video-list .bili-video-card` / `div.bili-video-card`
   - 标题/日期/链接均多 selector 兜底。
2. **失败日志**
   - 输出 `video/debug/video_collect_failures.jsonl`
   - 字段：`ts/author_id/author_name/url/title/reason`
3. **失败原因分类**
   - 登录跳转 / 出错页 / 验证码 / 反爬拦截 / 跳转异常 / 选择器失效。
4. **单作者 smoke test 参数**
   - `--smoke-author-id`
   - `--smoke-limit`

## 2.4 本地验证（非 mock）

执行：

```bash
./.venv/bin/python video/get_video_ls.py --smoke-author-id 520819684 --smoke-limit 1
```

结果：
- 进度条完成 1/1
- 输出：`rows=1`

说明：修复后在单作者场景可稳定抓到至少 1 条。

---

## 3) Health 链路鲁棒化设计

已产出可执行实施计划：
- `docs/HEALTH_ONEDRIVE_IMPLEMENTATION_PLAN.md`

覆盖内容：
- iPad 快捷指令定时导出 -> OneDrive -> Mac 自动入库校验全流程
- 文件格式与目录约定
- 幂等策略
- 质量闸门
- 失败告警
- 分步骤命令与风险清单

---

## 4) 变更清单（本次）

- 代码：
  - `video/get_video_ls.py`（已改，最小、可回滚）
- 文档：
  - `docs/LONG_TASK_RESEARCH_AND_FIX_2026-02-09.md`（本文件）
  - `docs/HEALTH_ONEDRIVE_IMPLEMENTATION_PLAN.md`

---

## 5) 验证命令

```bash
# 1) 视频单作者冒烟
./.venv/bin/python video/get_video_ls.py --smoke-author-id 520819684 --smoke-limit 1

# 2) 健康链路（按需）
python3 health/scripts/update_from_onedrive.py --no-wait
python3 health/scripts/quality_report.py --days 14
```

---

## 6) 风险与后续建议

- B站页面结构仍可能继续演进，建议每次失败都保留 `video_collect_failures.jsonl` 并按周复盘失败原因分布。
- 若 `出错啦` 高频出现，建议在后续迭代加入：
  - 重试（指数退避）
  - headless/headful 自适应
  - cookie 复用（如合规允许）
- health 侧建议优先落地“锁文件 + run manifest + 告警通道”，避免静默失败。
