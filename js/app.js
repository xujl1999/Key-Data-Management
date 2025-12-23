const statusEl = document.getElementById("status");
      const updateTimeEl = document.getElementById("update-time");
      const headRow = document.getElementById("table-head");
      const bodyEl = document.getElementById("table-body");
      const categoryGroup = document.getElementById("category-group");
      const limitInput = document.getElementById("limit-input");
      const tabButtons = document.querySelectorAll(".tab-button");
      const tabPanels = document.querySelectorAll(".tab-panel");
      const healthStatus = document.getElementById("health-status");
      const metricTableBody = document.getElementById("health-metric-body");
      const healthCategoryGroup = document.getElementById("health-category-group");
      const highlightEls = {
        weight: document.getElementById("hl-weight"),
        weightWow: document.getElementById("hl-weight-wow"),
        bodyFat: document.getElementById("hl-bodyfat"),
        bodyFatWow: document.getElementById("hl-bodyfat-wow"),
        sleep: document.getElementById("hl-sleep"),
        sleepWow: document.getElementById("hl-sleep-wow"),
        bedTime: document.getElementById("hl-bedtime"),
        bedTimeWow: document.getElementById("hl-bedtime-wow"),
        wakeTime: document.getElementById("hl-wake"),
        wakeTimeWow: document.getElementById("hl-wake-wow"),
        hrv: document.getElementById("hl-hrv"),
        hrvWow: document.getElementById("hl-hrv-wow"),
        exerciseWeek: document.getElementById("hl-ex-week"),
        exerciseMonth: document.getElementById("hl-ex-month"),
        exerciseMsg: document.getElementById("hl-ex-msg"),
      };

      const CATEGORY_OPTIONS = ["全部", "超优质", "历史区", "创意区", "运动区", "游戏区", "影视综", "数分"];
      const DEFAULT_CATEGORY = "超优质";
      const DEFAULT_LIMIT = 1;
      const MAX_LIMIT = 10;
      const CSV_SOURCES = [{ url: "video/video_ls.csv", label: "Local" }];
      const HEALTH_SOURCES = [{ url: "health/data/sleep_daily.csv", label: "Local" }];
      const WEIGHT_SOURCES = [{ url: "health/data/weight_daily.csv", label: "Local" }];
      const STEPS_SOURCES = [{ url: "health/data/steps_daily.csv", label: "Local" }];
      const ENERGY_SOURCES = [{ url: "health/data/energy_daily.csv", label: "Local" }];
      const DIET_SOURCES = [
        { url: "health/data/diet_daily.csv", label: "Local" },
      ];
      const HR_SOURCES = [
        { url: "health/data/heart_rate_daily.csv", label: "Local" },
      ];
      const REST_HR_SOURCES = [
        { url: "health/data/resting_hr_daily.csv", label: "Local" },
      ];
      const WALK_HR_SOURCES = [
        { url: "health/data/walking_hr_daily.csv", label: "Local" },
      ];
      const RESP_SOURCES = [
        { url: "health/data/respiratory_daily.csv", label: "Local" },
      ];
      const VO2_SOURCES = [
        { url: "health/data/vo2max_daily.csv", label: "Local" },
      ];
      const WALK_METRIC_SOURCES = [
        { url: "health/data/walking_metrics_daily.csv", label: "Local" },
      ];
      const WALK_STEP_LEN_SOURCES = [
        { url: "health/data/walking_step_length_daily.csv", label: "Local" },
      ];
      const WALK_DS_SOURCES = [
        { url: "health/data/walking_double_support_daily.csv", label: "Local" },
      ];
      const WALK_ASYM_SOURCES = [
        { url: "health/data/walking_asymmetry_daily.csv", label: "Local" },
      ];
      const WALK_STEADY_SOURCES = [
        { url: "health/data/walking_steadiness_daily.csv", label: "Local" },
      ];
      const RUN_SPEED_SOURCES = [
        { url: "health/data/running_speed_daily.csv", label: "Local" },
      ];
      const RUN_POWER_SOURCES = [
        { url: "health/data/running_power_daily.csv", label: "Local" },
      ];
      const RUN_VERT_SOURCES = [
        { url: "health/data/running_vertical_osc_daily.csv", label: "Local" },
      ];
      const RUN_GC_SOURCES = [
        { url: "health/data/running_ground_contact_daily.csv", label: "Local" },
      ];
      const RUN_STRIDE_SOURCES = [
        { url: "health/data/running_stride_length_daily.csv", label: "Local" },
      ];
      const STAIR_ASC_SOURCES = [
        { url: "health/data/stair_ascent_speed_daily.csv", label: "Local" },
      ];
      const STAIR_DESC_SOURCES = [
        { url: "health/data/stair_descent_speed_daily.csv", label: "Local" },
      ];
      const AUDIO_ENV_SOURCES = [
        { url: "health/data/audio_exposure_daily.csv", label: "Local" },
      ];
      const AUDIO_HEAD_SOURCES = [
        { url: "health/data/headphone_audio_daily.csv", label: "Local" },
      ];
      const EXERCISE_SOURCES = [
        { url: "health/data/exercise_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/exercise_daily.csv", label: "GitHub Raw" },
      ];
      const DISTANCE_SOURCES = [
        { url: "health/data/distance_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/distance_daily.csv", label: "GitHub Raw" },
      ];
      const RESTING_HR_SOURCES = [
        { url: "health/data/resting_hr_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/resting_hr_daily.csv", label: "GitHub Raw" },
      ];
      const BODY_SOURCES = [
        { url: "health/data/body_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/body_daily.csv", label: "GitHub Raw" },
      ];
      const HEART_RATE_SOURCES = [
        { url: "health/data/heart_rate_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/heart_rate_daily.csv", label: "GitHub Raw" },
      ];
      const HRV_SOURCES = [
        { url: "health/data/hrv_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/hrv_daily.csv", label: "GitHub Raw" },
      ];
      const RESPIRATORY_SOURCES = [
        { url: "health/data/respiratory_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/respiratory_daily.csv", label: "GitHub Raw" },
      ];
      const SPO2_SOURCES = [
        { url: "health/data/spo2_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/spo2_daily.csv", label: "GitHub Raw" },
      ];
      const VO2MAX_SOURCES = [
        { url: "health/data/vo2max_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/vo2max_daily.csv", label: "GitHub Raw" },
      ];
      const FLIGHTS_SOURCES = [
        { url: "health/data/flights_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/flights_daily.csv", label: "GitHub Raw" },
      ];
      const DAYLIGHT_SOURCES = [
        { url: "health/data/daylight_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/daylight_daily.csv", label: "GitHub Raw" },
      ];
      const WALKING_HR_SOURCES = [
        { url: "health/data/walking_hr_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/walking_hr_daily.csv", label: "GitHub Raw" },
      ];
      const WALKING_METRICS_SOURCES = [
        { url: "health/data/walking_metrics_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/walking_metrics_daily.csv", label: "GitHub Raw" },
      ];
      const WALKING_STEP_LENGTH_SOURCES = [
        { url: "health/data/walking_step_length_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/walking_step_length_daily.csv", label: "GitHub Raw" },
      ];
      const WALKING_DOUBLE_SUPPORT_SOURCES = [
        { url: "health/data/walking_double_support_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/walking_double_support_daily.csv", label: "GitHub Raw" },
      ];
      const WALKING_ASYMMETRY_SOURCES = [
        { url: "health/data/walking_asymmetry_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/walking_asymmetry_daily.csv", label: "GitHub Raw" },
      ];
      const WALKING_STEADINESS_SOURCES = [
        { url: "health/data/walking_steadiness_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/walking_steadiness_daily.csv", label: "GitHub Raw" },
      ];
      const RUNNING_SPEED_SOURCES = [
        { url: "health/data/running_speed_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/running_speed_daily.csv", label: "GitHub Raw" },
      ];
      const RUNNING_POWER_SOURCES = [
        { url: "health/data/running_power_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/running_power_daily.csv", label: "GitHub Raw" },
      ];
      const RUNNING_STRIDE_LENGTH_SOURCES = [
        { url: "health/data/running_stride_length_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/running_stride_length_daily.csv", label: "GitHub Raw" },
      ];
      const RUNNING_VERTICAL_OSC_SOURCES = [
        { url: "health/data/running_vertical_osc_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/running_vertical_osc_daily.csv", label: "GitHub Raw" },
      ];
      const RUNNING_GROUND_CONTACT_SOURCES = [
        { url: "health/data/running_ground_contact_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/running_ground_contact_daily.csv", label: "GitHub Raw" },
      ];
      const STAIR_ASCENT_SPEED_SOURCES = [
        { url: "health/data/stair_ascent_speed_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/stair_ascent_speed_daily.csv", label: "GitHub Raw" },
      ];
      const STAIR_DESCENT_SPEED_SOURCES = [
        { url: "health/data/stair_descent_speed_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/stair_descent_speed_daily.csv", label: "GitHub Raw" },
      ];
      const AUDIO_EXPOSURE_SOURCES = [
        { url: "health/data/audio_exposure_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/audio_exposure_daily.csv", label: "GitHub Raw" },
      ];
      const HEADPHONE_AUDIO_SOURCES = [
        { url: "health/data/headphone_audio_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/headphone_audio_daily.csv", label: "GitHub Raw" },
      ];
      const SLEEP_TEMP_SOURCES = [
        { url: "health/data/sleep_temp_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/sleep_temp_daily.csv", label: "GitHub Raw" },
      ];
      const SLEEP_SCHEDULE_SOURCES = [
        { url: "health/data/sleep_schedule_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/sleep_schedule_daily.csv", label: "GitHub Raw" },
      ];
      const DISTANCE_CYCLING_SOURCES = [
        { url: "health/data/distance_daily.csv", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/health/data/distance_daily.csv", label: "GitHub Raw" },
      ];

      const dataSources = (window.KDM_CONFIG && window.KDM_CONFIG.dataSources) || {};
      const applySourceOverrides = (key, target) => {
        const override = dataSources[key];
        if (!Array.isArray(override)) return;
        target.length = 0;
        override.forEach((item) => target.push(item));
      };

      const METRIC_DEFS = [
        { label: "睡眠时长", valueKey: "sleep_hours", unit: "小时", sources: HEALTH_SOURCES },
        { label: "体重", valueKey: "weight_kg", unit: "kg", sources: WEIGHT_SOURCES },
        { label: "步数", valueKey: "steps", unit: "步", sources: STEPS_SOURCES },
        { label: "主动能量", valueKey: "active_energy", unit: "kcal", sources: ENERGY_SOURCES },
        { label: "基础代谢", valueKey: "basal_energy", unit: "kcal", sources: ENERGY_SOURCES },
        { label: "身体负荷指数", valueKey: "physical_effort", unit: "AU", sources: ENERGY_SOURCES },
        { label: "锻炼时长", valueKey: "exercise_time_min", unit: "分钟", sources: EXERCISE_SOURCES },
        { label: "站立时长", valueKey: "stand_time_min", unit: "分钟", sources: EXERCISE_SOURCES },
        { label: "站立小时数", valueKey: "stand_hours", unit: "小时", sources: EXERCISE_SOURCES },
        { label: "步行跑步距离", valueKey: "distance_walk_run_km", unit: "km", sources: DISTANCE_SOURCES },
        { label: "骑行距离", valueKey: "distance_cycling_km", unit: "km", sources: DISTANCE_CYCLING_SOURCES },
        { label: "爬楼层数", valueKey: "flights_climbed", unit: "层", sources: FLIGHTS_SOURCES },
        { label: "户外日照时长", valueKey: "time_in_daylight_min", unit: "分钟", sources: DAYLIGHT_SOURCES },
        { label: "静息心率", valueKey: "resting_hr_avg", unit: "bpm", sources: RESTING_HR_SOURCES },
        { label: "心率均值", valueKey: "hr_avg", unit: "bpm", sources: HEART_RATE_SOURCES },
        { label: "心率最小值", valueKey: "hr_min", unit: "bpm", sources: HEART_RATE_SOURCES },
        { label: "心率最大值", valueKey: "hr_max", unit: "bpm", sources: HEART_RATE_SOURCES },
        { label: "步行心率均值", valueKey: "walk_hr_avg", unit: "bpm", sources: WALKING_HR_SOURCES },
        { label: "HRV-SDNN均值", valueKey: "sdnn_avg", unit: "ms", sources: HRV_SOURCES },
        { label: "呼吸频率均值", valueKey: "resp_avg", unit: "次/分", sources: RESPIRATORY_SOURCES },
        { label: "血氧均值", valueKey: "spo2_avg", unit: "%", sources: SPO2_SOURCES },
        { label: "最大摄氧量均值", valueKey: "vo2max_avg", unit: "ml·kg⁻¹·min⁻¹", sources: VO2MAX_SOURCES },
        { label: "BMI", valueKey: "bmi", unit: "", sources: BODY_SOURCES },
        { label: "体脂率", valueKey: "body_fat_pct", unit: "%", sources: BODY_SOURCES },
        { label: "去脂体重", valueKey: "lean_mass_kg", unit: "kg", sources: BODY_SOURCES },
        { label: "行走速度均值", valueKey: "walking_speed_avg", unit: "m/s", sources: WALKING_METRICS_SOURCES },
        { label: "步长均值", valueKey: "step_length_avg", unit: "cm", sources: WALKING_STEP_LENGTH_SOURCES },
        { label: "双支撑占比均值", valueKey: "double_support_pct_avg", unit: "%", sources: WALKING_DOUBLE_SUPPORT_SOURCES },
        { label: "步态不对称均值", valueKey: "asymmetry_pct_avg", unit: "%", sources: WALKING_ASYMMETRY_SOURCES },
        { label: "步态稳定度均值", valueKey: "steady_avg", unit: "分", sources: WALKING_STEADINESS_SOURCES },
        { label: "跑步速度均值", valueKey: "running_speed_avg", unit: "m/s", sources: RUNNING_SPEED_SOURCES },
        { label: "跑步功率均值", valueKey: "running_power_avg", unit: "W", sources: RUNNING_POWER_SOURCES },
        { label: "跑步步幅均值", valueKey: "running_stride_len_avg", unit: "m", sources: RUNNING_STRIDE_LENGTH_SOURCES },
        { label: "跑步垂直振幅均值", valueKey: "running_vertical_osc_avg", unit: "cm", sources: RUNNING_VERTICAL_OSC_SOURCES },
        { label: "着地时间均值", valueKey: "ground_contact_ms_avg", unit: "ms", sources: RUNNING_GROUND_CONTACT_SOURCES },
        { label: "上楼速度均值", valueKey: "stair_ascent_speed_avg", unit: "m/s", sources: STAIR_ASCENT_SPEED_SOURCES },
        { label: "下楼速度均值", valueKey: "stair_descent_speed_avg", unit: "m/s", sources: STAIR_DESCENT_SPEED_SOURCES },
        { label: "环境噪声均值", valueKey: "env_audio_avg", unit: "dB", sources: AUDIO_EXPOSURE_SOURCES },
        { label: "耳机音量均值", valueKey: "headphone_audio_avg", unit: "dB", sources: HEADPHONE_AUDIO_SOURCES },
        { label: "睡眠手腕温度均值", valueKey: "temp_avg", unit: "°C", sources: SLEEP_TEMP_SOURCES },
      ];

      const HIGHLIGHT_EXTRA_DEFS = [
        { label: "入睡时间", valueKey: "bed_time", unit: "", sources: SLEEP_SCHEDULE_SOURCES },
        { label: "起床时间", valueKey: "wake_time", unit: "", sources: SLEEP_SCHEDULE_SOURCES },
        { label: "本周运动天数", valueKey: "exercise_days", unit: "天", sources: EXERCISE_SOURCES },
        { label: "本月运动天数", valueKey: "exercise_days", unit: "天", sources: EXERCISE_SOURCES },
      ];

            const healthGoals = (window.KDM_CONFIG && window.KDM_CONFIG.healthGoals) || {};
      const exerciseGoal = healthGoals["运动相关"]?.exercise_time_min;
      const sleepGoal = healthGoals["睡眠相关"]?.sleep_hours;
      const hrvGoal = healthGoals["心肺指标"]?.sdnn_avg;

const EXERCISE_DAY_THRESHOLD_MIN = Number(exerciseGoal?.target) || 30;
const EXERCISE_WARN_SLEEP_HOURS = Number(sleepGoal?.warning) || 6;
const EXERCISE_WARN_HRV = Number(hrvGoal?.warning) || 30;

      const HEALTH_METRIC_CONFIG_SOURCES = [
        { url: "config/health_metrics.json", label: "Local" },
        { url: "https://raw.githubusercontent.com/xujl1999/Key-Data-Management/main/config/health_metrics.json", label: "GitHub Raw" },
      ];

      [
        ["CSV_SOURCES", CSV_SOURCES],
        ["HEALTH_SOURCES", HEALTH_SOURCES],
        ["WEIGHT_SOURCES", WEIGHT_SOURCES],
        ["STEPS_SOURCES", STEPS_SOURCES],
        ["ENERGY_SOURCES", ENERGY_SOURCES],
        ["DIET_SOURCES", DIET_SOURCES],
        ["HR_SOURCES", HR_SOURCES],
        ["REST_HR_SOURCES", REST_HR_SOURCES],
        ["WALK_HR_SOURCES", WALK_HR_SOURCES],
        ["RESP_SOURCES", RESP_SOURCES],
        ["VO2_SOURCES", VO2_SOURCES],
        ["WALK_METRIC_SOURCES", WALK_METRIC_SOURCES],
        ["WALK_STEP_LEN_SOURCES", WALK_STEP_LEN_SOURCES],
        ["WALK_DS_SOURCES", WALK_DS_SOURCES],
        ["WALK_ASYM_SOURCES", WALK_ASYM_SOURCES],
        ["WALK_STEADY_SOURCES", WALK_STEADY_SOURCES],
        ["RUN_SPEED_SOURCES", RUN_SPEED_SOURCES],
        ["RUN_POWER_SOURCES", RUN_POWER_SOURCES],
        ["RUN_VERT_SOURCES", RUN_VERT_SOURCES],
        ["RUN_GC_SOURCES", RUN_GC_SOURCES],
        ["RUN_STRIDE_SOURCES", RUN_STRIDE_SOURCES],
        ["STAIR_ASC_SOURCES", STAIR_ASC_SOURCES],
        ["STAIR_DESC_SOURCES", STAIR_DESC_SOURCES],
        ["AUDIO_ENV_SOURCES", AUDIO_ENV_SOURCES],
        ["AUDIO_HEAD_SOURCES", AUDIO_HEAD_SOURCES],
        ["EXERCISE_SOURCES", EXERCISE_SOURCES],
        ["DISTANCE_SOURCES", DISTANCE_SOURCES],
        ["RESTING_HR_SOURCES", RESTING_HR_SOURCES],
        ["BODY_SOURCES", BODY_SOURCES],
        ["HEART_RATE_SOURCES", HEART_RATE_SOURCES],
        ["HRV_SOURCES", HRV_SOURCES],
        ["RESPIRATORY_SOURCES", RESPIRATORY_SOURCES],
        ["SPO2_SOURCES", SPO2_SOURCES],
        ["VO2MAX_SOURCES", VO2MAX_SOURCES],
        ["FLIGHTS_SOURCES", FLIGHTS_SOURCES],
        ["DAYLIGHT_SOURCES", DAYLIGHT_SOURCES],
        ["WALKING_HR_SOURCES", WALKING_HR_SOURCES],
        ["WALKING_METRICS_SOURCES", WALKING_METRICS_SOURCES],
        ["WALKING_STEP_LENGTH_SOURCES", WALKING_STEP_LENGTH_SOURCES],
        ["WALKING_DOUBLE_SUPPORT_SOURCES", WALKING_DOUBLE_SUPPORT_SOURCES],
        ["WALKING_ASYMMETRY_SOURCES", WALKING_ASYMMETRY_SOURCES],
        ["WALKING_STEADINESS_SOURCES", WALKING_STEADINESS_SOURCES],
        ["RUNNING_SPEED_SOURCES", RUNNING_SPEED_SOURCES],
        ["RUNNING_POWER_SOURCES", RUNNING_POWER_SOURCES],
        ["RUNNING_STRIDE_LENGTH_SOURCES", RUNNING_STRIDE_LENGTH_SOURCES],
        ["RUNNING_VERTICAL_OSC_SOURCES", RUNNING_VERTICAL_OSC_SOURCES],
        ["RUNNING_GROUND_CONTACT_SOURCES", RUNNING_GROUND_CONTACT_SOURCES],
        ["STAIR_ASCENT_SPEED_SOURCES", STAIR_ASCENT_SPEED_SOURCES],
        ["STAIR_DESCENT_SPEED_SOURCES", STAIR_DESCENT_SPEED_SOURCES],
        ["AUDIO_EXPOSURE_SOURCES", AUDIO_EXPOSURE_SOURCES],
        ["HEADPHONE_AUDIO_SOURCES", HEADPHONE_AUDIO_SOURCES],
        ["SLEEP_TEMP_SOURCES", SLEEP_TEMP_SOURCES],
        ["SLEEP_SCHEDULE_SOURCES", SLEEP_SCHEDULE_SOURCES],
        ["DISTANCE_CYCLING_SOURCES", DISTANCE_CYCLING_SOURCES],
        ["HEALTH_METRIC_CONFIG_SOURCES", HEALTH_METRIC_CONFIG_SOURCES],
      ].forEach(([key, target]) => applySourceOverrides(key, target));

      const DEFAULT_HEALTH_METRIC_CATEGORY = "基础体征";
      window.healthMetricDefs = window.healthMetricDefs || METRIC_DEFS.slice();
      let healthMetricDefs = window.healthMetricDefs;
      let healthMetricCategories = ["全部"];
      let activeHealthMetricCategory = DEFAULT_HEALTH_METRIC_CATEGORY;
      let metricRows = [];

      window.records = window.records || [];
      let records = window.records;
      let activeCategory = CATEGORY_OPTIONS.includes(DEFAULT_CATEGORY) ? DEFAULT_CATEGORY : CATEGORY_OPTIONS[0];

      const fallbackHeader = (text, index) => {
        if (text && text.trim()) return text.trim();
        return index === 0 ? "id" : `col_${index}`;
      };

      const parseCSV = (text) => {
        const rows = [];
        let current = "";
        let row = [];
        let inQuotes = false;

        for (let i = 0; i < text.length; i++) {
          const char = text[i];
          const next = text[i + 1];

          if (char === "\r" && next === "\n" && !inQuotes) {
            continue;
          }

          if (char === "\n" && !inQuotes) {
            row.push(current);
            rows.push(row);
            row = [];
            current = "";
            continue;
          }

          if (char === '"') {
            if (inQuotes && next === '"') {
              current += '"';
              i++;
            } else {
              inQuotes = !inQuotes;
            }
            continue;
          }

          if (char === "," && !inQuotes) {
            row.push(current);
            current = "";
            continue;
          }

          current += char;
        }

        if (current.length > 0 || row.length) {
          row.push(current);
          rows.push(row);
        }

        return rows.filter((cells) => cells.some((cell) => cell.trim().length));
      };

      const normalizeKey = (text) => text.trim().toLowerCase();

      const parseDate = (text) => {
        const d = new Date(text);
        return Number.isNaN(d.getTime()) ? null : d;
      };

      const createCell = (tag, text, linkHref = "") => {
        const cell = document.createElement(tag);
        if (linkHref && text) {
          const link = document.createElement("a");
          link.href = linkHref;
          link.target = "_blank";
          link.rel = "noopener";
          link.textContent = text;
          cell.appendChild(link);
        } else {
          cell.textContent = text || "";
        }
        return cell;
      };

      const parsePublishDate = (text) => {
        if (!text) return 0;
        const now = new Date();
        const cleaned = text.trim();
        if (!cleaned) return 0;

        const normalized = cleaned.replace(/\./g, "-");
        const direct = Date.parse(normalized);
        if (!Number.isNaN(direct)) {
          return direct;
        }

        const mmddPattern = /^(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?$/;
        const mmddMatch = cleaned.match(mmddPattern);
        if (mmddMatch) {
          const year = now.getFullYear();
          const month = parseInt(mmddMatch[1], 10) - 1;
          const day = parseInt(mmddMatch[2], 10);
          const hour = mmddMatch[3] ? parseInt(mmddMatch[3], 10) : 0;
          const minute = mmddMatch[4] ? parseInt(mmddMatch[4], 10) : 0;
          const guessed = new Date(year, month, day, hour, minute);
          if (guessed > now) {
            guessed.setFullYear(year - 1);
          }
          return guessed.getTime();
        }

        const relHour = cleaned.match(/^(\d+)\s*小时前$/);
        if (relHour) {
          const diff = parseInt(relHour[1], 10);
          const d = new Date(now);
          d.setHours(d.getHours() - diff);
          return d.getTime();
        }

        const relMinute = cleaned.match(/^(\d+)\s*分钟前$/);
        if (relMinute) {
          const diff = parseInt(relMinute[1], 10);
          const d = new Date(now);
          d.setMinutes(d.getMinutes() - diff);
          return d.getTime();
        }

        const yesterdayMatch = cleaned.match(/^昨天(?:\s+(\d{1,2}):(\d{2}))?$/);
        if (yesterdayMatch) {
          const d = new Date(now);
          d.setDate(d.getDate() - 1);
          const hour = yesterdayMatch[1] ? parseInt(yesterdayMatch[1], 10) : 0;
          const minute = yesterdayMatch[2] ? parseInt(yesterdayMatch[2], 10) : 0;
          d.setHours(hour, minute, 0, 0);
          return d.getTime();
        }

        const todayTime = cleaned.match(/^(\d{1,2}):(\d{2})$/);
        if (todayTime) {
          const d = new Date(now);
          d.setHours(parseInt(todayTime[1], 10), parseInt(todayTime[2], 10), 0, 0);
          return d.getTime();
        }

        if (cleaned === "刚刚") {
          return now.getTime();
        }

        return 0;
      };

      const ensureLimitValue = () => {
        if (!limitInput) return DEFAULT_LIMIT;
        let value = parseInt(limitInput.value, 10);
        if (Number.isNaN(value) || value < 1) {
          value = DEFAULT_LIMIT;
        }
        value = Math.min(value, MAX_LIMIT);
        limitInput.value = value;
        return value;
      };

      const initLimitSelect = () => {
        if (!limitInput) return;
        limitInput.innerHTML = "";
        for (let i = 1; i <= MAX_LIMIT; i++) {
          const option = document.createElement("option");
          option.value = i;
          option.textContent = i;
          if (i === DEFAULT_LIMIT) {
            option.selected = true;
          }
          limitInput.appendChild(option);
        }
      };

      const switchTab = (target) => {
        tabButtons.forEach((button) => {
          button.classList.toggle("tab-button--active", button.dataset.tab === target);
        });
        tabPanels.forEach((panel) => {
          panel.classList.toggle("tab-panel--active", panel.id === `tab-${target}`);
        });
      };

      const renderLineChart = (container, data, options = {}) => {
        container.innerHTML = "";
        if (!data.length) {
          container.textContent = "暂无数据";
          return;
        }
        const width = options.width || 800;
        const height = options.height || 280;
        const padding = 30;

        const xs = data.map((_, idx) => idx);
        const ys = data.map((d) => d.value);
        const minY = Math.min(...ys, 0);
        const maxY = Math.max(...ys, 1);
        const yRange = maxY - minY || 1;

        const scaleX = (x) =>
          padding + (x / Math.max(xs.length - 1, 1)) * (width - padding * 2);
        const scaleY = (y) =>
          height - padding - ((y - minY) / yRange) * (height - padding * 2);

        const points = data.map((d, idx) => `${scaleX(idx)},${scaleY(d.value)}`).join(" ");

        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "320");

        // Axes (minimal)
        const axis = document.createElementNS("http://www.w3.org/2000/svg", "line");
        axis.setAttribute("x1", padding);
        axis.setAttribute("y1", scaleY(minY));
        axis.setAttribute("x2", width - padding);
        axis.setAttribute("y2", scaleY(minY));
        axis.setAttribute("stroke", "rgba(148,163,184,0.4)");
        axis.setAttribute("stroke-width", "1");
        svg.appendChild(axis);

        const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
        polyline.setAttribute("points", points);
        polyline.setAttribute("fill", "none");
        polyline.setAttribute("stroke", options.color || "#60a5fa");
        polyline.setAttribute("stroke-width", "2");
        svg.appendChild(polyline);

        // Labels (first/last)
        const addLabel = (text, x, y) => {
          const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
          t.setAttribute("x", x);
          t.setAttribute("y", y);
          t.setAttribute("fill", "#cbd5f5");
          t.setAttribute("font-size", "12");
          t.textContent = text;
          svg.appendChild(t);
        };

        if (data.length) {
          addLabel(data[0].label, scaleX(0), height - padding + 14);
          addLabel(data[data.length - 1].label, scaleX(data.length - 1) - 20, height - padding + 14);
          addLabel(maxY.toFixed(1), padding, scaleY(maxY) - 6);
          addLabel(minY.toFixed(1), padding, scaleY(minY) + 14);
        }

        container.appendChild(svg);
      };

      const renderCategoryChips = () => {
        if (!categoryGroup) return;
        categoryGroup.innerHTML = "";
        CATEGORY_OPTIONS.forEach((label) => {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = `chip${label === activeCategory ? " chip--active" : ""}`;
          chip.textContent = label;
          chip.addEventListener("click", () => {
            if (activeCategory === label) return;
            activeCategory = label;
            renderCategoryChips();
            applyFilters();
          });
          categoryGroup.appendChild(chip);
        });
      };

      const buildRecords = (rows) => {
        if (!rows.length) return [];
        const headers = rows[0].map(fallbackHeader).map(normalizeKey);
        return rows.slice(1).map((row) => {
          const record = {};
          headers.forEach((key, idx) => {
            record[key] = (row[idx] || "").trim();
          });
          record._timestamp = parsePublishDate(record.publish_date || record["publish_date"]);
          return record;
        });
      };

      const renderHeader = () => {
        if (!headRow) return;
        headRow.innerHTML = "";
        ["作者", "视频发布时间", "视频名称"].forEach((text) => {
          headRow.appendChild(createCell("th", text));
        });
      };

      const renderBody = (rows) => {
        if (!bodyEl) return;
        bodyEl.innerHTML = "";
        if (!rows.length) {
          const tr = document.createElement("tr");
          const cell = document.createElement("td");
          cell.colSpan = 3;
          cell.textContent = "暂无数据";
          tr.appendChild(cell);
          bodyEl.appendChild(tr);
          return;
        }

        rows.forEach((item) => {
          const tr = document.createElement("tr");
          tr.appendChild(createCell("td", item.author || "-"));
          tr.appendChild(createCell("td", item.publish_date || "-"));
          tr.appendChild(createCell("td", item.title || "", item.url || ""));
          bodyEl.appendChild(tr);
        });
      };

      const applyFilters = () => {
        if (!records.length) {
          renderBody([]);
          statusEl.textContent = "暂无数据";
          return;
        }

        const limit = ensureLimitValue();
        const authorCounts = new Map();
        const authorSet = new Set();
        const rows = [];

        records.forEach((record) => {
          const category = record.category || record["category"] || "";
          if (!record.author || !record.title) return;
          if (activeCategory !== "全部" && category !== activeCategory) return;

          const used = authorCounts.get(record.author) || 0;
          if (used >= limit) return;

          authorCounts.set(record.author, used + 1);
          authorSet.add(record.author);
          rows.push(record);
        });

        rows.sort((a, b) => (b._timestamp || 0) - (a._timestamp || 0));

        renderBody(rows);

        if (rows.length) {
          statusEl.textContent = `筛选：${activeCategory} · 作者 ${authorSet.size} 位，共 ${rows.length} 条（每位最多 ${limit} 条）`;
        } else {
          statusEl.textContent = "暂无匹配数据";
        }
      };

      if (limitInput) {
        limitInput.addEventListener("change", () => {
          ensureLimitValue();
          applyFilters();
          renderEntertainmentTagCloud();
        });
      }

      tabButtons.forEach((button) => {
        button.addEventListener("click", () => switchTab(button.dataset.tab));
      });

      const formatUpdateTime = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        return ` ${year}-${month}-${day} ${hours}:${minutes}`;
      };

      const isSameOrigin = (url) => {
        try {
          const absolute = new URL(url, window.location.href);
          return absolute.origin === window.location.origin;
        } catch (error) {
          console.warn("Invalid URL for origin check", url, error);
          return false;
        }
      };

      const resolveLastModified = async (response, url) => {
        const headerValue = response.headers.get("Last-Modified");
        if (headerValue) {
          const parsed = new Date(headerValue);
          if (!Number.isNaN(parsed.getTime())) {
            return parsed;
          }
        }
        if (!isSameOrigin(url)) {
          return null;
        }
        try {
          const headResp = await fetch(url, { method: "HEAD", cache: "no-store" });
          if (headResp.ok) {
            const headValue = headResp.headers.get("Last-Modified");
            if (headValue) {
              const fallback = new Date(headValue);
              if (!Number.isNaN(fallback.getTime())) {
                return fallback;
              }
            }
          }
        } catch (error) {
          console.warn("HEAD request failed", error);
        }
        return null;
      };


      const avgWindow = (series, count, offset = 0) => {
        if (series.length < count + offset) return null;
        const slice = series.slice(series.length - count - offset, series.length - offset);
        const total = slice.reduce((acc, cur) => acc + cur.ma, 0);
        return total / slice.length;
      };

      const formatDelta = (current, previous) => {
        if (current === null || previous === null || previous === 0) return { text: "—", cls: "" };
        const delta = ((current - previous) / previous) * 100;
        const cls = delta > 0 ? "positive" : delta < 0 ? "negative" : "";
        const sign = delta > 0 ? "+" : "";
        return { text: `${sign}${delta.toFixed(1)}%`, cls };
      };

      const fetchFromSources = async (sourceList) => {
        const errors = [];
        for (const source of sourceList) {
          try {
            const response = await fetch(source.url, { cache: "no-store" });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const text = await response.text();
            return { text, sourceLabel: source.label };
          } catch (error) {
            errors.push(`${source.label}: ${error.message}`);
          }
        }
        throw new Error(errors.join(" | "));
      };
      window.fetchFromSources = fetchFromSources;

      const fetchJsonFromSources = async (sourceList) => {
        const { text, sourceLabel } = await fetchFromSources(sourceList);
        try {
          return JSON.parse(text);
        } catch (error) {
          throw new Error(`${sourceLabel}: JSON 解析失败`);
        }
      };

      const uniqueList = (list) => Array.from(new Set(list.filter(Boolean)));

      const applyHealthMetricConfig = (config) => {
        const configMetrics = Array.isArray(config?.metrics) ? config.metrics : [];
        const configMap = new Map();
        configMetrics.forEach((item) => {
          if (!item || !item.valueKey) return;
          const key = String(item.valueKey).trim();
          if (key) configMap.set(key, item);
        });

        const defs = METRIC_DEFS.map((def) => {
          const item = configMap.get(def.valueKey);
          return {
            ...def,
            category: item && item.category ? item.category : "未分类",
            enabled: item ? item.enabled !== false : true,
          };
        });

        const categories =
          Array.isArray(config?.categories) && config.categories.length
            ? config.categories.filter((item) => typeof item === "string" && item.trim())
            : uniqueList(defs.map((def) => def.category));

        return { defs, categories };
      };

      const renderHealthCategoryChips = () => {
        if (!healthCategoryGroup) return;
        healthCategoryGroup.innerHTML = "";
        healthMetricCategories.forEach((label) => {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = `chip${label === activeHealthMetricCategory ? " chip--active" : ""}`;
          chip.textContent = label;
          chip.addEventListener("click", () => {
            if (activeHealthMetricCategory === label) return;
            activeHealthMetricCategory = label;
            renderHealthCategoryChips();
        window.healthMetricDefs = healthMetricDefs;
            applyHealthMetricFilters();
          });
          healthCategoryGroup.appendChild(chip);
        });
      };

      const loadHealthMetricConfig = async () => {
        try {
          const config = await fetchJsonFromSources(HEALTH_METRIC_CONFIG_SOURCES);
          const applied = applyHealthMetricConfig(config);
          healthMetricDefs = applied.defs;
          healthMetricCategories = applied.categories.length
            ? applied.categories
            : uniqueList(applied.defs.map((def) => def.category));
        } catch (error) {
          console.error("加载健康指标配置失败:", error);
          healthMetricDefs = METRIC_DEFS.map((def) => ({
            ...def,
            category: "未分类",
            enabled: true,
          }));
          healthMetricCategories = uniqueList(healthMetricDefs.map((def) => def.category));
        }

        healthMetricCategories = uniqueList(["全部", ...healthMetricCategories]);
        if (healthMetricCategories.includes(DEFAULT_HEALTH_METRIC_CATEGORY)) {
          activeHealthMetricCategory = DEFAULT_HEALTH_METRIC_CATEGORY;
        } else if (!healthMetricCategories.includes(activeHealthMetricCategory)) {
          activeHealthMetricCategory = healthMetricCategories[0];
        }
        renderHealthCategoryChips();
      };

      const applyHealthMetricFilters = () => {
        const rows =
          activeHealthMetricCategory === "全部"
            ? metricRows
            : metricRows.filter((row) => row.category === activeHealthMetricCategory);
        renderMetricTable(rows);
      };

      const parseMetricSeries = (text, valueKey) => {
        if (SleepTimeUtils.isSleepTimeKey(valueKey)) {
          const baseSeries = SleepTimeUtils.parseSeries(text, valueKey, parseCSV, parseDate);
          if (!baseSeries.length) return [];
          const finalSeries = SleepTimeUtils.needsUnwrap(valueKey)
            ? SleepTimeUtils.unwrapSeries(baseSeries, valueKey)
            : baseSeries;
          return finalSeries.sort((a, b) => a.date - b.date);
        }
        const rows = parseCSV(text);
        if (!rows.length) return [];
        const headers = rows[0].map((h) => h.trim().toLowerCase());
        const idxDate = headers.indexOf("date");
        const idxVal = headers.indexOf(valueKey.toLowerCase());
        if (idxDate === -1 || idxVal === -1) return [];
        return rows
          .slice(1)
          .map((cells) => {
            const d = parseDate(cells[idxDate]);
            const v = parseFloat(cells[idxVal]);
            if (!d || Number.isNaN(v)) return null;
            return { date: d, value: v };
          })
          .filter(Boolean)
          .sort((a, b) => a.date - b.date);
      };
      window.parseMetricSeries = parseMetricSeries;
      window.parseCSV = parseCSV;
      window.parseDate = parseDate;

      const avgWindowByDate = (series, days, offsetDays = 0) => {
        if (!series.length) return null;
        const lastDate = series[series.length - 1].date;
        const end = new Date(lastDate);
        end.setHours(23, 59, 59, 999); // 设置为当天的结束时间
        end.setDate(end.getDate() - offsetDays);
        const start = new Date(end);
        start.setDate(start.getDate() - (days - 1));
        start.setHours(0, 0, 0, 0); // 设置为开始日期的开始时间
        const window = series.filter((item) => {
          const itemDate = new Date(item.date);
          itemDate.setHours(0, 0, 0, 0);
          return itemDate >= start && itemDate <= end;
        });
        if (!window.length) return null;
        const total = window.reduce((acc, cur) => acc + cur.value, 0);
        return total / window.length;
      };

      const formatValueWithUnit = (val, unit) => {
        if (val === null || Number.isNaN(val)) return "--";
        const num = Number(val);
        // 体脂率：将小数转换为百分比
        if (unit === "%" && num < 1) {
          return `${(num * 100).toFixed(1)}%`;
        }
        // 空单位：不显示单位
        if (!unit || unit === "") {
          return num.toFixed(2);
        }
        // 3位有效数字：智能格式化（整数或包含小数点）
        const formatted = formatThreeSignificantDigits(num);
        return `${formatted} ${unit}`;
      };

      const formatThreeSignificantDigits = (num) => {
        if (num === 0) return "0";
        const absNum = Math.abs(num);
        // 如果数值 >= 1000，保留整数部分
        if (absNum >= 1000) {
          return Math.round(num).toString();
        }
        // 如果数值 < 1000，保留3位有效数字
        // 如果是整数或接近整数（小数部分小于0.001），显示整数
        if (Math.abs(num % 1) < 0.001) {
          return num.toString();
        }
        // 否则使用3位有效数字
        return num.toPrecision(3);
      };

      const formatDeltaColored = (current, previous) => {
        if (current === null || previous === null || previous === 0) return "—";
        const delta = ((current - previous) / previous) * 100;
        // 变化超过5%才标注颜色，否则使用默认颜色
        const absDelta = Math.abs(delta);
        const cls = absDelta >= 5 ? (delta > 0 ? "delta-pos" : "delta-neg") : "";
        const sign = delta > 0 ? "+" : "";
        return `<span class="${cls}">${sign}${delta.toFixed(1)}%</span>`;
      };

      const formatDeltaSigned = (current, previous) => {
        if (current === null || previous === null || previous === 0) return "—";
        const delta = ((current - previous) / previous) * 100;
        const cls = delta > 0 ? "delta-pos" : delta < 0 ? "delta-neg" : "";
        const sign = delta > 0 ? "+" : "";
        return `<span class="${cls}">${sign}${delta.toFixed(1)}%</span>`;
      };

      const formatClock = (minutes, wrapOverMidnight = false) => {
        if (minutes === null || Number.isNaN(minutes)) return "--";
        let mins = minutes;
        if (wrapOverMidnight && mins >= 24 * 60) {
          mins -= 24 * 60;
        }
        mins = Math.round(mins);
        const hh = String(Math.floor(mins / 60) % 24).padStart(2, "0");
        const mm = String(mins % 60).padStart(2, "0");
        return `${hh}:${mm}`;
      };

      const parseClockToMinutes = (text) => {
        if (!text) return null;
        const cleaned = text.trim();
        if (!cleaned) return null;
        if (cleaned.includes(":")) {
          const parts = cleaned.split(":");
          const hh = parseInt(parts[0], 10);
          const mm = parseInt(parts[1], 10);
          if (Number.isNaN(hh) || Number.isNaN(mm)) return null;
          return hh * 60 + mm;
        }
        const num = parseFloat(cleaned);
        return Number.isNaN(num) ? null : num;
      };

      const SleepTimeUtils = {
        isSleepTimeKey: (valueKey) => valueKey === "bed_time" || valueKey === "wake_time",
        needsUnwrap: (valueKey) => valueKey === "bed_time",
        parseClockToMinutes,
        formatMinutesToClock: (minutes, short = false) => {
          if (minutes === null || Number.isNaN(minutes)) return "";
          const m = ((minutes % 1440) + 1440) % 1440;
          const h = Math.floor(m / 60);
          const mm = Math.round(m % 60);
          return short
            ? `${h}:${String(mm).padStart(2, "0")}`
            : `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
        },
        isDirtyValue: (valueKey, minutes) => {
          if (minutes === null || Number.isNaN(minutes)) return true;
          if (!SleepTimeUtils.isSleepTimeKey(valueKey)) return false;
          return minutes >= 12 * 60 && minutes < 18 * 60;
        },
        computeUnwrapPivot: (values) => {
          if (!values.length) return 720;
          const sorted = values.slice().sort((a, b) => a - b);
          if (sorted.length === 1) return (sorted[0] + 720) % 1440;
          let maxGap = -1;
          let pivot = 720;
          for (let i = 0; i < sorted.length; i += 1) {
            const current = sorted[i];
            const next = sorted[(i + 1) % sorted.length];
            const gap = (next - current + 1440) % 1440;
            if (gap > maxGap) {
              maxGap = gap;
              pivot = (current + gap / 2) % 1440;
            }
          }
          return pivot;
        },
        unwrapValue: (value, pivot) => (value < pivot ? value + 1440 : value),
        parseSeries: (csvText, valueKey, parseCSVFn, parseDateFn) => {
          const rows = parseCSVFn(csvText);
          if (!rows.length) return [];
          const headers = rows[0].map((h) => h.trim().toLowerCase());
          const idxDate = headers.indexOf("date");
          const idxVal = headers.indexOf(valueKey.toLowerCase());
          if (idxDate === -1 || idxVal === -1) return [];
          return rows
            .slice(1)
            .map((cells) => {
              const d = parseDateFn(cells[idxDate]);
              const v = SleepTimeUtils.parseClockToMinutes(cells[idxVal]);
              if (!d || v === null) return null;
              if (SleepTimeUtils.isDirtyValue(valueKey, v)) return null;
              return { date: d, value: v };
            })
            .filter(Boolean)
            .sort((a, b) => a.date - b.date);
        },
        unwrapSeries: (series, valueKey) => {
          if (!series.length || !SleepTimeUtils.needsUnwrap(valueKey)) return series;
          const pivot = SleepTimeUtils.computeUnwrapPivot(series.map((item) => item.value));
          return series.map((item) => ({
            date: item.date,
            value: SleepTimeUtils.unwrapValue(item.value, pivot),
          }));
        },
      };
      window.SleepTimeUtils = SleepTimeUtils;

      const isDirtySleepTime = (valueKey, minutes) => {
        if (minutes === null || Number.isNaN(minutes)) return true;
        if (valueKey !== "bed_time" && valueKey !== "wake_time") return false;
        return minutes >= 12 * 60 && minutes < 18 * 60;
      };

      const parseScheduleSeries = (text, valueKey) => {
        const rows = parseCSV(text);
        if (!rows.length) return [];
        const headers = rows[0].map((h) => h.trim().toLowerCase());
        const idxDate = headers.indexOf("date");
        const idxVal = headers.indexOf(valueKey.toLowerCase());
        if (idxDate === -1 || idxVal === -1) return [];
        return rows
          .slice(1)
          .map((cells) => {
            const d = parseDate(cells[idxDate]);
            const v = parseClockToMinutes(cells[idxVal]);
            if (!d || v === null) return null;
            if (isDirtySleepTime(valueKey, v)) return null;
            return { date: d, value: v };
          })
          .filter(Boolean)
          .sort((a, b) => a.date - b.date);
      };

      const normalizeBedtimeForAverage = (minutes) =>
        minutes < 12 * 60 ? minutes + 24 * 60 : minutes;

      const setHighlightValue = (el, value) => {
        if (!el) return;
        el.textContent = value;
      };

      const setHighlightDelta = (el, current, previous) => {
        if (!el) return;
        el.innerHTML = formatDeltaSigned(current, previous);
      };

      const loadHealthHighlight = async () => {
        // 不再依赖 highlight 元素，仪表盘数据始终加载
        const highlightWindow = 7;
        const highlightOffset = 7;
        const calcAvg = (series) => avgWindowByDate(series, highlightWindow, 0);
        const calcPrev = (series) => avgWindowByDate(series, highlightWindow, highlightOffset);
        const countWindowByDate = (series, days, offsetDays = 0) => {
          if (!series.length) return null;
          const lastDate = series[series.length - 1].date;
          const end = new Date(lastDate);
          end.setHours(23, 59, 59, 999);
          end.setDate(end.getDate() - offsetDays);
          const start = new Date(end);
          start.setDate(start.getDate() - (days - 1));
          start.setHours(0, 0, 0, 0);
          const window = series.filter((item) => {
            const itemDate = new Date(item.date);
            itemDate.setHours(0, 0, 0, 0);
            return itemDate >= start && itemDate <= end;
          });
          if (!window.length) return null;
          return window.reduce(
            (acc, cur) => acc + (cur.value >= EXERCISE_DAY_THRESHOLD_MIN ? 1 : 0),
            0
          );
        };

        try {
          const { text } = await fetchFromSources(BODY_SOURCES);
          const weightSeries = parseMetricSeries(text, "weight_kg");
          const fatSeries = parseMetricSeries(text, "body_fat_pct");

          const weightAvg = calcAvg(weightSeries);
          const weightPrev = calcPrev(weightSeries);
          const fatAvg = calcAvg(fatSeries);
          const fatPrev = calcPrev(fatSeries);

          setHighlightValue(highlightEls.weight, formatValueWithUnit(weightAvg, "kg"));
          setHighlightDelta(highlightEls.weightWow, weightAvg, weightPrev);
          setHighlightValue(highlightEls.bodyFat, formatValueWithUnit(fatAvg, "%"));
          setHighlightDelta(highlightEls.bodyFatWow, fatAvg, fatPrev);
          // 更新可视化方案
          updateVizPanels({ weight: weightAvg, weightPrev: weightPrev });
        } catch (error) {
          console.error("加载体重高亮失败:", error);
        }

        try {
          const { text } = await fetchFromSources(HEALTH_SOURCES);
          const sleepSeries = parseMetricSeries(text, "sleep_hours");
          const sleepAvg = calcAvg(sleepSeries);
          const sleepPrev = calcPrev(sleepSeries);
          setHighlightValue(highlightEls.sleep, formatValueWithUnit(sleepAvg, "小时"));
          setHighlightDelta(highlightEls.sleepWow, sleepAvg, sleepPrev);
          // 更新可视化方案
          updateVizPanels({ sleep: sleepAvg, sleepPrev: sleepPrev });
        } catch (error) {
          console.error("加载睡眠高亮失败:", error);
        }

        try {
          const { text } = await fetchFromSources(SLEEP_SCHEDULE_SOURCES);
          const bedRaw = parseScheduleSeries(text, "bed_time");
          const wakeSeries = parseScheduleSeries(text, "wake_time");
          const bedSeries = bedRaw.map((item) => ({
            ...item,
            value: normalizeBedtimeForAverage(item.value),
          }));

          const bedAvg = calcAvg(bedSeries);
          const bedPrev = calcPrev(bedSeries);
          const wakeAvg = calcAvg(wakeSeries);
          const wakePrev = calcPrev(wakeSeries);

          setHighlightValue(highlightEls.bedTime, formatClock(bedAvg, true));
          setHighlightDelta(highlightEls.bedTimeWow, bedAvg, bedPrev);
          setHighlightValue(highlightEls.wakeTime, formatClock(wakeAvg, false));
          setHighlightDelta(highlightEls.wakeTimeWow, wakeAvg, wakePrev);
          // 更新可视化方案
          updateVizPanels({ bedTime: bedAvg, bedTimePrev: bedPrev, wakeTime: wakeAvg, wakeTimePrev: wakePrev });
        } catch (error) {
          console.error("加载睡眠作息高亮失败:", error);
        }

        try {
          const { text } = await fetchFromSources(HRV_SOURCES);
          const hrvSeries = parseMetricSeries(text, "sdnn_avg");
          const hrvAvg = calcAvg(hrvSeries);
          const hrvPrev = calcPrev(hrvSeries);
          setHighlightValue(highlightEls.hrv, formatValueWithUnit(hrvAvg, "ms"));
          setHighlightDelta(highlightEls.hrvWow, hrvAvg, hrvPrev);
          // 更新可视化方案
          updateVizPanels({ hrv: hrvAvg, hrvPrev: hrvPrev });
        } catch (error) {
          console.error("加载 HRV 高亮失败:", error);
        }

        try {
          const { text } = await fetchFromSources(EXERCISE_SOURCES);
          const exerciseSeries = parseMetricSeries(text, "exercise_time_min");
          const weekCount = countWindowByDate(exerciseSeries, 7, 0);
          const monthCount = countWindowByDate(exerciseSeries, 30, 0);
          setHighlightValue(highlightEls.exerciseWeek, weekCount === null ? "--" : weekCount);
          setHighlightValue(highlightEls.exerciseMonth, monthCount === null ? "--" : monthCount);
          const canRest = (weekCount || 0) >= 5 || (monthCount || 0) >= 21;
          setHighlightValue(highlightEls.exerciseMsg, canRest ? "今天可以休息～" : "今天要继续加油");
          // 更新可视化方案
          updateVizPanels({ exerciseWeek: weekCount, exerciseMonth: monthCount, canRest });
        } catch (error) {
          console.error("加载运动天数高亮失败:", error);
        }
        
        // 加载饮食数据
        try {
          const { text } = await fetchFromSources(DIET_SOURCES);
          const kcalSeries = parseMetricSeries(text, "dietary_kcal");
          const proteinSeries = parseMetricSeries(text, "dietary_protein_g");
          const fatSeries = parseMetricSeries(text, "dietary_fat_g");
          const carbSeries = parseMetricSeries(text, "dietary_carb_g");
          
          const kcalAvg = calcAvg(kcalSeries);
          const proteinAvg = calcAvg(proteinSeries);
          const fatAvg = calcAvg(fatSeries);
          const carbAvg = calcAvg(carbSeries);
          
          updateVizPanels({ kcal: kcalAvg, protein: proteinAvg, fat: fatAvg, carb: carbAvg });
        } catch (error) {
          console.error("加载饮食数据失败:", error);
        }
        
        // 加载能量消耗数据（基础代谢+主动能量）
        try {
          const { text } = await fetchFromSources(ENERGY_SOURCES);
          const basalSeries = parseMetricSeries(text, "basal_energy");
          const activeSeries = parseMetricSeries(text, "active_energy");
          
          const basalAvg = calcAvg(basalSeries);
          const activeAvg = calcAvg(activeSeries);
          const totalBurn = (basalAvg || 0) + (activeAvg || 0);
          
          updateVizPanels({ basalEnergy: basalAvg, activeEnergy: activeAvg, totalBurn: totalBurn });
        } catch (error) {
          console.error("加载能量消耗数据失败:", error);
        }
        
        // 加载睡眠趋势数据（最近7天入睡/起床时间）
        try {
          const { text } = await fetchFromSources(SLEEP_SCHEDULE_SOURCES);
          const rows = text.trim().split("\n").slice(1);
          const scheduleData = rows.map(row => {
            const [date, bed_time, wake_time] = row.split(",");
            return { date, bed_time, wake_time };
          }).filter(d => d.date && d.bed_time && d.wake_time);
          const recent7 = scheduleData.slice(-7);
          updateVizPanels({ sleepScheduleTrend: recent7 });
        } catch (error) {
          console.error("加载睡眠趋势数据失败:", error);
        }
        
        // 设置健康数据更新时间
        try {
          const response = await fetch("health/data/sleep_daily.csv", { method: "HEAD", cache: "no-store" });
          const lastModified = response.headers.get("Last-Modified");
          const healthUpdateEl = document.getElementById("health-update-time");
          if (healthUpdateEl && lastModified) {
            const date = new Date(lastModified);
            healthUpdateEl.textContent = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
          }
        } catch (error) {
          console.error("获取健康数据更新时间失败:", error);
        }
      };

      // 可视化方案数据缓存
      const vizData = { weight: null, weightPrev: null, sleep: null, sleepPrev: null, hrv: null, hrvPrev: null, exerciseWeek: null, exerciseMonth: null, bedTime: null, bedTimePrev: null, wakeTime: null, wakeTimePrev: null, kcal: null, protein: null, fat: null, carb: null, basalEnergy: null, activeEnergy: null, totalBurn: null, sleepScheduleTrend: null };

      const updateVizPanels = (data) => {
        Object.assign(vizData, data);
        const { weight, weightPrev, sleep, sleepPrev, hrv, hrvPrev, exerciseWeek, exerciseMonth, canRest, bedTime, bedTimePrev, wakeTime, wakeTimePrev, kcal, protein, fat, carb, basalEnergy, activeEnergy, totalBurn, sleepScheduleTrend } = vizData;

        // 辅助函数
        const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        const setHtml = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
        const setStyle = (id, prop, val) => { const el = document.getElementById(id); if (el) el.style[prop] = val; };
        const deltaHtml = (cur, prev) => formatDeltaSigned(cur, prev);
        
        // 饮食数据
        if (kcal !== null) {
          setEl("viz1-kcal", Math.round(kcal) + "kcal");
          const kcalPct = Math.max(0, Math.min(100, (kcal / 2200) * 100));
          setStyle("viz1-kcal-bar", "width", kcalPct + "%");
        }
        if (protein !== null) setEl("viz1-protein", Math.round(protein) + "g");
        if (fat !== null) setEl("viz1-fat", Math.round(fat) + "g");
        if (carb !== null) setEl("viz1-carb", Math.round(carb) + "g");
        
        // 能量消耗数据
        if (totalBurn !== null && totalBurn > 0) {
          setEl("viz1-burn", Math.round(totalBurn) + "kcal");
          setEl("viz1-burn-detail", `基础${Math.round(basalEnergy || 0)} + 主动${Math.round(activeEnergy || 0)}`);
          const burnPct = Math.max(0, Math.min(100, (totalBurn / 2500) * 100));
          setStyle("viz1-burn-bar", "width", burnPct + "%");
          
          // 计算热量差
          if (kcal !== null) {
            const calorieDiff = Math.round(kcal - totalBurn);
            const diffColor = calorieDiff > 200 ? "#ef4444" : calorieDiff < -500 ? "#3b82f6" : "#22c55e";
            const diffSign = calorieDiff > 0 ? "+" : "";
            setHtml("viz1-calorie-diff", `<span style="color: ${diffColor}">${diffSign}${calorieDiff}kcal</span>`);
          }
        }
        
        // 营养成分扇形图
        if (protein !== null && fat !== null && carb !== null) {
          const total = protein + fat + carb;
          if (total > 0) {
            const proteinPct = (protein / total) * 100;
            const fatPct = (fat / total) * 100;
            const carbPct = (carb / total) * 100;
            
            const pieProtein = document.getElementById("pie-protein");
            const pieFat = document.getElementById("pie-fat");
            const pieCarb = document.getElementById("pie-carb");
            
            if (pieProtein) pieProtein.setAttribute("stroke-dasharray", `${proteinPct}, 100`);
            if (pieFat) {
              pieFat.setAttribute("stroke-dasharray", `${fatPct}, 100`);
              pieFat.setAttribute("stroke-dashoffset", `-${proteinPct}`);
            }
            if (pieCarb) {
              pieCarb.setAttribute("stroke-dasharray", `${carbPct}, 100`);
              pieCarb.setAttribute("stroke-dashoffset", `-${proteinPct + fatPct}`);
            }
          }
        }

        // 方案一：仪表盘卡片
        if (weight !== null) {
          setEl("viz1-weight", weight.toFixed(1) + "kg");
          setHtml("viz1-weight-delta", deltaHtml(weight, weightPrev));
          const weightPct = Math.max(0, Math.min(100, ((80 - weight) / (80 - 70)) * 100));
          setStyle("viz1-weight-bar", "width", weightPct + "%");
        }
        if (sleep !== null) {
          setEl("viz1-sleep", sleep.toFixed(1) + "h");
          setHtml("viz1-sleep-delta", deltaHtml(sleep, sleepPrev));
          const sleepPct = Math.max(0, Math.min(100, (sleep / 8) * 100));
          setStyle("viz1-sleep-bar", "width", sleepPct + "%");
        }
        if (hrv !== null) {
          setEl("viz1-hrv", hrv.toFixed(0) + "ms");
          setHtml("viz1-hrv-delta", deltaHtml(hrv, hrvPrev));
          const hrvPct = Math.max(0, Math.min(100, (hrv / 50) * 100));
          setStyle("viz1-hrv-bar", "width", hrvPct + "%");
        }
        if (exerciseWeek !== null) {
          setEl("viz1-exercise", exerciseWeek + "天");
          setEl("viz1-exercise-sub", "本月 " + (exerciseMonth || "--") + "天");
          const exPct = Math.max(0, Math.min(100, (exerciseWeek / 4) * 100));
          setStyle("viz1-exercise-bar", "width", exPct + "%");
        }
        // 入睡/起床时间 (bedTime/wakeTime 是分钟数)
        const formatClockFromMinutes = (mins, isBed) => {
          if (mins === null || mins === undefined || Number.isNaN(mins)) return "--";
          let totalMins = Math.round(mins);
          // 入睡时间可能超过24小时（跨午夜），需要减回来
          if (isBed && totalMins >= 24 * 60) totalMins -= 24 * 60;
          const hh = Math.floor(totalMins / 60) % 24;
          const mm = totalMins % 60;
          return String(hh).padStart(2, "0") + ":" + String(mm).padStart(2, "0");
        };
        if (bedTime !== null) {
          setEl("viz1-bedtime", formatClockFromMinutes(bedTime, true));
          setHtml("viz1-bedtime-delta", deltaHtml(bedTime, bedTimePrev));
          // 目标23:00(23*60=1380)，预警00:00(24*60=1440 normalized)，越早越好
          // bedTime 是分钟数，可能是 1380-1560 范围（23:00-02:00跨午夜后+1440）
          const bedPct = Math.max(0, Math.min(100, ((1500 - bedTime) / (1500 - 1380)) * 100));
          setStyle("viz1-bedtime-bar", "width", bedPct + "%");
        }
        if (wakeTime !== null) {
          setEl("viz1-waketime", formatClockFromMinutes(wakeTime, false));
          setHtml("viz1-waketime-delta", deltaHtml(wakeTime, wakeTimePrev));
          // 目标07:00(420)，预警09:00(540)，越早越好
          const wakePct = Math.max(0, Math.min(100, ((540 - wakeTime) / (540 - 420)) * 100));
          setStyle("viz1-waketime-bar", "width", wakePct + "%");
        }
        
        // 同步睡眠模块的数据
        if (sleep !== null) {
          setEl("viz1-sleep2", sleep.toFixed(1) + "h");
          setHtml("viz1-sleep2-delta", deltaHtml(sleep, sleepPrev));
          const sleepPct2 = Math.max(0, Math.min(100, (sleep / 8) * 100));
          setStyle("viz1-sleep2-bar", "width", sleepPct2 + "%");
        }

        // 运动建议规则
        // 规则：综合判断运动天数、HRV、睡眠来给出今日运动建议
        const getExerciseAdvice = () => {
          const weekGoal = 4, monthGoal = 16;
          const sleepOk = sleep !== null && sleep >= EXERCISE_WARN_SLEEP_HOURS;
          const hrvOk = hrv !== null && hrv >= EXERCISE_WARN_HRV;
          const weekOk = exerciseWeek !== null && exerciseWeek >= weekGoal;
          const monthOk = exerciseMonth !== null && exerciseMonth >= monthGoal;
          const bodyReady = sleepOk && hrvOk;

          // 已达标，可以休息
          if (weekOk && monthOk) {
            return { level: "rest", text: "本周本月都达标了，今天可以休息～", color: "#22c55e" };
          }
          // 本周达标但本月未达标
          if (weekOk && !monthOk) {
            if (bodyReady) {
              return { level: "suggest", text: "本周达标但本月还差一点，身体状态不错，可以加练", color: "#3b82f6" };
            }
            return { level: "rest", text: "本周达标，今天休息也行", color: "#22c55e" };
          }
          // 本周未达标
          if (!weekOk) {
            if (!bodyReady) {
              const reason = !sleepOk ? "睡眠不足" : "HRV偏低";
              return { level: "warn", text: `运动未达标，但${reason}，先休息恢复`, color: "#f97316" };
            }
            const gap = weekGoal - (exerciseWeek || 0);
            return { level: "go", text: `本周还差${gap}天，身体状态OK，快起来运动！`, color: "#ef4444" };
          }
          return { level: "unknown", text: "数据加载中...", color: "#64748b" };
        };

        if (exerciseWeek !== null && sleep !== null && hrv !== null) {
          const advice = getExerciseAdvice();
          // 仪表盘运动建议
          setEl("viz1-advice-text", advice.text);
          const adviceBox1 = document.getElementById("viz1-advice");
          if (adviceBox1) adviceBox1.style.borderLeftColor = advice.color;
        }
        
        // 饮食建议 - 考虑热量差
        const getDietAdvice = () => {
          if (weight === null) return { text: "数据加载中...", color: "#64748b" };
          const issues = [];
          let mainAdvice = "";
          let color = "#22c55e";
          
          // 体重判断
          if (weight > 80) {
            issues.push("体重超过预警值80kg");
            color = "#ef4444";
          } else if (weight > 75) {
            issues.push("体重略高于目标");
            color = "#f97316";
          }
          
          // 热量差判断
          if (kcal !== null && totalBurn !== null && totalBurn > 0) {
            const calorieDiff = kcal - totalBurn;
            if (weight > 75) {
              // 需要减重
              if (calorieDiff > 0) {
                issues.push("热量盈余不利于减重");
                mainAdvice = "建议制造300-500kcal热量缺口";
              } else if (calorieDiff > -300) {
                mainAdvice = "热量缺口不够，可以再少吃一点或多运动";
              } else if (calorieDiff < -800) {
                mainAdvice = "热量缺口过大，注意营养均衡";
                color = "#f97316";
              } else {
                mainAdvice = "热量缺口合理，继续保持";
                color = "#22c55e";
              }
            } else {
              // 维持体重
              if (Math.abs(calorieDiff) <= 200) {
                mainAdvice = "热量平衡，体重稳定";
              } else if (calorieDiff > 200) {
                mainAdvice = "热量略有盈余，注意控制";
              } else {
                mainAdvice = "热量略有缺口，可适当补充";
              }
            }
          } else {
            mainAdvice = weight > 75 ? "建议控制饮食热量" : "保持均衡饮食";
          }
          
          return { 
            text: issues.length > 0 ? issues.join("，") + "。" + mainAdvice : mainAdvice, 
            color 
          };
        };
        if (weight !== null) {
          const dietAdvice = getDietAdvice();
          setEl("diet-advice-text", dietAdvice.text);
          const dietBox = document.getElementById("diet-advice");
          if (dietBox) dietBox.style.borderLeftColor = dietAdvice.color;
        }
        
        // 睡眠建议 - 重点考虑入睡时间，强调早睡早起
        const getSleepAdvice = () => {
          if (sleep === null || bedTime === null) return { text: "数据加载中...", color: "#64748b" };
          const issues = [];
          let mainAdvice = "";
          let color = "#22c55e";
          
          // 入睡时间判断（最重要）- bedTime是分钟数，可能超过1440（跨午夜）
          const bedHour = bedTime >= 1440 ? (bedTime - 1440) / 60 : bedTime / 60;
          const isLateBed = bedTime > 1440 || bedHour >= 24 || (bedHour >= 0 && bedHour < 6); // 00:00后入睡
          const isVeryLateBed = bedTime > 1500 || (bedHour >= 1 && bedHour < 6); // 01:00后入睡
          
          if (isVeryLateBed) {
            issues.push("入睡时间太晚（超过凌晨1点）");
            mainAdvice = "请务必早睡！长期熬夜伤身体";
            color = "#ef4444";
          } else if (isLateBed) {
            issues.push("入睡时间偏晚（超过午夜）");
            mainAdvice = "建议23点前入睡，早睡早起身体好";
            color = "#f97316";
          }
          
          // 睡眠时长判断
          if (sleep < 6) {
            issues.push("睡眠时长不足6小时");
            if (!mainAdvice) mainAdvice = "睡眠严重不足，影响恢复和免疫力";
            color = "#ef4444";
          } else if (sleep < 7) {
            if (!issues.length) issues.push("睡眠时长略少");
            if (!mainAdvice) mainAdvice = "建议保证7-8小时睡眠";
            if (color === "#22c55e") color = "#f97316";
          }
          
          // 起床时间判断
          if (wakeTime > 600) { // 10:00后
            issues.push("起床太晚");
            if (!mainAdvice) mainAdvice = "建议7-8点起床，保持规律作息";
            if (color === "#22c55e") color = "#f97316";
          }
          
          if (issues.length === 0) {
            return { text: "睡眠状态良好，早睡早起，继续保持！", color: "#22c55e" };
          }
          
          return { text: issues.join("，") + "。" + mainAdvice, color };
        };
        if (sleep !== null) {
          const sleepAdvice = getSleepAdvice();
          setEl("sleep-advice-text", sleepAdvice.text);
          const sleepBox = document.getElementById("sleep-advice");
          if (sleepBox) sleepBox.style.borderLeftColor = sleepAdvice.color;
        }
        
        // 睡眠趋势图渲染 - 垂直时间轴样式
        if (sleepScheduleTrend && sleepScheduleTrend.length > 0) {
          const chartContainer = document.getElementById("sleep-trend-chart");
          const labelsContainer = document.getElementById("sleep-trend-labels");
          const titleEl = document.getElementById("sleep-trend-title");
          if (chartContainer && labelsContainer) {
            // 更新标题显示日期范围
            const firstDate = new Date(sleepScheduleTrend[0].date);
            const lastDate = new Date(sleepScheduleTrend[sleepScheduleTrend.length - 1].date);
            if (titleEl) {
              titleEl.textContent = `${firstDate.getFullYear()}年${firstDate.getMonth() + 1}月${firstDate.getDate()}日至${lastDate.getDate()}日`;
            }
            
            // 时间轴范围：21:00 到 11:00（跨午夜，共14小时）
            const timeMin = 21 * 60; // 21:00 = 1260分钟
            const timeMax = (24 + 11) * 60; // 11:00 next day = 2100分钟
            const totalRange = timeMax - timeMin; // 840分钟
            
            // 解析时间字符串为分钟数（相对于当天0点）
            const parseTimeToMins = (timeStr) => {
              const [hh, mm] = timeStr.split(":").map(Number);
              return hh * 60 + mm;
            };
            
            // 将时间转换为图表位置（百分比）
            const timeToPosition = (mins, isBed) => {
              let adjustedMins = mins;
              // 入睡时间：如果在0-21点之间，说明是跨午夜后的时间，需要+1440
              if (isBed && mins < timeMin) adjustedMins = mins + 24 * 60;
              // 起床时间：如果在0-11点之间，说明是第二天，需要+1440
              if (!isBed && mins < 12 * 60) adjustedMins = mins + 24 * 60;
              return ((adjustedMins - timeMin) / totalRange) * 100;
            };
            
            chartContainer.innerHTML = sleepScheduleTrend.map((d, i) => {
              const bedMins = parseTimeToMins(d.bed_time);
              const wakeMins = parseTimeToMins(d.wake_time);
              
              const bedPos = timeToPosition(bedMins, true);
              const wakePos = timeToPosition(wakeMins, false);
              const height = wakePos - bedPos;
              
              // 只使用3种颜色：深睡(#6366f1)、浅睡(#60a5fa)、清醒(#f97316)
              // 整体使用深睡+浅睡渐变，模拟睡眠周期
              return `<div style="flex: 1; position: relative; height: 100%;">
                <div style="position: absolute; top: ${bedPos}%; height: ${Math.max(height, 2)}%; width: 100%; background: linear-gradient(180deg, #6366f1 0%, #60a5fa 30%, #6366f1 50%, #60a5fa 70%, #6366f1 100%); border-radius: 3px; opacity: 0.85;"></div>
              </div>`;
            }).join("");
            
            // 渲染底部日期标签
            labelsContainer.innerHTML = sleepScheduleTrend.map(d => {
              const date = new Date(d.date);
              const dayNames = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
              return `<span>${dayNames[date.getDay()]}</span>`;
            }).join("");
          }
        }
      };

      const renderMetricTable = (rows) => {
        metricTableBody.innerHTML = "";
        if (!rows.length) {
          const tr = document.createElement("tr");
          const td = document.createElement("td");
          td.colSpan = 6;
          td.textContent = "暂无数据";
          tr.appendChild(td);
          metricTableBody.appendChild(tr);
          return;
        }
        rows.forEach((row) => {
          const tr = document.createElement("tr");

          const nameCell = document.createElement("td");
          nameCell.textContent = row.label;
          nameCell.dataset.metricLabel = row.label;
          nameCell.classList.add("metric-link");
          nameCell.title = "点击查看趋势图";
          tr.appendChild(nameCell);

          const weekCell = document.createElement("td");
          weekCell.textContent = row.weekAvg;
          tr.appendChild(weekCell);

          const wowCell = document.createElement("td");
          wowCell.innerHTML = row.wow;
          tr.appendChild(wowCell);

          const momCell = document.createElement("td");
          momCell.innerHTML = row.mom;
          tr.appendChild(momCell);

          const yoyCell = document.createElement("td");
          yoyCell.innerHTML = row.yoy;
          tr.appendChild(yoyCell);


          metricTableBody.appendChild(tr);
        });
      };

      const loadMetricTable = async () => {
        try {
          if (healthStatus) {
            healthStatus.textContent = "正在加载健康数据...";
          }
          const rows = [];
          for (const def of healthMetricDefs) {
            if (def.enabled === false) continue;
            const category = def.category || "未分类";
            try {
              const { text } = await fetchFromSources(def.sources);
              const series = parseMetricSeries(text, def.valueKey);
              if (!series.length) {
                rows.push({
                  label: def.label,
                  category,
                  weekAvg: "--",
                  wow: "—",
                  mom: "—",
                  yoy: "—",
                });
                continue;
              }
              
              // 统一使用原始数据直接计算周日均值（7日滚动平均仅用于趋势图）
              const avg7 = avgWindowByDate(series, 7, 0);
              const prev7 = avgWindowByDate(series, 7, 7);
              const prev30 = avgWindowByDate(series, 30, 7);
              const avg365 = avgWindowByDate(series, 365, 0);

              rows.push({
                label: def.label,
                category,
                weekAvg: formatValueWithUnit(avg7, def.unit),
                wow: formatDeltaColored(avg7, prev7),
                mom: formatDeltaColored(avg7, prev30),
                yoy: formatDeltaColored(avg7, avg365),
              });
            } catch (error) {
              console.error(`加载指标 ${def.label} 失败:`, error);
              rows.push({
                label: def.label,
                category,
                weekAvg: "加载失败",
                wow: "—",
                mom: "—",
                yoy: "—",
              });
            }
          }
          metricRows = rows;
          applyHealthMetricFilters();
          if (healthStatus) {
            healthStatus.textContent = "健康数据已加载";
          }
        } catch (error) {
          console.error("加载指标表格失败:", error);
          metricRows = [];
          renderMetricTable([]);
          if (healthStatus) {
            healthStatus.textContent = "健康数据加载失败";
          }
        }
      };

      const initHealthMetricTable = async () => {
        await loadHealthMetricConfig();
        await loadMetricTable();
      };


      const fetchCSVSource = async () => {
        const errors = [];
        for (const source of CSV_SOURCES) {
          try {
            const response = await fetch(source.url, { cache: "no-store" });
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}`);
            }
            const text = await response.text();
            const lastModified = await resolveLastModified(response, source.url);
            return { text, lastModified, sourceLabel: source.label };
          } catch (error) {
            errors.push(`${source.label}: ${error.message}`);
          }
        }
        throw new Error(errors.join(" | "));
      };

      const loadCSV = async () => {
        if (statusEl) statusEl.textContent = "正在加载数据...";
        if (updateTimeEl) updateTimeEl.textContent = " 正在获取...";
        try {
          const { text, lastModified, sourceLabel } = await fetchCSVSource();
          if (lastModified) {
            if (updateTimeEl) {
              updateTimeEl.textContent = formatUpdateTime(lastModified);
              updateTimeEl.title = `${lastModified.toString()} · 来源：${sourceLabel}`;
            }
          } else {
            if (updateTimeEl) {
              updateTimeEl.textContent = ` 无可用数据（来源：${sourceLabel})`;
              updateTimeEl.removeAttribute("title");
            }
          }
          const rows = parseCSV(text);
          if (!rows.length) {
            if (statusEl) statusEl.textContent = "CSV 文件为空";
            records = [];
            renderBody([]);
            return;
          }
          records = buildRecords(rows);
          window.records = records;
          applyFilters();
          renderEntertainmentTagCloud();
        } catch (error) {
          console.error(error);
          if (statusEl) statusEl.textContent = "加载失败，请确认 CSV 文件路径正确";
          records = [];
          renderBody([]);
        }
      };

      renderCategoryChips();
      initLimitSelect();
      ensureLimitValue();
      renderHeader();
      renderBody([]);
      initHealthMetricTable();
 loadHealthHighlight();
 loadCSV();

      window.records = records;
      window.healthMetricDefs = healthMetricDefs;

