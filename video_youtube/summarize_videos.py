"""对 youtube_ls.csv 中的视频调用 summarize CLI 生成摘要。

用法：
    python summarize_videos.py                     # 提取字幕并用 LLM 总结
    python summarize_videos.py --extract-only      # 仅提取字幕原文（不需要 API key）
    python summarize_videos.py --limit 3           # 最多处理 3 条
    python summarize_videos.py --force             # 强制重新处理（忽略缓存）
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"
CSV_PATH = BASE_DIR / "youtube_ls.csv"
OUTPUT_DIR = BASE_DIR / "output"
SUMMARIES_DIR = OUTPUT_DIR / "summaries"
STATE_PATH = OUTPUT_DIR / "state.json"
DIGEST_PATH = OUTPUT_DIR / "daily_digest.md"


# ─── Config ────────────────────────────────────────────────────

def load_config() -> Dict:
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(raw)
    return json.loads(raw)


# ─── State (incremental processing) ───────────────────────────

def load_state() -> Dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"summarized": {}}


def save_state(state: Dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ─── Summarize ─────────────────────────────────────────────────

def call_summarize(
    url: str,
    model: str = "google/gemini-3-flash-preview",
    length: str = "medium",
    youtube_mode: str = "auto",
    extract_only: bool = False,
) -> Optional[str]:
    """Call the summarize CLI and return the summary/transcript text."""
    cmd = ["summarize", url, "--youtube", youtube_mode]

    if extract_only:
        cmd.append("--extract-only")
    else:
        cmd.extend(["--model", model, "--length", length])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            stderr = result.stderr[:300]
            # If summarize fails due to missing API key, fall back to extract-only
            if not extract_only and "API_KEY" in stderr:
                print(f"    ⚡ LLM API key not found, falling back to transcript extraction...")
                return call_summarize(url, youtube_mode=youtube_mode, extract_only=True)
            print(f"    ⚠ summarize failed (exit {result.returncode}): {stderr[:200]}")
            return None
        output = result.stdout.strip()
        # Remove the "Transcript:" prefix if present (extract-only mode)
        if output.startswith("Transcript:\n"):
            output = output[len("Transcript:\n"):]
        return output
    except subprocess.TimeoutExpired:
        print(f"    ⚠ summarize timed out for {url}")
        return None
    except FileNotFoundError:
        print("    ✗ 'summarize' CLI not found. Install with: brew install steipete/tap/summarize")
        sys.exit(1)


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    for ch in r'/\:*?"<>|':
        name = name.replace(ch, "_")
    return name.strip()[:80]


def write_summary_file(
    channel: str,
    video_id: str,
    title: str,
    url: str,
    publish_date: str,
    summary: str,
    is_transcript: bool = False,
) -> Path:
    """Write a summary markdown file and return its path."""
    channel_dir = SUMMARIES_DIR / sanitize_filename(channel)
    channel_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{video_id}.md"
    filepath = channel_dir / filename

    section_title = "字幕原文" if is_transcript else "总结"
    content = f"""# {title}

- **频道**: {channel}
- **发布日期**: {publish_date}
- **链接**: {url}

---

## {section_title}

{summary}
"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


def write_daily_digest(summaries: List[Dict]) -> None:
    """Write a combined daily digest markdown."""
    DIGEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"# YouTube 视频日报 — {today}\n"]

    for s in summaries:
        lines.append(f"## {s['title']}\n")
        lines.append(f"- **频道**: {s['channel']}")
        lines.append(f"- **分类**: {s['category']}")
        lines.append(f"- **发布日期**: {s['publish_date']}")
        lines.append(f"- **链接**: {s['url']}\n")
        section = "字幕原文" if s.get("is_transcript") else "摘要"
        lines.append(f"### {section}\n")
        lines.append(f"{s['summary']}\n")
        lines.append("---\n")

    DIGEST_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ Daily digest → {DIGEST_PATH}")


# ─── CLI ───────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="对 YouTube 视频进行总结")
    parser.add_argument("--limit", type=int, default=None, help="最多处理多少条视频")
    parser.add_argument("--force", action="store_true", help="忽略缓存，强制重新处理")
    parser.add_argument("--extract-only", action="store_true",
                        help="仅提取字幕原文（不需要 LLM API key）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    summarize_cfg = config.get("summarize", {})

    model = summarize_cfg.get("model", "google/gemini-3-flash-preview")
    length = summarize_cfg.get("length", "medium")
    youtube_mode = summarize_cfg.get("youtube_mode", "auto")
    extract_only = args.extract_only

    if not CSV_PATH.exists():
        print(f"✗ CSV not found: {CSV_PATH}")
        print("  Run get_youtube_ls.py first.")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} videos from {CSV_PATH}")
    if extract_only:
        print("Mode: extract-only (transcript)")

    state = load_state()
    summarized_ids = state.get("summarized", {})

    digest_entries: List[Dict] = []
    processed = 0
    succeeded = 0

    for _, row in df.iterrows():
        video_id = str(row.get("video_id", "")).strip()
        if not video_id:
            continue

        # Skip already summarized (unless --force)
        if not args.force and video_id in summarized_ids:
            continue

        # Limit check
        if args.limit is not None and processed >= args.limit:
            break

        title = str(row.get("title", "")).strip()
        url = str(row.get("url", "")).strip()
        channel = str(row.get("channel", "")).strip()
        category = str(row.get("category", "")).strip()
        publish_date = str(row.get("publish_date", "")).strip()

        action = "Extracting transcript" if extract_only else "Summarizing"
        print(f"  [{processed + 1}] {action}: {title[:60]}...")
        summary = call_summarize(
            url, model=model, length=length,
            youtube_mode=youtube_mode, extract_only=extract_only,
        )

        if summary:
            filepath = write_summary_file(
                channel, video_id, title, url, publish_date, summary,
                is_transcript=extract_only,
            )
            print(f"    ✓ → {filepath}")

            summarized_ids[video_id] = {
                "title": title,
                "channel": channel,
                "mode": "transcript" if extract_only else "summary",
                "summarized_at": datetime.now().isoformat(),
            }
            state["summarized"] = summarized_ids
            save_state(state)

            digest_entries.append({
                "title": title,
                "channel": channel,
                "category": category,
                "publish_date": publish_date,
                "url": url,
                "summary": summary,
                "is_transcript": extract_only,
            })
            succeeded += 1
        else:
            print(f"    ✗ Skipped (no output returned)")

        processed += 1

    if digest_entries:
        write_daily_digest(digest_entries)

    print(f"\nDone. Processed {processed}, succeeded {succeeded}. Total in state: {len(summarized_ids)}")


if __name__ == "__main__":
    main()
