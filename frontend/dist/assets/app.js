const GROUP_LABELS = {
  Poet: "词人",
  Cipai: "词牌",
  Instrument: "乐器",
  Period: "朝代",
  CiStyle: "流派",
  Alias: "别称",
  Work: "作品",
  Context: "文献",
};

const PERIODS = ["全部", "唐五代", "北宋", "南宋", "宋末"];
const MOBILE_BP = 768;

let network = null;
let nodesDataset = null;
let edgesDataset = null;
let currentPeriod = null;
let graphData = { nodes: [], links: [] };
let activeLegendGroups = new Set();
let contextText = "";
let panelMode = "detail"; // detail | context

const els = {
  graph: document.getElementById("graph"),
  loading: document.getElementById("loading"),
  searchInput: document.getElementById("searchInput"),
  searchBtn: document.getElementById("searchBtn"),
  resetBtn: document.getElementById("resetBtn"),
  detailPanel: document.getElementById("detailPanel"),
  detailContent: document.getElementById("detailContent"),
  panelTitle: document.getElementById("panelTitle"),
  closePanel: document.getElementById("closePanel"),
  panelBackdrop: document.getElementById("panelBackdrop"),
  timelineFilters: document.getElementById("timelineFilters"),
  legendList: document.getElementById("legendList"),
  legendPanel: document.getElementById("legendPanel"),
  legendToggle: document.getElementById("legendToggle"),
  legendClose: document.getElementById("legendClose"),
  legendBackdrop: document.getElementById("legendBackdrop"),
  legendClear: document.getElementById("legendClear"),
  contextBtn: document.getElementById("contextBtn"),
  contextSection: document.getElementById("contextSection"),
  contextToggle: document.getElementById("contextToggle"),
  contextContent: document.getElementById("contextContent"),
};

function isMobile() {
  return window.innerWidth <= MOBILE_BP;
}

function showLoading(show) {
  els.loading.classList.toggle("hidden", !show);
}

function openPanel(mode = "detail") {
  panelMode = mode;
  els.detailPanel.classList.remove("hidden");
  els.detailPanel.classList.toggle("context-only", mode === "context");
  els.panelTitle.textContent = mode === "context" ? "文献背景" : "节点详情";
  if (isMobile()) {
    els.panelBackdrop.classList.remove("hidden");
    requestAnimationFrame(() => els.panelBackdrop.classList.add("visible"));
  }
}

function closePanel() {
  els.detailPanel.classList.add("hidden");
  els.detailPanel.classList.remove("context-only");
  els.panelBackdrop.classList.remove("visible");
  setTimeout(() => els.panelBackdrop.classList.add("hidden"), 250);
}

function openLegend() {
  els.legendPanel.classList.add("open");
  if (isMobile()) {
    els.legendBackdrop.classList.remove("hidden");
    requestAnimationFrame(() => els.legendBackdrop.classList.add("visible"));
  }
}

function closeLegend() {
  els.legendPanel.classList.remove("open");
  els.legendBackdrop.classList.remove("visible");
  setTimeout(() => els.legendBackdrop.classList.add("hidden"), 250);
}

function buildVisData(data) {
  nodesDataset = new vis.DataSet(
    data.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      color: {
        background: n.color,
        border: n.color,
        highlight: { background: n.color, border: "#2c2416" },
      },
      font: { color: "#2c2416", face: "Noto Serif SC", size: isMobile() ? 12 : 14 },
      group: n.group,
      shape: n.group === "Work" ? "box" : "dot",
      size: n.group === "Cipai" ? (isMobile() ? 18 : 22) : (isMobile() ? 14 : 16),
      hidden: false,
      opacity: 1,
    }))
  );

  edgesDataset = new vis.DataSet(
    data.links.map((l, i) => ({
      id: i,
      from: l.source,
      to: l.target,
      label: isMobile() ? undefined : l.type,
      font: { size: 9, color: "#9a8b7a", strokeWidth: 0 },
      color: { color: "#c4b8a8", highlight: "#8b4513" },
      arrows: "to",
      smooth: { type: "continuous" },
      hidden: false,
    }))
  );

  return { nodes: nodesDataset, edges: edgesDataset };
}