// --- UI helpers for modals, tips, and entertainment tab ---
const bindInfoPopup = (triggerId, popupId, closeId, overlayId) => {
  const trigger = document.getElementById(triggerId);
  const popup = document.getElementById(popupId);
  const close = document.getElementById(closeId);
  const overlay = document.getElementById(overlayId);
  if (!trigger || !popup || !close || !overlay) return;

  const open = () => {
    popup.style.display = "block";
    overlay.style.display = "block";
    document.body.classList.add("modal-open");
  };
  const closeFn = () => {
    popup.style.display = "none";
    overlay.style.display = "none";
    document.body.classList.remove("modal-open");
  };

  trigger.addEventListener("click", open);
  close.addEventListener("click", closeFn);
  overlay.addEventListener("click", closeFn);
};

bindInfoPopup("exercise-advice-trigger", "exercise-advice-popup", "exercise-advice-close", "exercise-advice-overlay");
bindInfoPopup("diet-advice-trigger", "diet-advice-popup", "diet-advice-close", "diet-advice-overlay");
bindInfoPopup("sleep-advice-trigger", "sleep-advice-popup", "sleep-advice-close", "sleep-advice-overlay");

// 睡眠建议的 ? 按钮绑定
const sleepInfoTrigger = document.getElementById("sleep-info-trigger");
const sleepInfoModal = document.getElementById("sleep-info-modal");
const sleepInfoClose = document.getElementById("sleep-info-close");
if (sleepInfoTrigger && sleepInfoModal && sleepInfoClose) {
  sleepInfoTrigger.addEventListener("click", () => {
    sleepInfoModal.classList.add("modal--open");
    document.body.classList.add("modal-open");
  });
  sleepInfoClose.addEventListener("click", () => {
    sleepInfoModal.classList.remove("modal--open");
    document.body.classList.remove("modal-open");
  });
  sleepInfoModal.addEventListener("click", (event) => {
    if (event.target === sleepInfoModal) {
      sleepInfoModal.classList.remove("modal--open");
      document.body.classList.remove("modal-open");
    }
  });
}

