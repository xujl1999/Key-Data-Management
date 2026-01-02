## 目的
为 AI 编码代理（Copilot/Agent）提供在本仓库中快速上手的关键上下文：架构要点、常用开发/运行命令、项目约定与可直接引用的示例文件。

## 大体架构（为何及如何分层）
- 前端：单页静态页面，位于 `index.html` + `css/` + `js/`，通过相对路径读取本地 CSV（见 `js/app.js` 中的 `CSV_SOURCES` 与 `HEALTH_SOURCES`）。
- 数据抓取：位于 `video/`（抓取脚本 `video/get_video_ls.py`、配置 `video/bilibili_authors.json`），生成 `video/video_ls.csv`，由前端直接消费。
- 本地辅助 API：`local_api.py`（简单 HTTP server，监听 `POST /author`，将 author id 写入 `video/` 目录）。
- 服务后端（可选）：`food_service/` 是一个基于 FastAPI 的服务（入口 `food_service/app.py`），用于图片识别/营养估算，调用外部 LLM/Vision API（由环境变量 `QWEN_API_KEY` 等配置）。
- 健康数据：静态 CSV 文件放在 `health/data/`，前端通过 `js/app.js` 的多个 `*_SOURCES` 读取并渲染。

## 关键开发/运行流程（具体命令与示例）
- 快速预览前端（静态）：在仓库根目录运行 `python -m http.server 8000`，然后打开 `http://127.0.0.1:8000/index.html`（见 [index.html](index.html#L1-L10) 与 `js/app.js` 数据引用）。
- 抓取视频（Selenium）：参见 [README.md](README.md#L1-L80)；通常运行 `python video/get_video_ls.py` 或使用一键脚本 `video_update.bat`。
- 本地 API：`python local_api.py` 将在 `127.0.0.1:8000` 提供 `POST /author`，用于快速生成 `video/<author_id>.csv` 示例。
- 启动食物识别服务（开发）：使用 `food_service/run_demo.bat` 或在容器/虚拟环境里运行 `uvicorn food_service.app:app --reload`（请确保 `QWEN_API_KEY`、`SHORTCUT_TOKEN` 等环境变量已设置）。日志写入 `food_service/logs/food_log.jsonl`。

## 项目约定与模式（重要且具体）
- 数据优先本地：前端优先读取仓库内的 CSV（`health/data/` 与 `video/video_ls.csv`），并在 `js/app.js` 中保留遠程备用 `GitHub Raw` 源。
- 配置集中在 `config/`：`config/data-sources.json`、`config/health_metrics.json` 与 `config/bilibili_authors.json` 用於覆盖或扩展默认数据源；前端会读取全局 `window.KDM_CONFIG` 做运行时覆盖。
- 后端对外依赖采用环境变量：`food_service/app.py` 明确使用 `QWEN_API_KEY`、`QWEN_API_BASE`、`QWEN_MODEL`、`SHORTCUT_TOKEN`（请不要把密钥硬编码到代码）。
- 错误/日志：`food_service` 将每次请求写入 `logs/food_log.jsonl`（JSONL），便于回放与离线分析。

## 代码风格与常见实现细节（供自动补全和修复参考）
- 前端 CSV 解析用自定义 `parseCSV`（位于 `js/app.js`），修改時请尽量保持与现有键名兼容（例如列头回退逻辑 `fallbackHeader`）。
- 后端返回约定：`food_service` 要求上游模型返回纯 JSON（见 `build_prompt` 里的 schema），处理函数 `extract_json_object` 容错地从任意文本中提取首个 JSON 对象。
- 身份/认证：`food_service` 使用 `X-Token` 校验（见 `analyze` 中 `SHORTCUT_TOKEN` 校验逻辑）；`local_api.py` 为轻量写入接口无 auth。

## 代码修改建议（AI agent 指南）
- 若改动数据路径或新增数据源，务必同时更新 `js/app.js` 中对应 `*_SOURCES` 常量和 `config/data-sources.json`。
- 若更换上游 LLM/Vision 提供商，请定位 `food_service/app.py` 的 `analyze_image`、`extract_content`、`extract_json_object`，并保持 `normalize_response` 的输出 schema 不变以兼容日志与前端。
- 对于前端改动，优先做小范围变更并在本地用 `python -m http.server` 验证静态页面渲染与 CSV 加载。

## 关键文件速查
- 仓库首页说明：[README.md](README.md#L1-L40)
- 前端入口：[index.html](index.html#L1-L20)
- 前端逻辑与数据源：[js/app.js](js/app.js#L1-L40)
- 视频抓取脚本：[video/get_video_ls.py](video/get_video_ls.py#L1-L40)
- 本地写接口：[local_api.py](local_api.py#L1-L60)
- 食物识别服务：[food_service/app.py](food_service/app.py#L1-L40)
- 配置目录：`config/`（包含 `data-sources.json`、`bilibili_authors.json`、`health_metrics.json`）

## 我没在代码里发现（但需要确认）
- CI/CD 流程：仓库中没有明显的 GitHub Actions 配置；如需自动化发布/抓取，应新增工作流。
- 单元/集成测试：仓库没有测试框架或测试目录；若要添加，请先确认运行时依赖（Selenium、浏览器 driver、QWEN key）。

若这些说明中有不准确或遗漏的地方，请指出我应该补充或更正的具体区域（例如哪个脚本的运行命令、哪个环境变量或哪个数据源）。
