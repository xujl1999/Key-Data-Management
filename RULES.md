# 项目操作规程（请务必遵守）

> 目标：每次更新数据/页面前，先在本地规范化数据并自查，再提交推送。避免出现未排序/未统一日期格式的文件。

## 操作步骤
1) 环境准备  
   - 确保已激活 Python 环境（包含 `selenium`、`pandas`、`tqdm` 等依赖）。

2) 抓取数据  
   - 在仓库根目录执行：`python video/get_video_ls.py`  
   - 生成/更新 `video/video_ls.csv`。

3) 规范化并排序 `publish_date`  
   - 在仓库根目录执行：`python video/normalize_publish_date.py`  
   - 作用：将 `publish_date` 统一为 `yyyy-mm-dd`，并按最新时间降序排序写回同一个 CSV。

4) 自查验证  
   - 快速查看前几行、日期格式：  
     `python - <<'PY'\nimport pandas as pd\nimport itertools as it\n df=pd.read_csv('video/video_ls.csv'); print(df.head()); print(list(it.islice(df['publish_date'].unique(),0,10)))\nPY`  
   - 确认日期均为 `yyyy-mm-dd`，排序为最新在前。

5) 提交与推送（默认分支 main）  
   - `git add video/video_ls.csv`（以及其他改动）  
   - `git commit -m "<描述本次更新>"`  
   - `git push origin main`

6) 前端验证（如需本地预览）  
   - 启动本地服务：`python -m http.server 4173`  
   - 浏览器访问 `http://127.0.0.1:4173/index.html`，确认展示正常。

## 原则
- 不得跳过规范化步骤；确保上传前日期格式已统一且排序正确。
- 提交信息尽量清晰，便于追溯（如 `data: normalize publish dates`）。
- 本项目仅供学习研究，严禁用于商业或违规用途。
- GitHub Pages 必须与本地页面一致：`index.html` 新增依赖（图片/CSV/JS/CSS/`health/charts` 等）一律加入 Git 并推送同步。
- 若新增依赖或删除依赖，请确认 `video_update.bat` 的提交流程能同步（建议保持 `git add -A`/`git add .` 覆盖新增与删除）。

## Local workflow agreements (appendix)
- 本地预览默认使用 `python -m http.server 8000 --bind 127.0.0.1`，每次改完代码启动/重启以便验证。
- 修改后先本地验证，再推送到 `main`，完成后通知验收。
- Apple Health 原始导出（导出.zip）不上传，仅提交聚合 CSV/PNG。