const chartModal = {
  modal: document.getElementById("chart-modal"),
  title: document.getElementById("modal-title"),
  chart: document.getElementById("modal-chart"),
  image: document.getElementById("modal-image"),
  close: document.getElementById("modal-close"),
};

let currentEChart = null;
let currentResizeHandler = null;

const disposeEChart = () => {
  if (currentResizeHandler) {
    window.removeEventListener("resize", currentResizeHandler);
    currentResizeHandler = null;
  }
  if (currentEChart) {
    currentEChart.dispose();
    currentEChart = null;
  }
};

const openChartModal = () => {
  if (!chartModal.modal) return;
  chartModal.modal.classList.add("modal--open");
  document.body.classList.add("modal-open");
};

const closeChartModal = () => {
  if (!chartModal.modal) return;
  disposeEChart();
  chartModal.modal.classList.remove("modal--open");
  document.body.classList.remove("modal-open");
};

if (chartModal.close) {
  chartModal.close.addEventListener("click", closeChartModal);
}
if (chartModal.modal) {
  chartModal.modal.addEventListener("click", (event) => {
    if (event.target === chartModal.modal) closeChartModal();
  });
}

const GUIDE_LINES = {
  sleep_hours: [
    { value: 8, label: "目标 8h", color: "#22d3ee" },
    { value: 6, label: "预警 6h", color: "#f97316" },
  ],
  bed_time: [
    { value: 23 * 60, label: "目标 23:00", color: "#22d3ee" },
    { value: 24 * 60, label: "预警 00:00", color: "#f97316" },
  ],
  wake_time: [
    { value: 7 * 60, label: "目标 7:00", color: "#22d3ee" },
    { value: 9 * 60, label: "预警 9:00", color: "#f97316" },
  ],
};

