window.KDMTabs = window.KDMTabs || {};

(() => {
  const DATA_URL = "health/workspace_data.json";

  const qs = (id) => document.getElementById(id);
  const updatedAtEl = qs("workspace-updated-at");
  const modelsUpdatedEl = qs("workspace-models-updated");
  const modelsEl = qs("workspace-models");
  const taskSummaryEl = qs("workspace-task-summary");

  const columns = {
    todo: {
      list: qs("workspace-list-todo"),
      count: qs("workspace-count-todo"),
      emptyText: "暂无待办任务",
    },
    in_progress: {
      list: qs("workspace-list-in-progress"),
      count: qs("workspace-count-in-progress"),
      emptyText: "暂无进行中任务",
    },
    done: {
      list: qs("workspace-list-done"),
      count: qs("workspace-count-done"),
      emptyText: "暂无已完成任务",
    },
  };

  const PRIORITY_LABELS = {
    low: "低优先级",
    medium: "中优先级",
    high: "高优先级",
  };

  const formatUpdatedAt = (raw) => {
    if (!raw) return "--";
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return raw;
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const dd = String(date.getDate()).padStart(2, "0");
    const hh = String(date.getHours()).padStart(2, "0");
    const min = String(date.getMinutes()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
  };

  const formatTime = (raw) => {
    if (!raw) return "--";
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return raw;
    const hh = String(date.getHours()).padStart(2, "0");
    const min = String(date.getMinutes()).padStart(2, "0");
    return `${hh}:${min}`;
  };

  const formatReset = (minutes) => {
    const total = Number(minutes);
    if (!Number.isFinite(total) || total < 0) return "--";
    const hours = Math.floor(total / 60);
    const mins = Math.round(total % 60);
    if (hours && mins) return `${hours}h${mins}m`;
    if (hours) return `${hours}h`;
    return `${mins}m`;
  };

  const clampPercent = (value) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return 0;
    return Math.min(100, Math.max(0, Math.round(num)));
  };

  const getQuotaClass = (percent) => {
    if (percent > 80) return "workspace-progress--high";
    if (percent >= 50) return "workspace-progress--mid";
    return "workspace-progress--low";
  };

  const getStatusClass = (status) => {
    if (status === "warning") return "is-warning";
    if (status === "exhausted") return "is-exhausted";
    if (status === "ok") return "is-ok";
    return "";
  };

  const renderEmpty = (target, message) => {
    if (!target) return;
    target.innerHTML = `<div class="workspace-empty">${message}</div>`;
  };

  const renderModels = (models) => {
    if (!modelsEl) return;
    if (!Array.isArray(models) || !models.length) {
      renderEmpty(modelsEl, "暂无模型数据");
      return;
    }
    modelsEl.innerHTML = models
      .map((model) => {
        const percent = clampPercent(model.quota_percent);
        const name = model.name || "--";
        const reset = formatReset(model.reset_in_minutes);
        const quotaClass = getQuotaClass(percent);
        const statusClass = getStatusClass(model.status);
        return `
          <div class="workspace-model ${statusClass}">
            <div class="workspace-model__name">${name}</div>
            <div class="workspace-model__bar">
              <span class="workspace-model__fill ${quotaClass}" style="width: ${percent}%"></span>
            </div>
            <div class="workspace-model__meta">
              <span class="workspace-model__percent">${percent}%</span>
              <span>重置: ${reset}</span>
            </div>
          </div>
        `;
      })
      .join("");
  };

  const renderTasks = (tasks) => {
    const grouped = { todo: [], in_progress: [], done: [] };
    const list = Array.isArray(tasks) ? tasks : [];
    list.forEach((task) => {
      if (!task || !grouped[task.status]) return;
      grouped[task.status].push(task);
    });

    const total = list.length;
    const doneCount = grouped.done.length;
    if (taskSummaryEl) {
      taskSummaryEl.textContent = `${doneCount}/${total} 已完成`;
    }

    Object.entries(columns).forEach(([status, info]) => {
      if (!info.list || !info.count) return;
      const items = grouped[status] || [];
      info.count.textContent = String(items.length);
      if (!items.length) {
        renderEmpty(info.list, info.emptyText);
        return;
      }
      info.list.innerHTML = items
        .map((task) => {
          const title = task.title || "--";
          const idTag = task.id ? `<span class="workspace-task__id">#${task.id}</span>` : "";
          const projectTag = task.project ? `<span class="workspace-task__project">${task.project}</span>` : "";
          const priorityLabel = PRIORITY_LABELS[task.priority];
          const priorityTag = priorityLabel
            ? `<span class="workspace-task__badge workspace-task__badge--${task.priority}">${priorityLabel}</span>`
            : "";
          const meta = [idTag, projectTag, priorityTag].filter(Boolean).join("");
          const metaHtml = meta ? `<div class="workspace-task__meta">${meta}</div>` : "";
          return `
            <div class="workspace-task">
              <div class="workspace-task__title">${title}</div>
              ${metaHtml}
            </div>
          `;
        })
        .join("");
    });
  };

  const fetchWorkspaceData = async () => {
    try {
      const fetchText =
        window.KDMDataLoader && typeof window.KDMDataLoader.fetchText === "function"
          ? window.KDMDataLoader.fetchText
          : async (url) => {
              const response = await fetch(url, { cache: "no-store" });
              if (!response.ok) throw new Error(`Request failed: ${response.status}`);
              return response.text();
            };
      const text = await fetchText(DATA_URL);
      return JSON.parse(text);
    } catch (error) {
      console.error("加载工作台数据失败:", error);
      return null;
    }
  };

  const boot = async () => {
    const data = await fetchWorkspaceData();
    if (!data) {
      if (updatedAtEl) updatedAtEl.textContent = "加载失败";
      if (modelsUpdatedEl) modelsUpdatedEl.textContent = "--";
      renderEmpty(modelsEl, "模型数据加载失败");
      Object.values(columns).forEach((info) => {
        renderEmpty(info.list, "任务数据加载失败");
        if (info.count) info.count.textContent = "0";
      });
      if (taskSummaryEl) taskSummaryEl.textContent = "0/0 已完成";
      return;
    }

    if (updatedAtEl) updatedAtEl.textContent = formatUpdatedAt(data.updated_at);
    if (modelsUpdatedEl) modelsUpdatedEl.textContent = formatTime(data.updated_at);
    renderModels(data.models || []);
    renderTasks(data.tasks || []);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
