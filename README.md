# 项目说明

一个抓取视频列表、并在网页上展示的简单项目，仅供学习交流使用，不得用于商业或违规用途。

## 目录结构
- `video/`：抓取脚本及配置，输出 `video_ls.csv`。
- `index.html`：根目录下的前端页面，从 `video/video_ls.csv` 读取并展示数据。
- `video_update.bat`：一键执行抓取并将整个仓库提交到远端。

## 使用步骤
1) 准备环境  
   - 安装 Edge 浏览器与对应的 Selenium WebDriver（需与浏览器版本匹配）。  
   - 在本机已有的 Python/conda 环境中安装依赖：`selenium`、`pandas`、`tqdm`。  
   - 配置作者列表文件 `video/bilibili_authors.json`（存放作者 id、类别等信息）。

2) 抓取数据  
   - 进入仓库根目录并激活环境：`conda activate base`（或你的 Python 环境）。  
   - 运行脚本：`python video/get_video_ls.py`。  
   - 成功后会生成/更新 `video/video_ls.csv`，并可供前端页面读取。

3) 本地预览页面  
   - 在仓库根目录启动简易服务：`python -m http.server 8000`。  
   - 浏览器打开 `http://127.0.0.1:8000/index.html` 查看列表。

4) 一键流程与提交  
   - 可运行 `video_update.bat`：依次激活环境、抓取数据、在根目录 `git add/commit/push` 到 `main` 分支（默认远端为 `origin`）。

## 免责声明
- 本项目仅供学习研究，切勿用于商业或其他违规场景。  
- 抓取操作应尊重目标站点的服务条款与数据使用规范，避免过度访问。
