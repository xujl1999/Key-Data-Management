# mini-bilibili

一个极简的 B 站视频清单工具：通过 `get_video_ls.py` 抓取配置作者的最新作品，生成 `video_ls.csv`；前端页面 `front/index.html` 会按视频类型与作者展示，并提供筛选控件。

## 目录结构

```
.
├── bili_cookies.json        # Selenium 登录用的 Cookie（需自行维护）
├── bilibili_authors.json    # 抓取作者配置，含分类、作者 ID、作者名
├── get_video_ls.py          # 爬虫脚本，输出 video_ls.csv / out_video_ls.csv
├── video_ls.csv             # 最新抓取结果，前端直接读取
└── front/
    └── index.html           # CSV 预览页面，内置筛选与跳转
```

当前结构较为紧凑，核心流程清晰：根目录负责数据抓取与产物，`front/` 只承担展示。如果后续增加更多页面或脚本，建议再拆分 `scripts/`、`data/` 等目录，以避免根目录文件过多。

## 依赖与准备

- Python 3.9+
- Microsoft Edge 浏览器与对应 WebDriver
- Python 库：`selenium`, `pandas`, `tqdm`

安装依赖：

```bash
pip install selenium pandas tqdm
```

准备文件：

1. `bili_cookies.json`：导出当前登录 B 站账号的 Cookies，供 Selenium 注入。
2. `bilibili_authors.json`：维护需要抓取的作者列表，字段包含 `category`、`author_id`、`author_name`。

## 抓取视频数据

```bash
python get_video_ls.py
```

脚本流程：

1. 打开 B 站并写入配置的 Cookies，保持登录态。
2. 遍历 `bilibili_authors.json` 中的作者，进入其空间抓取最新 10 条视频。
3. 写出 `video_ls.csv`（全量数据）。
4. 额外筛选「超优质 / 历史区 / 创意区」且 `rank <= 1` 的数据到 `out_video_ls.csv`（可选）。

若页面结构调整导致 CSS 选择器失效，可在脚本中更新对应的 `driver.find_element` 选择器。

## 预览前端页面

利用 Python 自带服务器即可本地查看：

```bash
cd /Users/xujl/Documents/个人文件/网站爬虫
python3 -m http.server 4173
```

然后打开 `http://127.0.0.1:4173/front/index.html`。

前端特性：

- 默认展示「超优质」分类，每位作者仅显示 1 条最新视频，可在页面右上角调整。
- Chip 样式的分类筛选、数量输入框、标题点击跳转。

## 项目结构评估

- **清晰度**：采集脚本与前端分离，CSV 为唯一桥梁，逻辑简单。
- **可维护性**：当文件数量增加时，可考虑：
  - 新增 `data/`（存放 CSV、JSON）、`scripts/`（爬虫、辅助脚本）等文件夹；
  - 为 Python 依赖提供 `requirements.txt`，便于一键安装。
- **部署**：目前通过静态服务器即可；若需要托管或自动更新数据，可扩展为定时任务或后端服务。

保持以上约定，项目结构在当前规模下已足够清楚，后续按需扩展即可。