const computeRollingAvg = (series, windowSize = 7) => {
  const out = [];
  const queue = [];
  let sum = 0;
  series.forEach((point) => {
    queue.push(point.value);
    sum += point.value;
    if (queue.length > windowSize) {
      sum -= queue.shift();
    }
    out.push({ date: point.date, value: sum / queue.length });
  });
  return out;
};

const buildSeries = (def, text) => {
  const isTime = SleepTimeUtils.isSleepTimeKey(def.valueKey);
  let baseSeries;
  if (isTime) {
    baseSeries = SleepTimeUtils.parseSeries(text, def.valueKey, parseCSV, parseDate);
  } else {
    baseSeries = parseMetricSeries(text, def.valueKey);
  }
  if (!baseSeries.length) return { series: [], isTime, pivot: null };
  let finalSeries = baseSeries;
  let pivot = null;
  if (isTime && SleepTimeUtils.needsUnwrap(def.valueKey)) {
    pivot = SleepTimeUtils.computeUnwrapPivot(baseSeries.map((item) => item.value));
    finalSeries = baseSeries.map((item) => ({
      date: item.date,
      value: SleepTimeUtils.unwrapValue(item.value, pivot),
    }));
  }
  finalSeries.sort((a, b) => a.date - b.date);
  return { series: finalSeries, isTime, pivot };
};

