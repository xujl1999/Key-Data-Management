(() => {
  const loadJsonSync = (url) => {
    try {
      const xhr = new XMLHttpRequest();
      xhr.open("GET", url, false);
      xhr.send(null);
      if (xhr.status >= 200 && xhr.status < 300) {
        return JSON.parse(xhr.responseText);
      }
    } catch (error) {
      console.warn("Config load failed:", url, error);
    }
    return null;
  };

  window.KDM_CONFIG = {
    dataSources: loadJsonSync("config/data-sources.json") || {},
    healthGoals: loadJsonSync("config/health_goals.json") || {},
    healthMetrics: loadJsonSync("config/health_metrics.json") || {},
    bilibiliAuthors: loadJsonSync("config/bilibili_authors.json") || {},
  };
})();
