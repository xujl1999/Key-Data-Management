#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update health/dashboard_data.json.

Targets:
- Weather: Shenzhen Nanshan + Chengdu via Caiyun (fallback to Open-Meteo if Caiyun fails)
- Markets: Tencent + indices via Yahoo Finance chart endpoint
- AI news: 3-5 items via RSS
- ClawHub skills: 3-5 items via simple HTML scrape (best-effort)
- Keep existing todos unchanged
- Update updated_at timestamp

No third-party deps.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = r"D:\\dream_life\\data-management"
DASHBOARD_JSON = ROOT + r"\\health\\dashboard_data.json"


def _now_iso_shanghai() -> str:
    # Avoid tz database dependency; Shanghai is fixed +08:00.
    tz = _dt.timezone(_dt.timedelta(hours=8))
    return _dt.datetime.now(tz=tz).replace(microsecond=0).isoformat()


def _http_get(url: str, headers: dict | None = None, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _safe_json_loads(b: bytes):
    return json.loads(b.decode("utf-8", errors="replace"))


_SKYCON_ZH = {
    "CLEAR_DAY": "晴",
    "CLEAR_NIGHT": "晴",
    "PARTLY_CLOUDY_DAY": "多云",
    "PARTLY_CLOUDY_NIGHT": "多云",
    "CLOUDY": "阴",
    "LIGHT_HAZE": "轻度雾霾",
    "MODERATE_HAZE": "中度雾霾",
    "HEAVY_HAZE": "重度雾霾",
    "LIGHT_RAIN": "小雨",
    "MODERATE_RAIN": "中雨",
    "HEAVY_RAIN": "大雨",
    "STORM_RAIN": "暴雨",
    "FOG": "雾",
    "LIGHT_SNOW": "小雪",
    "MODERATE_SNOW": "中雪",
    "HEAVY_SNOW": "大雪",
    "STORM_SNOW": "暴雪",
    "DUST": "浮尘",
    "SAND": "沙尘",
    "WIND": "大风",
}


def _caiyun_weather(lon: float, lat: float, token: str) -> dict:
    url = f"https://api.caiyunapp.com/v2.6/{token}/{lon},{lat}/weather?alert=true"
    data = _safe_json_loads(_http_get(url, headers={"User-Agent": "Mozilla/5.0"}))

    rt = data.get("result", {}).get("realtime", {})
    daily = data.get("result", {}).get("daily", {})

    temp_current = rt.get("temperature")
    humidity = rt.get("humidity")
    skycon = rt.get("skycon")
    wind = rt.get("wind", {})
    wind_kmph = None
    if isinstance(wind, dict) and wind.get("speed") is not None:
        # Caiyun wind speed is m/s
        wind_kmph = round(float(wind["speed"]) * 3.6)

    # Daily min/max (take first day)
    tmin = tmax = None
    try:
        tmin = round(float(daily["temperature"][0]["min"]))
        tmax = round(float(daily["temperature"][0]["max"]))
    except Exception:
        pass

    aqi = None
    aqi_level = None
    try:
        aqi = rt.get("air_quality", {}).get("aqi", {}).get("chn")
        if aqi is not None:
            aqi = int(round(float(aqi)))
        aqi_level = rt.get("air_quality", {}).get("description", {}).get("chn")
    except Exception:
        pass

    desc = _SKYCON_ZH.get(skycon, skycon or "未知")

    rain_forecast = None
    # Best-effort: find peak precipitation probability in next 24h
    try:
        hourly = data.get("result", {}).get("hourly", {})
        precip = hourly.get("precipitation", [])
        probs = hourly.get("precipitation_probability", [])
        # Older payloads: only precipitation with value.
        peak_p = 0.0
        peak_i = None
        if probs:
            for i, row in enumerate(probs[:24]):
                v = float(row.get("value", 0) or 0)
                if v > peak_p:
                    peak_p = v
                    peak_i = i
            if peak_i is not None and peak_p > 0:
                start = (_dt.datetime.now(_dt.timezone(_dt.timedelta(hours=8))) + _dt.timedelta(hours=peak_i)).strftime("%H:00")
                end = (_dt.datetime.now(_dt.timezone(_dt.timedelta(hours=8))) + _dt.timedelta(hours=min(peak_i + 3, 24))).strftime("%H:00")
                rain_forecast = f"{start}~{end} 降雨概率 {int(round(peak_p * 100))}%（峰值）"
        elif precip:
            for i, row in enumerate(precip[:24]):
                v = float(row.get("value", 0) or 0)
                if v > peak_p:
                    peak_p = v
                    peak_i = i
            if peak_i is not None and peak_p > 0.01:
                start = (_dt.datetime.now(_dt.timezone(_dt.timedelta(hours=8))) + _dt.timedelta(hours=peak_i)).strftime("%H:00")
                end = (_dt.datetime.now(_dt.timezone(_dt.timedelta(hours=8))) + _dt.timedelta(hours=min(peak_i + 3, 24))).strftime("%H:00")
                rain_forecast = f"{start}~{end} 可能有降雨（强度峰值 {peak_p:.2f}mm/h）"
    except Exception:
        pass

    if not rain_forecast:
        rain_forecast = "未来24小时无明显降雨"  # generic

    return {
        "temp_current": int(round(float(temp_current))) if temp_current is not None else None,
        "temp_min": int(tmin) if tmin is not None else None,
        "temp_max": int(tmax) if tmax is not None else None,
        "humidity": int(round(float(humidity) * 100)) if humidity is not None else None,
        "description": desc,
        "wind_kmph": wind_kmph,
        "aqi": aqi,
        "aqi_level": aqi_level,
        "rain_forecast": rain_forecast,
        "source": "caiyun",
    }


def _open_meteo_weather(lat: float, lon: float) -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min",
                "hourly": "precipitation_probability",
                "forecast_days": 2,
                "timezone": "Asia/Shanghai",
            }
        )
    )
    data = _safe_json_loads(_http_get(url, headers={"User-Agent": "Mozilla/5.0"}))

    wc = (data.get("current", {}) or {}).get("weather_code")
    # Minimal mapping
    wc_map = {
        0: "晴",
        1: "多云",
        2: "多云",
        3: "阴",
        45: "雾",
        48: "雾",
        51: "小雨",
        53: "小雨",
        55: "中雨",
        61: "小雨",
        63: "中雨",
        65: "大雨",
        80: "阵雨",
        81: "阵雨",
        82: "暴雨",
        95: "雷阵雨",
    }

    # Rain forecast: peak in next 24h
    rain_forecast = "未来24小时无明显降雨"
    try:
        probs = data.get("hourly", {}).get("precipitation_probability", [])
        times = data.get("hourly", {}).get("time", [])
        if probs and times:
            peak = max(probs[:24])
            if peak and peak >= 20:
                peak_i = probs[:24].index(peak)
                start = times[peak_i].split("T")[1]
                end = times[min(peak_i + 3, len(times) - 1)].split("T")[1]
                rain_forecast = f"{start}~{end} 降雨概率 {int(peak)}%（峰值）"
    except Exception:
        pass

    return {
        "temp_current": int(round(float((data.get("current", {}) or {}).get("temperature_2m"))))
        if (data.get("current", {}) or {}).get("temperature_2m") is not None
        else None,
        "temp_min": int(round(float((data.get("daily", {}) or {}).get("temperature_2m_min", [None])[0])))
        if (data.get("daily", {}) or {}).get("temperature_2m_min")
        else None,
        "temp_max": int(round(float((data.get("daily", {}) or {}).get("temperature_2m_max", [None])[0])))
        if (data.get("daily", {}) or {}).get("temperature_2m_max")
        else None,
        "humidity": int(round(float((data.get("current", {}) or {}).get("relative_humidity_2m"))))
        if (data.get("current", {}) or {}).get("relative_humidity_2m") is not None
        else None,
        "description": wc_map.get(wc, "未知"),
        "wind_kmph": int(round(float((data.get("current", {}) or {}).get("wind_speed_10m"))))
        if (data.get("current", {}) or {}).get("wind_speed_10m") is not None
        else None,
        "aqi": None,
        "aqi_level": None,
        "rain_forecast": rain_forecast,
        "source": "open-meteo(fallback)",
    }


