## Key working notes

- 默认本地预览端口：8000，启动命令 `python -m http.server 8000 --bind 127.0.0.1`；改动后需重启并自测。
- 提交流程：本地验证 -> 推送 `main` -> 通知验收。
- 健康数据：不提交原始导出，仅提交聚合 CSV/PNG；相关聚合脚本与数据在 `health/`。
- 网页：根目录 `index.html`，GitHub Pages 部署；娱乐数据源 `video/video_ls.csv`，健康静态图与指标表使用 `health/` 下聚合文件。
- 端口规则：仅使用 8000 进行本地服务。
