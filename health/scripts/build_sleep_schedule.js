const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const SCRIPT_DIR = __dirname;
const HEALTH_DIR = path.dirname(SCRIPT_DIR);
const DATA_DIR = path.join(HEALTH_DIR, "data");
const SESSION_GAP_MINUTES = 180;

const pad2 = (num) => String(num).padStart(2, "0");

const findExportZip = () => {
  const files = fs.readdirSync(HEALTH_DIR).filter((name) => name.toLowerCase().endsWith(".zip"));
  if (!files.length) {
    throw new Error("No zip export found in health/");
  }
  const stats = files.map((name) => {
    const full = path.join(HEALTH_DIR, name);
    return { name, full, size: fs.statSync(full).size };
  });
  stats.sort((a, b) => b.size - a.size);
  return stats[0].full;
};

const loadExportXmlBuffer = (zipPath) => {
  const zip = fs.readFileSync(zipPath);
  const EOCD_SIG = 0x06054b50;
  let eocdOffset = -1;
  const minSearch = Math.max(0, zip.length - 65557);
  for (let i = zip.length - 22; i >= minSearch; i -= 1) {
    if (zip.readUInt32LE(i) === EOCD_SIG) {
      eocdOffset = i;
      break;
    }
  }
  if (eocdOffset === -1) {
    throw new Error("EOCD not found");
  }

  const cdSize = zip.readUInt32LE(eocdOffset + 12);
  const cdOffset = zip.readUInt32LE(eocdOffset + 16);
  const CDFH_SIG = 0x02014b50;

  const entries = [];
  let offset = cdOffset;
  while (offset < cdOffset + cdSize) {
    if (zip.readUInt32LE(offset) !== CDFH_SIG) break;
    const compMethod = zip.readUInt16LE(offset + 10);
    const compSize = zip.readUInt32LE(offset + 20);
    const uncompSize = zip.readUInt32LE(offset + 24);
    const fileNameLen = zip.readUInt16LE(offset + 28);
    const extraLen = zip.readUInt16LE(offset + 30);
    const commentLen = zip.readUInt16LE(offset + 32);
    const localHeaderOffset = zip.readUInt32LE(offset + 42);
    const nameBuf = zip.slice(offset + 46, offset + 46 + fileNameLen);
    const fileNameUtf8 = nameBuf.toString("utf8");
    const fileNameLatin1 = nameBuf.toString("latin1");
    const nameLower = fileNameUtf8.toLowerCase();
    const latinLower = fileNameLatin1.toLowerCase();
    const isXml = nameLower.endsWith(".xml") || latinLower.endsWith(".xml");
    const isCda = nameLower.includes("cda") || latinLower.includes("cda");
    if (isXml && !isCda) {
      entries.push({
        fileName: fileNameUtf8,
        compMethod,
        compSize,
        uncompSize,
        localHeaderOffset,
      });
    }
    offset += 46 + fileNameLen + extraLen + commentLen;
  }

  if (!entries.length) {
    throw new Error("No non-CDA XML found");
  }

  entries.sort((a, b) => b.uncompSize - a.uncompSize);
  const target = entries[0];

  const LFH_SIG = 0x04034b50;
  const lfhOffset = target.localHeaderOffset;
  if (zip.readUInt32LE(lfhOffset) !== LFH_SIG) {
    throw new Error("Invalid local file header");
  }
  const fileNameLen2 = zip.readUInt16LE(lfhOffset + 26);
  const extraLen2 = zip.readUInt16LE(lfhOffset + 28);
  const dataStart = lfhOffset + 30 + fileNameLen2 + extraLen2;
  const compData = zip.slice(dataStart, dataStart + target.compSize);

  if (target.compMethod === 0) {
    return compData;
  }
  if (target.compMethod === 8) {
    return zlib.inflateRawSync(compData);
  }
  throw new Error(`Unsupported compression method: ${target.compMethod}`);
};

