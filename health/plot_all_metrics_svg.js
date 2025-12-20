const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const CHARTS_DIR = path.join(ROOT, "charts");
const CONFIG_PATH = path.join(ROOT, "metric_config.json");

const EXTRA_METRICS = [
  { label: "入睡时间", valueKey: "bed_time" },
  { label: "起床时间", valueKey: "wake_time" },
];

const GUIDE_LINES = {
  sleep_hours: [
    { value: 8, label: "目标 8h", color: "#22d3ee" },
    { value: 6, label: "预警 6h", color: "#f97316" },
  ],
  weight_kg: [
    { value: 70, label: "目标 70kg", color: "#22d3ee" },
    { value: 80, label: "预警 80kg", color: "#f97316" },
  ],
};

const TIME_VALUE_KEYS = new Set(["bed_time", "wake_time"]);

const WIDTH = 960;
const HEIGHT = 720;
const MARGIN_LEFT = 70;
const MARGIN_RIGHT = 30;
const MARGIN_TOP = 54;
const MARGIN_BOTTOM = 40;
const PANEL_GAP = 40;
const PANEL_TITLE_HEIGHT = 20;
const X_LABEL_HEIGHT = 24;

const MAIN_COLOR = "#60a5fa";

const escapeXml = (text) =>
  String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

const pad2 = (num) => String(num).padStart(2, "0");

const parseDate = (text) => {
  if (!text) return null;
  const parts = text.trim().split("-");
  if (parts.length !== 3) return null;
  const year = Number(parts[0]);
  const month = Number(parts[1]);
  const day = Number(parts[2]);
  if (!year || !month || !day) return null;
  return new Date(Date.UTC(year, month - 1, day));
};

const formatDate = (date, mode) => {
  if (!date) return "";
  const y = date.getUTCFullYear();
  const m = pad2(date.getUTCMonth() + 1);
  const d = pad2(date.getUTCDate());
  if (mode === "month-day") {
    return `${m}-${d}`;
  }
  return `${y}-${m}`;
};

const parseClockToMinutes = (text) => {
  if (!text) return null;
  const cleaned = text.trim();
  if (!cleaned) return null;
  if (cleaned.includes(":")) {
    const parts = cleaned.split(":");
    const hh = Number(parts[0]);
    const mm = Number(parts[1]);
    if (Number.isNaN(hh) || Number.isNaN(mm)) return null;
    return hh * 60 + mm;
  }
  const num = Number(cleaned);
  return Number.isNaN(num) ? null : num;
};

const formatMinutes = (mins) => {
  if (mins === null || mins === undefined || Number.isNaN(mins)) return "";
  const total = ((Math.round(mins) % 1440) + 1440) % 1440;
  const hh = pad2(Math.floor(total / 60));
  const mm = pad2(total % 60);
  return `${hh}:${mm}`;
};

const formatNumber = (value) => {
  if (value === null || value === undefined || Number.isNaN(value)) return "";
  const abs = Math.abs(value);
  if (abs >= 1000) return String(Math.round(value));
  if (abs >= 100) return value.toFixed(1).replace(/\.0$/, "");
  if (abs >= 10) return value.toFixed(1).replace(/\.0$/, "");
  return value
    .toFixed(2)
    .replace(/\.00$/, "")
    .replace(/(\.\d)0$/, "$1");
};

const parseCsvLine = (line) => {
  const out = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === "\"") {
      if (inQuotes && line[i + 1] === "\"") {
        current += "\"";
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === "," && !inQuotes) {
      out.push(current);
      current = "";
    } else {
      current += ch;
    }
  }
  out.push(current);
  return out;
};

const readCsv = (filePath) => {
  const text = fs.readFileSync(filePath, "utf8").trim();
  if (!text) return { headers: [], rows: [] };
  const lines = text.split(/\r?\n/).filter(Boolean);
  const rows = lines.map(parseCsvLine);
  return {
    headers: rows[0] ? rows[0].map((h) => h.trim()) : [],
    rows: rows.slice(1),
  };
};