const renderTrendChart = async (metricLabel) => {
  const baseDefs = typeof healthMetricDefs === "undefined" ? METRIC_DEFS : healthMetricDefs;
  const extraDefs = typeof HIGHLIGHT_EXTRA_DEFS === "undefined" ? [] : HIGHLIGHT_EXTRA_DEFS;
  const metricDef = [...baseDefs, ...extraDefs].find((def) => def.label === metricLabel);
  if (!metricDef || !chartModal.chart) return;
  if (!window.echarts) {
    console.warn("ECharts not loaded.");
    return;
  }

  try {
    const { text } = await fetchFromSources(metricDef.sources);
    const { series, isTime, pivot } = buildSeries(metricDef, text);
    if (!series.length) return;

    const lastDate = series[series.length - 1].date;
    const monthStart = new Date(lastDate.getTime() - 89 * 86400000);
    const yearStart = new Date(lastDate.getTime() - 364 * 86400000);
    const topSeries = series.filter((p) => p.date >= monthStart);
    const bottomSeries = computeRollingAvg(series.filter((p) => p.date >= yearStart), 7);

    const formatYAxis = (val) =>
      isTime ? SleepTimeUtils.formatMinutesToClock(val, true) : val;
    const guideLines = GUIDE_LINES[metricDef.valueKey] || [];
    const markLineData = guideLines.map((line) => {
      const rawValue =
        isTime && SleepTimeUtils.needsUnwrap(metricDef.valueKey) && pivot !== null
          ? SleepTimeUtils.unwrapValue(line.value, pivot)
          : line.value;
      return {
        yAxis: rawValue,
        lineStyle: { color: line.color, type: "dashed" },
        label: { formatter: line.label, color: line.color },
      };
    });

    const option = {
      backgroundColor: "#0f172a",
      grid: [
        { left: 60, right: 30, top: 50, height: "35%" },
        { left: 60, right: 30, top: "55%", height: "35%" },
      ],
      tooltip: {
        trigger: "axis",
        valueFormatter: (value) =>
          isTime ? SleepTimeUtils.formatMinutesToClock(value) : value,
      },
      xAxis: [
        { type: "time", gridIndex: 0, axisLine: { lineStyle: { color: "#334155" } } },
        { type: "time", gridIndex: 1, axisLine: { lineStyle: { color: "#334155" } } },
      ],
      yAxis: [
        { type: "value", gridIndex: 0, axisLabel: { formatter: formatYAxis } },
        { type: "value", gridIndex: 1, axisLabel: { formatter: formatYAxis } },
      ],
      series: [
        {
          name: "近3个月分天",
          type: "line",
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: topSeries.map((p) => [p.date, p.value]),
          symbol: "circle",
          symbolSize: 4,
          markLine: markLineData.length ? { data: markLineData } : undefined,
        },
        {
          name: "近1年7日均值",
          type: "line",
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: bottomSeries.map((p) => [p.date, p.value]),
          symbol: "none",
          areaStyle: { opacity: 0.3 },
        },
      ],
    };

    if (chartModal.title) chartModal.title.textContent = metricDef.label;
    chartModal.chart.style.display = "block";
    if (chartModal.image) chartModal.image.style.display = "none";
    openChartModal();
    if (!currentEChart) {
      currentEChart = window.echarts.init(chartModal.chart);
    }
    currentEChart.clear();
    currentEChart.setOption(option);
    if (currentResizeHandler) {
      window.removeEventListener("resize", currentResizeHandler);
    }
    currentResizeHandler = () => {
      if (currentEChart) currentEChart.resize();
    };
    window.addEventListener("resize", currentResizeHandler);
  } catch (error) {
    console.error("Render trend chart failed:", error);
  }
};