const parseHealthDate = (text) => {
  if (!text) return null;
  const trimmed = text.trim();
  const match = trimmed.match(
    /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})\s*([+-])(\d{2}):?(\d{2})$/
  );
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);
  const second = Number(match[6]);
  const sign = match[7] === "-" ? -1 : 1;
  const offsetHours = Number(match[8]);
  const offsetMins = Number(match[9]);
  const offsetMinutes = sign * (offsetHours * 60 + offsetMins);
  const utcMs = Date.UTC(year, month - 1, day, hour, minute, second) - offsetMinutes * 60000;
  return { utcMs, offsetMinutes };
};

const formatLocalDate = (utcMs, offsetMinutes) => {
  const localMs = utcMs + offsetMinutes * 60000;
  const d = new Date(localMs);
  return `${d.getUTCFullYear()}-${pad2(d.getUTCMonth() + 1)}-${pad2(d.getUTCDate())}`;
};

const formatLocalTime = (utcMs, offsetMinutes) => {
  const localMs = utcMs + offsetMinutes * 60000;
  const d = new Date(localMs);
  return `${pad2(d.getUTCHours())}:${pad2(d.getUTCMinutes())}`;
};

const getAttr = (line, name) => {
  const match = line.match(new RegExp(`${name}=\"([^\"]*)\"`));
  return match ? match[1] : "";
};

const SOURCE_BUCKETS = [
  {
    name: "appleWatch",
    test: (source) => /apple/i.test(source) && /watch/i.test(source),
  },
  {
    name: "iphone",
    test: (source) => /iphone/i.test(source),
  },
  {
    name: "health",
    test: (source) => /health/i.test(source),
  },
  {
    name: "other",
    test: () => true,
  },
];

const getBucketIndex = (source) => {
  for (let i = 0; i < SOURCE_BUCKETS.length; i += 1) {
    if (SOURCE_BUCKETS[i].test(source)) return i;
  }
  return SOURCE_BUCKETS.length - 1;
};

const buildSessions = (segments) => {
  if (!segments.length) return [];
  const gapMs = SESSION_GAP_MINUTES * 60 * 1000;
  const sorted = segments.slice().sort((a, b) => a.startUtcMs - b.startUtcMs);
  const sessions = [];
  let current = null;
  for (const seg of sorted) {
    if (!current || seg.startUtcMs - current.endUtcMs > gapMs) {
      if (current) sessions.push(current);
      current = {
        startUtcMs: seg.startUtcMs,
        endUtcMs: seg.endUtcMs,
        segments: [seg],
      };
    } else {
      current.endUtcMs = Math.max(current.endUtcMs, seg.endUtcMs);
      current.segments.push(seg);
    }
  }
  if (current) sessions.push(current);

  return sessions
    .map((session) => {
      const asleepSegments = session.segments.filter((seg) => seg.kind === "asleep");
      if (!asleepSegments.length) return null;
      let bedStartUtcMs = asleepSegments[0].startUtcMs;
      let bedOffset = asleepSegments[0].offsetMinutes;
      let wakeEndUtcMs = asleepSegments[0].endUtcMs;
      let totalSleepMs = 0;
      for (const seg of asleepSegments) {
        if (seg.startUtcMs < bedStartUtcMs) {
          bedStartUtcMs = seg.startUtcMs;
          bedOffset = seg.offsetMinutes;
        }
        if (seg.endUtcMs > wakeEndUtcMs) {
          wakeEndUtcMs = seg.endUtcMs;
        }
        totalSleepMs += seg.endUtcMs - seg.startUtcMs;
      }
      return {
        bedStartUtcMs,
        wakeEndUtcMs,
        offsetMinutes: bedOffset,
        totalSleepMs,
      };
    })
    .filter(Boolean);
};

const groupSessionsByDate = (sessions) => {
  const map = new Map();
  for (const session of sessions) {
    const wakeDate = formatLocalDate(session.wakeEndUtcMs, session.offsetMinutes);
    if (!map.has(wakeDate)) map.set(wakeDate, []);
    map.get(wakeDate).push(session);
  }
  return map;
};