const pickColor = () => MAIN_COLOR;

const buildChartMap = () => {
  const map = new Map();
  if (!fs.existsSync(CHARTS_DIR)) return map;
  const files = fs.readdirSync(CHARTS_DIR);
  files.forEach((file) => {
    const ext = path.extname(file).toLowerCase();
    if (ext !== ".svg" && ext !== ".png") return;
    const base = file.slice(0, -ext.length);
    const idx = base.lastIndexOf("__");
    if (idx === -1) return;
    const stem = base.slice(0, idx);
    const valueKey = base.slice(idx + 2);
    const existing = map.get(valueKey);
    if (!existing || (ext === ".svg" && existing.ext !== ".svg")) {
      map.set(valueKey, { stem, ext });
    }
  });
  return map;
};

const computeRollingAvg = (series, window) => {
  const out = [];
  const queue = [];
  let sum = 0;
  series.forEach((point) => {
    queue.push(point.value);
    sum += point.value;
    if (queue.length > window) {
      sum -= queue.shift();
    }
    out.push({ date: point.date, value: sum / queue.length });
  });
  return out;
};

const buildTicks = (min, max, count) => {
  if (!Number.isFinite(min) || !Number.isFinite(max) || count < 2) return [min];
  if (min === max) return [min];
  const step = (max - min) / (count - 1);
  return Array.from({ length: count }, (_, i) => min + step * i);
};

const buildDateTicks = (minDate, maxDate, count) => {
  if (!minDate || !maxDate || count < 2) return [minDate];
  const minTime = minDate.getTime();
  const maxTime = maxDate.getTime();
  if (minTime === maxTime) return [minDate];
  const step = (maxTime - minTime) / (count - 1);
  return Array.from({ length: count }, (_, i) => new Date(minTime + step * i));
};

