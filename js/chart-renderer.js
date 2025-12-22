window.KDMChart = window.KDMChart || {
  renderLineChart(container, data, options = {}) {
    if (!container) return;
    container.innerHTML = "";
    if (!data || !data.length) {
      container.textContent = "暂无数据";
      return;
    }
    const width = options.width || 800;
    const height = options.height || 280;
    const padding = 30;

    const ys = data.map((d) => d.value);
    const minY = Math.min(...ys, 0);
    const maxY = Math.max(...ys, 1);
    const yRange = maxY - minY || 1;

    const scaleX = (x) =>
      padding + (x / Math.max(data.length - 1, 1)) * (width - padding * 2);
    const scaleY = (y) =>
      height - padding - ((y - minY) / yRange) * (height - padding * 2);

    const points = data.map((d, idx) => `${scaleX(idx)},${scaleY(d.value)}`).join(" ");

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "320");

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

    container.appendChild(svg);
  },
};