if (metricTableBody) {
  metricTableBody.addEventListener("click", (event) => {
    const cell = event.target.closest(".metric-link");
    if (!cell) return;
    const label = cell.dataset.metricLabel || cell.textContent;
    if (!label) return;
    renderTrendChart(label.trim());
  });
}

const METRIC_KEY_TO_LABEL = {
  exercise_time_min: "锻炼时长",
  sleep_hours: "睡眠时长",
  weight_kg: "体重",
  bed_time: "入睡时间",
  wake_time: "起床时间",
  sdnn_avg: "HRV-SDNN均值",
  body_fat_pct: "体脂率",
  resting_hr_avg: "静息心率",
  steps: "步数",
  hr_avg: "心率均值",
};

document.querySelectorAll(".viz-card[data-metric]").forEach((card) => {
  card.addEventListener("click", () => {
    const metricKey = card.dataset.metric;
    const metricLabel = METRIC_KEY_TO_LABEL[metricKey];
    if (metricLabel) {
      renderTrendChart(metricLabel);
    }
  });
});

const exerciseCalendarState = {
  loaded: false,
  byDate: new Map(),
};
let exerciseDetailBound = false;

const formatDateKey = (date) => {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
};

const showExerciseDetail = (dateKey, value) => {
  const popup = document.getElementById("exercise-detail-popup");
  const overlay = document.getElementById("exercise-detail-overlay");
  const dateEl = document.getElementById("exercise-detail-date");
  const contentEl = document.getElementById("exercise-detail-content");
  if (!popup || !overlay || !dateEl || !contentEl) return;
  dateEl.textContent = dateKey;
  contentEl.textContent = value
    ? `运动时长：${Math.round(value)} 分钟`
    : "当天未记录运动";
  popup.style.display = "block";
  overlay.style.display = "block";
  document.body.classList.add("modal-open");

  if (!exerciseDetailBound) {
    const closeBtn = document.getElementById("exercise-detail-close");
    const close = () => {
      popup.style.display = "none";
      overlay.style.display = "none";
      document.body.classList.remove("modal-open");
    };
    if (closeBtn) closeBtn.addEventListener("click", close);
    overlay.addEventListener("click", close);
    exerciseDetailBound = true;
  }
};