const renderPanel = ({
  panel,
  series,
  title,
  color,
  showPoints,
  showFill,
  guideLines,
  isTime,
  xTickCount,
  xTickMode,
}) => {
  if (!series.length) return "";

  const plotLeft = MARGIN_LEFT;
  const plotRight = WIDTH - MARGIN_RIGHT;
  const plotTop = panel.top + PANEL_TITLE_HEIGHT;
  const plotBottom = panel.top + panel.height - X_LABEL_HEIGHT;
  const plotWidth = plotRight - plotLeft;
  const plotHeight = plotBottom - plotTop;

  const values = series.map((p) => p.value);
  let minVal = Math.min(...values);
  let maxVal = Math.max(...values);
  (guideLines || []).forEach((line) => {
    if (typeof line.value === "number") {
      minVal = Math.min(minVal, line.value);
      maxVal = Math.max(maxVal, line.value);
    }
  });
  if (minVal === maxVal) {
    minVal -= 1;
    maxVal += 1;
  }
  const pad = isTime ? Math.max((maxVal - minVal) * 0.1, 30) : Math.max((maxVal - minVal) * 0.1, 0.2);
  minVal -= pad;
  maxVal += pad;

  const dateMin = series[0].date;
  const dateMax = series[series.length - 1].date;
  const timeSpan = dateMax.getTime() - dateMin.getTime() || 86400000;
  const xScale = (date) =>
    plotLeft + ((date.getTime() - dateMin.getTime()) / timeSpan) * plotWidth;
  const yScale = (value) =>
    plotBottom - ((value - minVal) / (maxVal - minVal || 1)) * plotHeight;

  const yTicks = buildTicks(minVal, maxVal, 5);
  const xTicks = buildDateTicks(dateMin, dateMax, xTickCount);

  const elems = [];
  elems.push(
    `<text x="${plotLeft}" y="${panel.top + 16}" fill="#e2e8f0" font-size="13" font-weight="600">${escapeXml(
      title
    )}</text>`
  );

  yTicks.forEach((tick) => {
    const y = yScale(tick);
    elems.push(
      `<line x1="${plotLeft}" y1="${y.toFixed(2)}" x2="${plotRight}" y2="${y.toFixed(
        2
      )}" stroke="#94a3b8" stroke-opacity="0.18" stroke-width="1" />`
    );
    const label = isTime ? formatMinutes(tick) : formatNumber(tick);
    elems.push(
      `<text x="${plotLeft - 8}" y="${(y + 4).toFixed(
        2
      )}" fill="#cbd5f5" font-size="10" text-anchor="end">${escapeXml(label)}</text>`
    );
  });

  xTicks.forEach((tick) => {
    const x = xScale(tick);
    elems.push(
      `<line x1="${x.toFixed(2)}" y1="${plotBottom}" x2="${x.toFixed(
        2
      )}" y2="${plotBottom + 4}" stroke="#94a3b8" stroke-opacity="0.5" stroke-width="1" />`
    );
    elems.push(
      `<text x="${x.toFixed(2)}" y="${plotBottom + 18}" fill="#cbd5f5" font-size="10" text-anchor="middle">${escapeXml(
        formatDate(tick, xTickMode)
      )}</text>`
    );
  });

  elems.push(
    `<line x1="${plotLeft}" y1="${plotTop}" x2="${plotLeft}" y2="${plotBottom}" stroke="#94a3b8" stroke-width="1" />`
  );
  elems.push(
    `<line x1="${plotLeft}" y1="${plotBottom}" x2="${plotRight}" y2="${plotBottom}" stroke="#94a3b8" stroke-width="1" />`
  );

  (guideLines || []).forEach((line) => {
    if (typeof line.value !== "number") return;
    const y = yScale(line.value);
    elems.push(
      `<line x1="${plotLeft}" y1="${y.toFixed(2)}" x2="${plotRight}" y2="${y.toFixed(
        2
      )}" stroke="${line.color}" stroke-width="1" stroke-dasharray="4 4" stroke-opacity="0.9" />`
    );
    elems.push(
      `<text x="${plotRight - 4}" y="${(y - 6).toFixed(
        2
      )}" fill="${line.color}" font-size="10" text-anchor="end">${escapeXml(
        line.label
      )}</text>`
    );
  });

  const linePoints = series.map((point) => {
    const x = xScale(point.date);
    const y = yScale(point.value);
    return { x, y, display: point.display };
  });

  const linePath = linePoints
    .map((point, idx) => `${idx === 0 ? "M" : "L"}${point.x.toFixed(2)},${point.y.toFixed(2)}`)
    .join(" ");

  if (showFill && linePoints.length > 1) {
    const first = linePoints[0];
    const last = linePoints[linePoints.length - 1];
    const areaPath = [
      `M${first.x.toFixed(2)},${plotBottom.toFixed(2)}`,
      ...linePoints.map((p) => `L${p.x.toFixed(2)},${p.y.toFixed(2)}`),
      `L${last.x.toFixed(2)},${plotBottom.toFixed(2)}`,
      "Z",
    ].join(" ");
    elems.push(
      `<path d="${areaPath}" fill="${color}" fill-opacity="0.16" stroke="none" />`
    );
  }

  elems.push(
    `<path d="${linePath}" fill="none" stroke="${color}" stroke-width="2.2" stroke-linecap="round" />`
  );

  if (showPoints) {
    linePoints.forEach((point, idx) => {
      const label = point.display || "";
      const offset = idx % 2 === 0 ? -10 : -20;
      let labelY = point.y + offset;
      if (labelY < plotTop + 10) {
        labelY = point.y + 14;
      }
      elems.push(
        `<circle cx="${point.x.toFixed(2)}" cy="${point.y.toFixed(
          2
        )}" r="3" fill="${color}" stroke="#0f172a" stroke-width="1" />`
      );
      elems.push(
        `<text x="${point.x.toFixed(2)}" y="${labelY.toFixed(
          2
        )}" fill="#e2e8f0" font-size="9" text-anchor="middle">${escapeXml(label)}</text>`
      );
    });
  }

  return elems.join("\n");
};

