const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const SCRIPT_DIR = __dirname;
const HEALTH_DIR = path.dirname(SCRIPT_DIR);

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

const getAttr = (line, name) => {
  const match = line.match(new RegExp(`${name}=\"([^\"]*)\"`));
  return match ? match[1] : "";
};

const normalizeWorkoutType = (raw) => {
  if (!raw) return "Unknown";
  if (raw.includes("HKWorkoutActivityType")) {
    return raw.replace("HKWorkoutActivityType", "");
  }
  return raw;
};

const buildWorkoutList = () => {
  const zipPath = findExportZip();
  const xmlBuf = loadExportXmlBuffer(zipPath);
  const workouts = [];
  let lineStart = 0;
  for (let i = 0; i <= xmlBuf.length; i += 1) {
    const isEnd = i === xmlBuf.length;
    const ch = isEnd ? 10 : xmlBuf[i];
    if (ch !== 10) continue;
    const lineBuf = xmlBuf.slice(lineStart, i);
    lineStart = i + 1;
    if (!lineBuf.length) continue;
    const line = lineBuf.toString("utf8");
    if (line.indexOf("<Workout ") === -1) continue;
    const typeRaw = getAttr(line, "workoutActivityType");
    const start = parseHealthDate(getAttr(line, "startDate"));
    const end = parseHealthDate(getAttr(line, "endDate"));
    const duration = parseFloat(getAttr(line, "duration"));
    if (!start || !end || Number.isNaN(duration)) continue;
    const date = formatLocalDate(start.utcMs, start.offsetMinutes);
    workouts.push({
      date,
      type: normalizeWorkoutType(typeRaw),
      duration,
    });
  }
  return workouts;
};

const run = () => {
  const workouts = buildWorkoutList();
  if (!workouts.length) {
    console.log("No workout records found.");
    return;
  }
  workouts.sort((a, b) => (a.date > b.date ? 1 : -1));
  const lastDate = workouts[workouts.length - 1].date;
  const last = new Date(`${lastDate}T00:00:00Z`);
  const start = new Date(last);
  start.setUTCDate(start.getUTCDate() - 6);

  const groups = new Map();
  workouts.forEach((item) => {
    const d = new Date(`${item.date}T00:00:00Z`);
    if (d < start || d > last) return;
    const key = item.date;
    if (!groups.has(key)) groups.set(key, new Map());
    const typeMap = groups.get(key);
    typeMap.set(item.type, (typeMap.get(item.type) || 0) + item.duration);
  });

  const days = [];
  for (let i = 0; i < 7; i += 1) {
    const d = new Date(start);
    d.setUTCDate(start.getUTCDate() + i);
    days.push(`${d.getUTCFullYear()}-${pad2(d.getUTCMonth() + 1)}-${pad2(d.getUTCDate())}`);
  }

  console.log("最近7天运动时长明细（按类型汇总，单位：分钟）");
  days.forEach((date) => {
    console.log(`\n${date}`);
    const typeMap = groups.get(date);
    if (!typeMap) {
      console.log("  - 无");
      return;
    }
    Array.from(typeMap.entries())
      .sort((a, b) => b[1] - a[1])
      .forEach(([type, minutes]) => {
        console.log(`  - ${type}: ${minutes.toFixed(1)}`);
      });
  });
};

run();