const loadExerciseCalendar = async () => {
  const grid = document.getElementById("cal-v1-grid");
  if (!grid) return;
  try {
    const { text } = await fetchFromSources(EXERCISE_SOURCES);
    const series = parseMetricSeries(text, "exercise_time_min");
    exerciseCalendarState.byDate = new Map();
    series.forEach(({ date, value }) => {
      exerciseCalendarState.byDate.set(formatDateKey(date), value);
    });
    const endDate = series.length ? series[series.length - 1].date : new Date();
    const startDate = new Date(endDate);
    startDate.setDate(startDate.getDate() - 27);
    const days = [];
    for (let i = 0; i < 28; i += 1) {
      const d = new Date(startDate);
      d.setDate(startDate.getDate() + i);
      const key = formatDateKey(d);
      const value = exerciseCalendarState.byDate.get(key) || 0;
      days.push({ key, value });
    }
    grid.innerHTML = days
      .map(({ key, value }) => {
        const intensity = Math.min(1, value / 60);
        const opacity = value ? 0.2 + intensity * 0.6 : 0.08;
        const bg = `rgba(34, 197, 94, ${opacity.toFixed(2)})`;
        return `<button data-date="${key}" data-value="${value}" style="height: 26px; border-radius: 6px; border: 1px solid #334155; background: ${bg}; color: #f8fafc; font-size: 10px; cursor: pointer;">${key.slice(8)}</button>`;
      })
      .join("");

    grid.querySelectorAll("[data-date]").forEach((cell) => {
      cell.addEventListener("click", () => {
        const key = cell.dataset.date;
        const value = Number(cell.dataset.value || "0");
        showExerciseDetail(key, value);
      });
    });

    exerciseCalendarState.loaded = true;
  } catch (error) {
    console.error("加载运动日历失败:", error);
    grid.innerHTML = '<div style="color: #94a3b8; font-size: 12px;">加载失败</div>';
  }
};