const renderChart = ({ label, valueKey, topSeries, bottomSeries, guideLines, isTime }) => {
  const color = pickColor(valueKey);
  const panelHeight = (HEIGHT - MARGIN_TOP - MARGIN_BOTTOM - PANEL_GAP) / 2;
  const panels = [
    { top: MARGIN_TOP, height: panelHeight },
    { top: MARGIN_TOP + panelHeight + PANEL_GAP, height: panelHeight },
  ];

  const parts = [];
  parts.push(
    `<rect width="${WIDTH}" height="${HEIGHT}" fill="#0f172a" />`
  );
  parts.push(
    `<text x="${WIDTH / 2}" y="28" fill="#e2e8f0" font-size="16" font-weight="700" text-anchor="middle">${escapeXml(
      `${label}趋势图`
    )}</text>`
  );

  parts.push(
    renderPanel({
      panel: panels[0],
      series: topSeries,
      title: "本月分天指标明细",
      color,
      showPoints: true,
      showFill: false,
      guideLines,
      isTime,
      xTickCount: 6,
      xTickMode: "month-day",
    })
  );

  parts.push(
    renderPanel({
      panel: panels[1],
      series: bottomSeries,
      title: "本年核心指标趋势（滑动7日窗口平均）",
      color,
      showPoints: false,
      showFill: true,
      guideLines,
      isTime,
      xTickCount: 6,
      xTickMode: "year-month",
    })
  );

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${WIDTH} ${HEIGHT}" width="${WIDTH}" height="${HEIGHT}">\n${parts.join(
    "\n"
  )}\n</svg>\n`;
};

const buildSeries = ({ headers, rows, valueKey, isTime }) => {
  const headersLower = headers.map((h) => h.toLowerCase());
  const idxDate = headersLower.indexOf("date");
  const idxVal = headersLower.indexOf(valueKey.toLowerCase());
  if (idxDate === -1 || idxVal === -1) return [];
  const series = [];
  rows.forEach((row) => {
    const date = parseDate(row[idxDate]);
    if (!date) return;
    const raw = row[idxVal];
    if (raw === undefined || raw === null || raw === "") return;
    const value = isTime ? parseClockToMinutes(raw) : Number(raw);
    if (value === null || Number.isNaN(value)) return;
    const display = isTime ? formatMinutes(value) : formatNumber(value);
    series.push({ date, value, display });
  });
  series.sort((a, b) => a.date - b.date);
  return series;
};

const run = () => {
  fs.mkdirSync(CHARTS_DIR, { recursive: true });
  const metricConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
  const metrics = [...metricConfig.metrics, ...EXTRA_METRICS];
  const chartMap = buildChartMap();
  let generated = 0;

  metrics.forEach((metric) => {
    const mapEntry = chartMap.get(metric.valueKey);
    if (!mapEntry) return;
    const csvPath = path.join(ROOT, `${mapEntry.stem}.csv`);
    if (!fs.existsSync(csvPath)) return;

    const { headers, rows } = readCsv(csvPath);
    const isTime = TIME_VALUE_KEYS.has(metric.valueKey);
    const series = buildSeries({ headers, rows, valueKey: metric.valueKey, isTime });
    if (!series.length) return;

    const lastDate = series[series.length - 1].date;
    const monthStart = new Date(lastDate.getTime() - 29 * 86400000);
    const yearStart = new Date(lastDate.getTime() - 364 * 86400000);
    const topSeries = series.filter((p) => p.date >= monthStart);
    const yearSeries = series.filter((p) => p.date >= yearStart);
    const bottomSeries = computeRollingAvg(yearSeries, 7).map((p) => ({
      ...p,
      display: isTime ? formatMinutes(p.value) : formatNumber(p.value),
    }));

    const svg = renderChart({
      label: metric.label,
      valueKey: metric.valueKey,
      topSeries,
      bottomSeries,
      guideLines: GUIDE_LINES[metric.valueKey] || [],
      isTime,
    });

    const outPath = path.join(CHARTS_DIR, `${mapEntry.stem}__${metric.valueKey}.svg`);
    fs.writeFileSync(outPath, svg, "utf8");
    generated += 1;
  });

  console.log(`Generated ${generated} SVG charts.`);
};

run();