def _fetch_weather(prev_weather: dict | None = None) -> dict:
    # Nanshan, Shenzhen / Chengdu city center
    locs = {
        "shenzhen": {"name": "深圳南山", "lon": 113.930, "lat": 22.533},
        "chengdu": {"name": "成都", "lon": 104.066, "lat": 30.572},
    }

    out = {}
    for key, it in locs.items():
        lon, lat = it["lon"], it["lat"]
        try:
            out[key] = _caiyun_weather(lon=lon, lat=lat, token=_TOKEN)
        except Exception as e:
            # If Caiyun is rate-limiting (429) or unavailable, fall back, but make it explicit.
            try:
                fb = _open_meteo_weather(lat=lat, lon=lon)
                fb["source"] = "caiyun(failed)->open-meteo"
                out[key] = fb
            except Exception:
                # Final fallback: keep previous value if we have one.
                if prev_weather and key in prev_weather:
                    out[key] = prev_weather[key]
                else:
                    out[key] = {"source": f"caiyun(failed:{type(e).__name__})"}

    return out


# NOTE: keep a module-level token with sane default.
_TOKEN = "TAkhjf8d1nlSlspN"


def _yahoo_quote(symbol: str) -> tuple[float | None, float | None]:
    """Return (price, change_percent).

    Note: some UI symbols in our dashboard_data.json aren't valid Yahoo tickers.
    We remap a few common ones.
    """
    symbol_map = {
        "^NDQ": "^NDX",   # Nasdaq 100
        "^SPX": "^GSPC",  # S&P 500
    }
    q = symbol_map.get(symbol, symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(q)}?interval=1d&range=5d"
    data = _safe_json_loads(_http_get(url, headers={"User-Agent": "Mozilla/5.0"}))
    try:
        res = data["chart"]["result"][0]
        meta = res.get("meta", {})
        price = meta.get("regularMarketPrice")
        chg_pct = meta.get("regularMarketChangePercent")

        # If change percent missing (common for some markets), compute from last 2 closes.
        if chg_pct is None:
            closes = (
                (((res.get("indicators") or {}).get("quote") or [{}])[0]).get("close")
                or []
            )
            closes = [c for c in closes if c is not None]
            if len(closes) >= 2 and closes[-2] != 0:
                chg_pct = (float(closes[-1]) / float(closes[-2]) - 1.0) * 100.0
            elif len(closes) >= 1:
                chg_pct = None

        return (float(price) if price is not None else None, float(chg_pct) if chg_pct is not None else None)
    except Exception:
        return (None, None)