const toggleExerciseCalendar = () => {
  const panel = document.getElementById("exercise-calendar-v1");
  const icon = document.getElementById("calendar-toggle-icon");
  if (!panel) return;
  const isOpen = panel.style.display !== "none";
  panel.style.display = isOpen ? "none" : "block";
  if (icon) icon.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
  if (!isOpen && !exerciseCalendarState.loaded) {
    loadExerciseCalendar();
  }
};

window.toggleExerciseCalendar = toggleExerciseCalendar;

function renderEntertainmentTagCloud() {
  const tagsContainer = document.getElementById("ent-tags");
  const videoList = document.getElementById("ent-video-list");
  if (!tagsContainer || !videoList) return;
  if (!records || !records.length) return;

  let categoryOrder = ["超优质", "历史区", "创意区", "运动区", "游戏区", "影视综", "数分"];
  const config = window.KDM_CONFIG && window.KDM_CONFIG.bilibiliAuthors;
  if (config) {
    categoryOrder = Object.keys(config).filter((key) => !key.startsWith("_"));
  }

  const categoryCount = {};
  records.forEach((r) => {
    const cat = r.category || "其他";
    categoryCount[cat] = (categoryCount[cat] || 0) + 1;
  });

  const sortedCats = [];
  categoryOrder.forEach((cat) => {
    sortedCats.push([cat, categoryCount[cat] || 0]);
  });
  Object.entries(categoryCount).forEach(([cat, count]) => {
    if (!categoryOrder.includes(cat)) sortedCats.push([cat, count]);
  });

  let activeTag =
    sortedCats.find(([cat]) => cat === "超优质")?.[0] ||
    sortedCats[0]?.[0] ||
    "全部";

  const renderTags = () => {
    tagsContainer.innerHTML = sortedCats
      .map(([cat, count]) => {
        const isActive = cat === activeTag;
        const style = isActive
          ? "padding: 6px 14px; background: #2563eb; border-radius: 16px; font-size: 13px; font-weight: 600; color: #fff; cursor: pointer; border: none;"
          : "padding: 6px 14px; background: transparent; border: 1px solid #475569; border-radius: 16px; font-size: 13px; color: #94a3b8; cursor: pointer;";
        return `<span data-cat="${cat}" style="${style}">${cat}<span style="margin-left: 4px; opacity: 0.7; font-size: 11px;">${count}</span></span>`;
      })
      .join("");
  };

  const renderVideos = () => {
    const limit = parseInt(document.getElementById("limit-input")?.value || "1", 10);
    const filtered = records.filter((r) => (r.category || "其他") === activeTag);
    const authorCounts = new Map();
    const videos = [];

    filtered.forEach((r) => {
      if (!r.author || !r.title) return;
      const used = authorCounts.get(r.author) || 0;
      if (used >= limit) return;
      authorCounts.set(r.author, used + 1);
      videos.push(r);
    });

    videos.sort((a, b) => (b._timestamp || 0) - (a._timestamp || 0));

    if (!videos.length) {
      videoList.innerHTML = '<div style="text-align: center; padding: 20px; color: #64748b;">暂无视频</div>';
      return;
    }

    videoList.innerHTML = videos
      .slice(0, 20)
      .map((v, idx) => {
        const bg = idx % 2 === 0 ? "rgba(59, 130, 246, 0.08)" : "rgba(59, 130, 246, 0.03)";
        return `<a href="${v.url || "#"}" target="_blank" rel="noopener" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: ${bg}; border-radius: 6px; text-decoration: none; transition: background 0.2s;">
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 13px; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${v.title}</div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">${v.author} · ${v.publish_date || ""}</div>
          </div>
        </a>`;
      })
      .join("");
  };

  renderTags();
  renderVideos();

  tagsContainer.addEventListener("click", (event) => {
    const tag = event.target.closest("[data-cat]");
    if (!tag) return;
    activeTag = tag.dataset.cat;
    renderTags();
    renderVideos();
  });

  const limitSelect = document.getElementById("limit-input");
  if (limitSelect) {
    limitSelect.addEventListener("change", renderVideos);
  }
}
