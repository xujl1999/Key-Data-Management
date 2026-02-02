window.KDMTabs = window.KDMTabs || {};

(() => {
  const DATA_URL = "health/dashboard_data.json";
  const TODO_STORAGE_KEY = "kdm-dashboard-todos";

  const qs = (id) => document.getElementById(id);
  const updatedAtEl = qs("dashboard-updated-at");
  const weatherEl = qs("dashboard-weather");
  const marketsEl = qs("dashboard-markets");
  const aiNewsEl = qs("dashboard-ai-news");
  const skillsEl = qs("dashboard-skills");
  const todoListEl = qs("dashboard-todo-list");
  const todoInputEl = qs("dashboard-todo-input");
  const todoAddEl = qs("dashboard-todo-add");
  const todoCountEl = qs("dashboard-todo-count");

  const formatNumber = (value, digits = 2) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return "--";
    return num.toFixed(digits);
  };

  const formatChange = (value) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return { text: "--", className: "dashboard-change--flat" };
    const sign = num > 0 ? "+" : "";
    const className = num > 0 ? "dashboard-change--up" : num < 0 ? "dashboard-change--down" : "dashboard-change--flat";
    return { text: `${sign}${num.toFixed(2)}%`, className };
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

  const renderEmpty = (target, message) => {
    if (!target) return;
    target.innerHTML = `<div class="dashboard-empty">${message}</div>`;
  };

  const renderWeather = (weather) => {
    if (!weatherEl) return;
    const cities = [
      { key: "shenzhen", label: "深圳南山" },
      { key: "chengdu", label: "成都" },
    ];
    weatherEl.innerHTML = cities
      .map(({ key, label }) => {
        const info = weather && weather[key] ? weather[key] : {};
        const tempMin = formatNumber(info.temp_min, 0);
        const tempMax = formatNumber(info.temp_max, 0);
        const aqi = Number.isFinite(Number(info.aqi)) ? info.aqi : "--";
        const aqiLevel = info.aqi_level || "--";
        const rain = info.rain_forecast || "暂无预报";
        return `
          <div class="dashboard-weather__city">
            <div class="dashboard-weather__name">${label}</div>
            <div class="dashboard-weather__temp">${tempMin}°C - ${tempMax}°C</div>
            <div class="dashboard-weather__meta">
              <span class="dashboard-pill">AQI ${aqi} ${aqiLevel}</span>
              <span>${rain}</span>
            </div>
          </div>
        `;
      })
      .join("");
  };

  const renderMarkets = (markets) => {
    if (!marketsEl) return;
    if (!Array.isArray(markets) || !markets.length) {
      renderEmpty(marketsEl, "暂无市场数据");
      return;
    }
    marketsEl.innerHTML = markets
      .map((item) => {
        const change = formatChange(item.change);
        return `
          <div class="dashboard-market">
            <div>
              <div class="dashboard-market__name">${item.name || "--"}</div>
              <div class="dashboard-market__symbol">${item.symbol || "--"}</div>
            </div>
            <div class="dashboard-market__price">${formatNumber(item.price)}</div>
            <div class="dashboard-market__change ${change.className}">${change.text}</div>
          </div>
        `;
      })
      .join("");
  };

  const renderList = (items, target, emptyText) => {
    if (!target) return;
    if (!Array.isArray(items) || !items.length) {
      renderEmpty(target, emptyText);
      return;
    }
    target.innerHTML = items
      .map((item) => {
        const title = item.title || item.name || "--";
        const summary = item.summary || "";
        const url = item.url || "#";
        const summaryHtml = summary ? `<p class="dashboard-list__summary">${summary}</p>` : "";
        return `
          <div class="dashboard-list__item">
            <a href="${url}" target="_blank" rel="noopener" class="dashboard-list__title">${title}</a>
            ${summaryHtml}
          </div>
        `;
      })
      .join("");
  };

  const todoState = {
    items: [],
  };

  const saveTodos = () => {
    try {
      localStorage.setItem(TODO_STORAGE_KEY, JSON.stringify(todoState.items));
    } catch (error) {
      console.warn("保存 Todo 失败:", error);
    }
  };

  const updateTodoCount = () => {
    if (!todoCountEl) return;
    const total = todoState.items.length;
    const done = todoState.items.filter((item) => item.done).length;
    todoCountEl.textContent = `${done}/${total} 已完成`;
  };

  const renderTodos = () => {
    if (!todoListEl) return;
    todoListEl.innerHTML = "";
    if (!todoState.items.length) {
      todoListEl.innerHTML = '<div class="dashboard-empty">暂无待办事项</div>';
      updateTodoCount();
      return;
    }
    todoState.items.forEach((item) => {
      const row = document.createElement("div");
      row.className = `dashboard-todo__item${item.done ? " is-done" : ""}`;
      row.dataset.id = String(item.id);

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.className = "dashboard-todo__check";
      checkbox.checked = Boolean(item.done);

      const textInput = document.createElement("input");
      textInput.type = "text";
      textInput.className = "dashboard-todo__text";
      textInput.value = item.text || "";

      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "dashboard-todo__delete";
      deleteBtn.textContent = "删除";

      row.append(checkbox, textInput, deleteBtn);
      todoListEl.append(row);
    });
    updateTodoCount();
  };

  const addTodo = () => {
    if (!todoInputEl) return;
    const text = todoInputEl.value.trim();
    if (!text) return;
    todoState.items.push({
      id: Date.now(),
      text,
      done: false,
    });
    saveTodos();
    renderTodos();
    todoInputEl.value = "";
    todoInputEl.focus();
  };

  const bindTodoEvents = () => {
    if (todoAddEl) todoAddEl.addEventListener("click", addTodo);
    if (todoInputEl) {
      todoInputEl.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          addTodo();
        }
      });
    }
    if (!todoListEl) return;
    todoListEl.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("dashboard-todo__delete")) return;
      const row = target.closest(".dashboard-todo__item");
      if (!row) return;
      const id = Number(row.dataset.id);
      todoState.items = todoState.items.filter((item) => item.id !== id);
      saveTodos();
      renderTodos();
    });

    todoListEl.addEventListener("change", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const row = target.closest(".dashboard-todo__item");
      if (!row) return;
      const id = Number(row.dataset.id);
      const item = todoState.items.find((entry) => entry.id === id);
      if (!item) return;
      if (target.classList.contains("dashboard-todo__check")) {
        item.done = target.checked;
        row.classList.toggle("is-done", item.done);
        saveTodos();
        updateTodoCount();
      }
    });

    todoListEl.addEventListener("input", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("dashboard-todo__text")) return;
      const row = target.closest(".dashboard-todo__item");
      if (!row) return;
      const id = Number(row.dataset.id);
      const item = todoState.items.find((entry) => entry.id === id);
      if (!item) return;
      item.text = target.value;
      saveTodos();
    });
  };

  const loadTodos = (fallback) => {
    try {
      const stored = localStorage.getItem(TODO_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          todoState.items = parsed;
          return;
        }
      }
    } catch (error) {
      console.warn("读取 Todo 失败:", error);
    }
    todoState.items = Array.isArray(fallback) ? fallback : [];
  };

  const fetchDashboardData = async () => {
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
      console.error("加载仪表盘数据失败:", error);
      return null;
    }
  };

  const boot = async () => {
    const data = await fetchDashboardData();
    if (!data) {
      if (updatedAtEl) updatedAtEl.textContent = "加载失败";
      renderEmpty(weatherEl, "天气数据加载失败");
      renderEmpty(marketsEl, "市场数据加载失败");
      renderEmpty(aiNewsEl, "AI 新闻加载失败");
      renderEmpty(skillsEl, "技能列表加载失败");
      loadTodos([]);
      renderTodos();
      return;
    }
    if (updatedAtEl) updatedAtEl.textContent = formatUpdatedAt(data.updated_at);
    renderWeather(data.weather || {});
    renderMarkets(data.markets || []);
    renderList(data.ai_news || [], aiNewsEl, "暂无 AI 动态");
    renderList(data.clawhub_skills || [], skillsEl, "暂无推荐技能");
    loadTodos(data.todos || []);
    renderTodos();
  };

  bindTodoEvents();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