def _fetch_markets() -> list[dict]:
    items = [
        {"name": "腾讯", "symbol": "0700.HK"},
        {"name": "恒生指数", "symbol": "^HSI"},
        {"name": "纳指", "symbol": "^NDQ"},
        {"name": "标普500", "symbol": "^SPX"},
        {"name": "上证综指", "symbol": "000001.SS"},
        {"name": "深证成指", "symbol": "399001.SZ"},
    ]
    out = []
    for it in items:
        p, c = _yahoo_quote(it["symbol"])
        out.append({"name": it["name"], "symbol": it["symbol"], "price": round(p, 2) if p is not None else None, "change": round(c, 2) if c is not None else None})
    return out


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fetch_ai_news(limit: int = 5) -> list[dict]:
    rss_urls = [
        "https://openai.com/blog/rss.xml",
        "https://www.anthropic.com/news/rss.xml",
        "https://blog.google/technology/ai/rss/",
        "https://www.theverge.com/rss/ai/index.xml",
    ]

    news: list[dict] = []
    seen = set()

    for url in rss_urls:
        try:
            raw = _http_get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            root = ET.fromstring(raw)

            # Handle RSS and Atom-ish feeds.
            items = root.findall(".//item")
            if not items:
                # Atom
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            for it in items[:10]:
                title = it.findtext("title") or it.findtext("{http://www.w3.org/2005/Atom}title")
                link = it.findtext("link")
                if link is None:
                    link_el = it.find("{http://www.w3.org/2005/Atom}link")
                    if link_el is not None:
                        link = link_el.attrib.get("href")
                desc = it.findtext("description") or it.findtext("{http://www.w3.org/2005/Atom}summary") or ""
                title = _strip_html(title)
                link = (link or "").strip()

                if not title or not link:
                    continue
                key = (title + "|" + link)
                if key in seen:
                    continue
                seen.add(key)

                summary = _strip_html(desc)
                if len(summary) > 120:
                    summary = summary[:120].rstrip() + "…"

                news.append({"title": title, "summary": summary, "url": link})
                if len(news) >= limit:
                    return news
        except Exception:
            continue

    return news[:limit]


def _fetch_clawhub_skills(limit: int = 5) -> list[dict]:
    # Best-effort scrape; ClawHub may be protected/changed.
    candidate_urls = [
        "https://www.clawhub.com/",
        "https://www.clawhub.com/explore",
        "https://www.clawhub.com/skills",
    ]

    for url in candidate_urls:
        try:
            html = _http_get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20).decode("utf-8", errors="replace")
            # heuristic: skill cards link pattern: /<author>/<slug>
            links = re.findall(r"href=\"(/[^\"\s<>]{3,})\"", html)
            out = []
            seen = set()
            for href in links:
                if href.count("/") < 2:
                    continue
                if href.startswith("/pricing") or href.startswith("/login") or href.startswith("/terms"):
                    continue
                full = "https://www.clawhub.com" + href
                if full in seen:
                    continue
                seen.add(full)
                # Try to extract name near the link (very rough)
                name = href.strip("/").split("/")[-1].replace("-", " ")
                name = re.sub(r"\s+", " ", name).strip().title()[:60]
                out.append({"name": name, "desc": "", "url": full})
                if len(out) >= limit:
                    return out
        except Exception:
            continue

    return []


def main() -> int:
    with open(DASHBOARD_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    todos = data.get("todos")

    # Allow CLI override for Caiyun token.
    global _TOKEN
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        _TOKEN = sys.argv[1].strip()

    data["updated_at"] = _now_iso_shanghai()
    data["weather"] = _fetch_weather(prev_weather=data.get("weather"))
    data["markets"] = _fetch_markets()
    data["ai_news"] = _fetch_ai_news(limit=5)

    skills = _fetch_clawhub_skills(limit=5)
    if skills:
        data["clawhub_skills"] = skills

    # Keep todos unchanged
    data["todos"] = todos

    with open(DASHBOARD_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