function applyLegendFilter() {
  if (!nodesDataset || !edgesDataset) return;

  const hasFilter = activeLegendGroups.size > 0;
  els.legendClear.classList.toggle("hidden", !hasFilter);

  const nodeUpdates = graphData.nodes.map((n) => {
    const visible = !hasFilter || activeLegendGroups.has(n.group);
    return {
      id: n.id,
      hidden: !visible,
      opacity: visible ? 1 : 0.15,
      font: { color: visible ? "#2c2416" : "#b0a89c" },
    };
  });
  nodesDataset.update(nodeUpdates);

  const visibleIds = new Set(
    graphData.nodes
      .filter((n) => !hasFilter || activeLegendGroups.has(n.group))
      .map((n) => n.id)
  );

  const edgeUpdates = graphData.links.map((l, i) => ({
    id: i,
    hidden: hasFilter && (!visibleIds.has(l.source) || !visibleIds.has(l.target)),
  }));
  edgesDataset.update(edgeUpdates);

  els.legendList.querySelectorAll("li").forEach((li) => {
    const group = li.dataset.group;
    li.classList.toggle("active", activeLegendGroups.has(group));
    li.classList.toggle("dimmed", hasFilter && !activeLegendGroups.has(group));
  });
}

function renderGraph(data) {
  graphData = data;
  activeLegendGroups.clear();
  const visData = buildVisData(data);

  const options = {
    physics: {
      enabled: true,
      barnesHut: {
        gravitationalConstant: isMobile() ? -5000 : -8000,
        springLength: isMobile() ? 100 : 120,
        damping: 0.09,
      },
      stabilization: { iterations: isMobile() ? 100 : 150 },
    },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      navigationButtons: !isMobile(),
      keyboard: !isMobile(),
      zoomView: true,
      dragView: true,
    },
    nodes: { borderWidth: 2, shadow: !isMobile() },
    edges: { width: 1 },
  };

  if (network) {
    network.setData(visData);
    network.setOptions(options);
  } else {
    network = new vis.Network(els.graph, visData, options);
    network.on("click", (params) => {
      if (params.nodes.length > 0) {
        loadNodeDetail(params.nodes[0]);
      }
    });
    network.on("stabilizationIterationsDone", () => showLoading(false));
  }

  applyLegendFilter();
}

function renderLegend(data) {
  const counts = {};
  data.nodes.forEach((n) => {
    counts[n.group] = (counts[n.group] || 0) + 1;
  });

  const groups = Object.keys(counts).sort(
    (a, b) => (GROUP_LABELS[a] || a).localeCompare(GROUP_LABELS[b] || b, "zh")
  );

  els.legendList.innerHTML = "";
  groups.forEach((group) => {
    const color = data.nodes.find((n) => n.group === group)?.color || "#888";
    const li = document.createElement("li");
    li.dataset.group = group;
    li.innerHTML = `<span class="dot" style="background:${color}"></span><span>${GROUP_LABELS[group] || group}</span><span class="count">${counts[group]}</span>`;
    li.addEventListener("click", () => toggleLegendGroup(group));
    els.legendList.appendChild(li);
  });
}

function toggleLegendGroup(group) {
  if (activeLegendGroups.has(group)) {
    activeLegendGroups.delete(group);
  } else {
    activeLegendGroups.add(group);
  }
  applyLegendFilter();
}

async function fetchGraph(period = null) {
  showLoading(true);
  const params = new URLSearchParams({ limit: "120" });
  if (period) params.set("period", period);
  const res = await fetch(`/api/graph?${params}`);
  const data = await res.json();
  renderGraph(data);
  renderLegend(data);
}

