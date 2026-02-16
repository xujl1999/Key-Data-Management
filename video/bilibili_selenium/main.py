from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List

from crawler import CrawlConfig, crawl_up_videos, read_cookie_header, write_csv


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_COOKIE_FILE = BASE_DIR / "cookie.local.json"
DEFAULT_OUTPUT_DIR = BASE_DIR.parent / "output"


def _parse_mids(raw: str) -> List[str]:
    mids = [seg.strip() for seg in raw.split(",") if seg.strip()]
    if not mids:
        raise ValueError("请通过 --mids 提供至少一个 up 主 mid")
    return mids


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="独立 B 站 up 主视频抓取模块（Selenium + Chrome）",
    )
    parser.add_argument("--mids", required=True, help="up 主 mid，支持逗号分隔，例如 354638894,546195")
    parser.add_argument("--max-pages", type=int, default=2, help="每个 up 主抓取页数，默认 2")
    parser.add_argument("--timeout", type=int, default=20, help="页面等待超时秒数，默认 20")
    parser.add_argument("--sleep", type=float, default=1.3, help="页面加载后的额外等待秒数，默认 1.3")
    parser.add_argument("--cookie-file", default=str(DEFAULT_COOKIE_FILE), help="cookie 文件路径，默认 video/bilibili_selenium/cookie.local.json")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="CSV 输出目录，默认 video/output")
    parser.add_argument("--headed", action="store_true", help="使用有头模式运行浏览器（默认无头）")
    parser.add_argument("--check-env", action="store_true", help="仅做环境检查（参数、cookie读取、输出目录）")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    mids = _parse_mids(args.mids)
    if args.max_pages < 1:
        parser.error("--max-pages 必须 >= 1")
    cookie_file = Path(args.cookie_file)
    output_dir = Path(args.output_dir)
    cookie_header = read_cookie_header(cookie_file)

    if args.check_env:
        output_dir.mkdir(parents=True, exist_ok=True)
        source = "env:BILI_COOKIE" if cookie_header and "BILI_COOKIE" in os.environ else f"file:{cookie_file}"
        print(f"[OK] mids={mids}")
        print(f"[OK] output_dir={output_dir}")
        print(f"[OK] cookie_source={source if cookie_header else 'none'}")
        return 0

    config = CrawlConfig(
        mids=mids,
        max_pages=args.max_pages,
        headless=not args.headed,
        timeout_sec=args.timeout,
        sleep_sec=args.sleep,
        output_dir=output_dir,
        cookie_header=cookie_header,
    )

    rows = crawl_up_videos(config)
    csv_path = write_csv(rows, output_dir=config.output_dir)

    print(f"[DONE] rows={len(rows)}")
    print(f"[DONE] csv={csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
