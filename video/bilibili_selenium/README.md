# B站 Selenium 抓取模块（独立）

本目录是独立实现，不依赖仓库原有 `video/get_video_ls.py` 逻辑。

## 目录
- `video/bilibili_selenium/main.py`：入口脚本
- `video/bilibili_selenium/crawler.py`：抓取实现
- `video/bilibili_selenium/requirements.txt`：最小依赖
- `video/bilibili_selenium/cookie.local.example.json`：cookie 示例
- 输出目录：`video/output/`

## 依赖
1. Python 3.9+
2. Google Chrome（或 Chromium）
3. 与 Chrome 匹配版本的 ChromeDriver（Selenium 4.6+ 常可自动管理驱动，但受网络/环境影响）
4. Python 包：

```bash
pip install -r video/bilibili_selenium/requirements.txt
```

## Cookie 支持（提升稳定性）
优先级：环境变量 `BILI_COOKIE` > 本地文件 `--cookie-file`

1. 环境变量方式：

```bash
export BILI_COOKIE='SESSDATA=xxx; bili_jct=xxx; DedeUserID=xxx'
```

2. 本地文件方式：
复制 `cookie.local.example.json` 为 `cookie.local.json`，填写 cookie：

```json
{
  "cookie": "SESSDATA=xxx; bili_jct=xxx; DedeUserID=xxx"
}
```

## 运行方式
抓取一个或多个 up 主（`mid` 可逗号分隔）：

```bash
python video/bilibili_selenium/main.py --mids 354638894 --max-pages 2
```

常用参数：
- `--mids`：必填，up 主 mid，支持逗号分隔
- `--max-pages`：每个 up 抓取页数，默认 `2`
- `--timeout`：页面超时秒数，默认 `20`
- `--sleep`：每页额外等待秒数，默认 `1.3`
- `--cookie-file`：cookie 文件路径，默认 `video/bilibili_selenium/cookie.local.json`
- `--output-dir`：输出目录，默认 `video/output`
- `--headed`：开启有头浏览器（默认无头）
- `--check-env`：仅检查参数/cookie/输出目录，不实际抓取

## 输出
CSV 写入 `video/output/`，字段：
- `up_mid`
- `up_name`
- `page`
- `title`
- `video_url`
- `publish_time`
- `play_count`
- `crawl_time`

## 常见失败处理
1. 页面空白或无数据
- 先带 cookie 运行
- 改用 `--headed` 观察是否遇到风控页面
- 增大 `--sleep`（如 `2.5`）和 `--timeout`（如 `30`）

2. 驱动错误（`chromedriver` 相关）
- 检查 Chrome 与 ChromeDriver 版本是否匹配
- 若 Selenium 自动下载受限，手动安装并加入 `PATH`

3. 被登录页/验证页拦截
- 更新 cookie（至少包含 `SESSDATA`）
- 切换网络环境后重试

## 最小验证命令
不访问 B 站的基础验证：

```bash
python video/bilibili_selenium/main.py --mids 354638894 --check-env
```

实际抓取验证（依赖本机 Chrome、网络、cookie 状态）：

```bash
python video/bilibili_selenium/main.py --mids 354638894 --max-pages 1
```