async function searchGraph(q) {
  showLoading(true);
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&limit=80`);
  const data = await res.json();
  renderGraph(data);
  renderLegend(data);
  if (data.nodes.length > 0 && network) {
    network.selectNodes([data.nodes[0].id]);
    network.focus(data.nodes[0].id, { scale: isMobile() ? 1.0 : 1.2, animation: true });
  }
}

async function loadContext() {
  if (contextText) return;
  try {
    const res = await fetch("/api/context");
    const data = await res.json();
    contextText = data.content || "暂无文献背景数据。";
    renderContext(contextText);
  } catch {
    contextText = "文献背景加载失败。";
    renderContext(contextText);
  }
}

function renderContext(text) {
  const paragraphs = text.split("\n").filter(Boolean);
  els.contextContent.innerHTML = paragraphs.length
    ? paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join("")
    : `<p class="context-loading">暂无文献背景数据。</p>`;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function loadNodeDetail(nodeId) {
  const res = await fetch(`/api/node/${encodeURIComponent(nodeId)}`);
  if (!res.ok) return;
  const detail = await res.json();
  renderDetail(detail);
  openPanel("detail");
  expandContext(true);
}

function renderDetail(d) {
  const props = d.properties || {};
  const groupLabel = GROUP_LABELS[d.group] || d.group;

  let html = `<h2>${escapeHtml(d.label)}</h2><span class="type-badge">${escapeHtml(groupLabel)}</span><dl>`;

  const fieldMap = {
    name: "名称",
    alias: "别称",
    type: "词体",
    famous_line: "名句",
    classic_work: "经典篇目",
    style: "流派",
    period: "朝代",
    description: "说明",
    title: "标题",
    note: "备注",
    content: "内容",
  };

  Object.entries(fieldMap).forEach(([key, label]) => {
    if (props[key]) {
      html += `<dt>${label}</dt><dd>${escapeHtml(String(props[key]))}</dd>`;
    }
  });

  html += "</dl>";

  if (d.related && d.related.length > 0) {
    html += `<div class="related-section"><h3>关联实体</h3>`;
    d.related.forEach((r) => {
      const relLabel = r.relation || "";
      const nodeLabel = r.node?.label || "";
      html += `<div class="related-item" data-id="${escapeHtml(r.node?.id || "")}">
        <span class="rel-tag">${escapeHtml(relLabel)}</span>${escapeHtml(nodeLabel)}
      </div>`;
    });
    html += "</div>";
  }

  els.detailContent.innerHTML = html;

  els.detailContent.querySelectorAll(".related-item").forEach((el) => {
    el.addEventListener("click", () => {
      const id = el.dataset.id;
      if (id) loadNodeDetail(id);
    });
  });
}

function expandContext(expanded) {
  els.contextContent.classList.toggle("collapsed", !expanded);
  els.contextToggle.classList.toggle("collapsed", !expanded);
  els.contextToggle.setAttribute("aria-expanded", String(expanded));
}

function initTimeline() {
  PERIODS.forEach((p) => {
    const btn = document.createElement("button");
    btn.textContent = p;
    if (p === "全部") btn.classList.add("active");
    btn.addEventListener("click", () => {
      els.timelineFilters.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentPeriod = p === "全部" ? null : p;
      fetchGraph(currentPeriod);
    });
    els.timelineFilters.appendChild(btn);
  });
}

els.searchBtn.addEventListener("click", () => {
  const q = els.searchInput.value.trim();
  if (q) searchGraph(q);
});

els.searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const q = els.searchInput.value.trim();
    if (q) searchGraph(q);
  }
});

els.resetBtn.addEventListener("click", () => {
  els.searchInput.value = "";
  closePanel();
  els.detailContent.innerHTML = "";
  els.timelineFilters.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
  els.timelineFilters.querySelector("button").classList.add("active");
  currentPeriod = null;
  activeLegendGroups.clear();
  fetchGraph();
});

els.closePanel.addEventListener("click", closePanel);
els.panelBackdrop.addEventListener("click", closePanel);

els.legendToggle.addEventListener("click", openLegend);
els.legendClose.addEventListener("click", closeLegend);
els.legendBackdrop.addEventListener("click", closeLegend);

els.legendClear.addEventListener("click", () => {
  activeLegendGroups.clear();
  applyLegendFilter();
});

els.contextBtn.addEventListener("click", () => {
  loadContext().then(() => {
    els.detailContent.innerHTML = "";
    openPanel("context");
    expandContext(true);
  });
});

els.contextToggle.addEventListener("click", () => {
  const expanded = els.contextContent.classList.contains("collapsed");
  expandContext(expanded);
});

window.addEventListener("resize", () => {
  if (!isMobile()) {
    closeLegend();
    els.panelBackdrop.classList.add("hidden");
    els.panelBackdrop.classList.remove("visible");
  }
  if (network) {
    network.redraw();
    network.setOptions({
      interaction: { navigationButtons: !isMobile(), keyboard: !isMobile() },
    });
  }
});

initTimeline();
loadContext();
fetchGraph();