const pickBestSession = (sessions) => {
  const sorted = sessions
    .slice()
    .sort(
      (a, b) =>
        b.totalSleepMs - a.totalSleepMs || a.bedStartUtcMs - b.bedStartUtcMs
    );
  return sorted[0];
};

const buildSchedule = () => {
  const zipPath = findExportZip();
  const xmlBuf = loadExportXmlBuffer(zipPath);
  const needle = Buffer.from("HKCategoryTypeIdentifierSleepAnalysis");

  const bucketSegments = SOURCE_BUCKETS.map(() => ({
    asleepAwake: [],
    inBed: [],
  }));

  let lineStart = 0;
  for (let i = 0; i < xmlBuf.length; i += 1) {
    if (xmlBuf[i] !== 0x0a) continue;
    const lineBuf = xmlBuf.slice(lineStart, i);
    lineStart = i + 1;
    if (!lineBuf.includes(needle)) continue;
    const line = lineBuf.toString("utf8");
    const recordType = getAttr(line, "type");
    if (recordType !== "HKCategoryTypeIdentifierSleepAnalysis") continue;
    const value = getAttr(line, "value");
    const startDate = getAttr(line, "startDate");
    const endDate = getAttr(line, "endDate");
    const sourceName = getAttr(line, "sourceName") || "Unknown";
    if (!value || !startDate || !endDate) continue;

    const startInfo = parseHealthDate(startDate);
    const endInfo = parseHealthDate(endDate);
    if (!startInfo || !endInfo) continue;

    let kind = "";
    if (value.startsWith("HKCategoryValueSleepAnalysisAsleep")) {
      kind = "asleep";
    } else if (value === "HKCategoryValueSleepAnalysisAwake") {
      kind = "awake";
    } else if (value === "HKCategoryValueSleepAnalysisInBed") {
      kind = "inbed";
    } else {
      continue;
    }

    const bucketIndex = getBucketIndex(sourceName);
    const entry = {
      startUtcMs: startInfo.utcMs,
      endUtcMs: endInfo.utcMs,
      offsetMinutes: startInfo.offsetMinutes,
      kind,
    };

    if (kind === "inbed") {
      bucketSegments[bucketIndex].inBed.push(entry);
    } else {
      bucketSegments[bucketIndex].asleepAwake.push(entry);
    }
  }

  const asleepMaps = [];
  const inbedMaps = [];
  const allDates = new Set();

  for (const bucket of bucketSegments) {
    const asleepSessions = buildSessions(bucket.asleepAwake);
    const inbedSessions = buildSessions(bucket.inBed);
    const asleepMap = groupSessionsByDate(asleepSessions);
    const inbedMap = groupSessionsByDate(inbedSessions);
    asleepMaps.push(asleepMap);
    inbedMaps.push(inbedMap);
    for (const date of asleepMap.keys()) allDates.add(date);
    for (const date of inbedMap.keys()) allDates.add(date);
  }

  const results = [];
  const sortedDates = Array.from(allDates).sort();
  for (const date of sortedDates) {
    let chosen = null;
    for (const map of asleepMaps) {
      const sessions = map.get(date);
      if (sessions && sessions.length) {
        chosen = pickBestSession(sessions);
        break;
      }
    }
    if (!chosen) {
      for (const map of inbedMaps) {
        const sessions = map.get(date);
        if (sessions && sessions.length) {
          chosen = pickBestSession(sessions);
          break;
        }
      }
    }
    if (!chosen) continue;
    results.push({
      date,
      bedTime: formatLocalTime(chosen.bedStartUtcMs, chosen.offsetMinutes),
      wakeTime: formatLocalTime(chosen.wakeEndUtcMs, chosen.offsetMinutes),
    });
  }

  const output = ["date,bed_time,wake_time"];
  results.forEach((row) => {
    output.push(`${row.date},${row.bedTime},${row.wakeTime}`);
  });

  fs.writeFileSync(path.join(DATA_DIR, "sleep_schedule_daily.csv"), output.join("\n"), "utf8");
  console.log(`sleep_schedule_daily.csv updated (${results.length} days)`);
};

buildSchedule();
