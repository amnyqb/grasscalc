import { TYPES, buildChartInput, buildAnnotations } from "./chart-types.js";
import { mountGridForType } from "./grids.js";
import { McpClient, parseChartEnvelope } from "./mcp-client.js";

const CHART_TAG_KEY = "CHARTSMITH_ID";

const els = {
  status: document.getElementById("status-pill"),
  url: document.getElementById("mcp-url"),
  ds: document.getElementById("design-system"),
  refresh: document.getElementById("refresh-ds"),
  picker: document.getElementById("type-picker"),
  title: document.getElementById("chart-title"),
  gridHost: document.getElementById("grid-host"),
  addRow: document.getElementById("add-row"),
  addCol: document.getElementById("add-col"),
  delRow: document.getElementById("del-row"),
  delCol: document.getElementById("del-col"),
  cagr: document.getElementById("ann-cagr"),
  totals: document.getElementById("ann-totals"),
  preview: document.getElementById("preview-host"),
  warnings: document.getElementById("warnings"),
  insert: document.getElementById("btn-insert"),
  update: document.getElementById("btn-update"),
};

const state = {
  type: "bar",
  client: null,
  lastEnvelope: null,
  selectedShapeChartId: null, // chartId on the currently-selected slide shape, if any
  rerenderTimer: null,
};

// ----------------------------------------------------------------- status

function status(label, kind = "idle") {
  els.status.textContent = label;
  els.status.className = `cs-pill cs-pill--${kind}`;
}

function showWarnings(arr) {
  els.warnings.textContent = (arr ?? []).join("\n");
}

// ----------------------------------------------------------------- settings persistence

function loadSettings() {
  els.url.value = localStorage.getItem("cs.mcpUrl") ?? "http://localhost:3333/mcp";
  const ds = localStorage.getItem("cs.designSystem") ?? "default";
  els.ds.value = ds;
}
function saveSettings() {
  localStorage.setItem("cs.mcpUrl", els.url.value);
  localStorage.setItem("cs.designSystem", els.ds.value);
}

async function ensureClient() {
  if (state.client && state.client.url === els.url.value) return state.client;
  state.client = new McpClient(els.url.value);
  status("connecting…", "working");
  await state.client.initialize();
  status("ready", "ok");
  // Populate design system list.
  await refreshDesignSystems();
  return state.client;
}

async function refreshDesignSystems() {
  try {
    const result = await state.client.callTool("list_design_systems", {});
    const list = JSON.parse(result.content[0].text);
    const keep = els.ds.value;
    els.ds.innerHTML = "";
    for (const d of list) {
      const opt = document.createElement("option");
      opt.value = d.id;
      opt.textContent = d.name ?? d.id;
      els.ds.appendChild(opt);
    }
    if (list.find((d) => d.id === keep)) els.ds.value = keep;
  } catch (e) {
    console.warn("list_design_systems failed:", e);
  }
}

// ----------------------------------------------------------------- chart-type picker

function buildPicker() {
  els.picker.innerHTML = "";
  for (const [key, def] of Object.entries(TYPES)) {
    const btn = document.createElement("button");
    btn.className = "cs-thumb";
    btn.type = "button";
    btn.setAttribute("aria-pressed", key === state.type ? "true" : "false");
    btn.dataset.type = key;
    btn.innerHTML = `${def.icon}<span class="cs-thumb-label">${def.label}</span>`;
    btn.addEventListener("click", () => setType(key));
    els.picker.appendChild(btn);
  }
}

function setType(t) {
  state.type = t;
  for (const btn of els.picker.querySelectorAll(".cs-thumb")) {
    btn.setAttribute("aria-pressed", btn.dataset.type === t ? "true" : "false");
  }
  // Disable annotation toggles that don't apply to this type.
  const caps = TYPES[t].annotations;
  els.cagr.disabled = !caps.cagr;
  els.totals.disabled = !caps.totals;
  if (!caps.cagr) els.cagr.checked = false;
  if (!caps.totals) els.totals.checked = false;
  // Mount grid with type defaults.
  mountGridForType(els.gridHost, t, TYPES[t].defaults());
  scheduleRender();
}

// ----------------------------------------------------------------- live preview

function scheduleRender() {
  clearTimeout(state.rerenderTimer);
  state.rerenderTimer = setTimeout(renderPreview, 200);
}

async function renderPreview() {
  try {
    await ensureClient();
    const grid = els.gridHost.__grid;
    if (!grid) return;
    const gridState = grid.getState();
    const annotations = buildAnnotations(state.type, {
      cagr: els.cagr.checked,
      totals: els.totals.checked,
    }, gridState);
    const chart = buildChartInput(
      state.type,
      gridState,
      { title: els.title.value },
      annotations,
    );
    status("rendering…", "working");
    const result = await state.client.callTool("create_chart", {
      chart,
      design_system: els.ds.value,
      persistent: true,
    });
    const env = parseChartEnvelope(result);
    state.lastEnvelope = env;
    els.preview.innerHTML = env.svg.replace(/^<\?xml[^>]*\?>\s*/, "");
    showWarnings(env.warnings);
    status("ready", "ok");
  } catch (e) {
    status("error", "err");
    showWarnings([String(e.message ?? e)]);
  }
}

// ----------------------------------------------------------------- insert / update via Office.js

async function rasterizeSvgToPng(svg, widthPt, heightPt) {
  // Render at 2x for crisp PPT output.
  const scale = 2;
  const w = Math.round(widthPt * scale);
  const h = Math.round(heightPt * scale);
  const blob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  try {
    const img = await new Promise((resolve, reject) => {
      const i = new Image();
      i.onload = () => resolve(i);
      i.onerror = reject;
      i.src = url;
    });
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0, w, h);
    return canvas.toDataURL("image/png").replace(/^data:image\/png;base64,/, "");
  } finally {
    URL.revokeObjectURL(url);
  }
}

async function insertChart() {
  if (!state.lastEnvelope) return;
  const env = state.lastEnvelope;
  const pngBase64 = await rasterizeSvgToPng(env.svg, env.widthPt, env.heightPt);

  if (typeof PowerPoint === "undefined") {
    // Office.js not loaded (running outside PowerPoint, e.g. dev preview)
    alert("Insert is only available inside PowerPoint. Preview works fine here.");
    return;
  }

  await PowerPoint.run(async (context) => {
    const slide = context.presentation.slides.getItemAt(
      context.presentation.getSelectedSlides
        ? (await context.presentation.getSelectedSlides()).items[0].id
        : 0,
    );
    // Insert as image; size in points.
    const shape = slide.shapes.addImage(pngBase64, {
      width: env.widthPt,
      height: env.heightPt,
    });
    shape.tags.add(CHART_TAG_KEY, env.chartId);
    shape.altTextDescription = els.title.value || "Chartsmith chart";
    await context.sync();
  });
  status("inserted", "ok");
}

async function updateSelectedChart() {
  if (!state.lastEnvelope) {
    alert("Render a chart first, then click Update.");
    return;
  }
  if (!state.selectedShapeChartId) {
    alert("Select a chartsmith-inserted shape on the slide first.");
    return;
  }
  const env = state.lastEnvelope;
  // Push the patched data via update_chart so the server keeps the
  // original spec under the *original* chartId.
  await ensureClient();
  const grid = els.gridHost.__grid.getState();
  const patch = buildChartInput(state.type, grid, { title: els.title.value }, []);
  delete patch.type;
  delete patch.widthPt;
  delete patch.heightPt;
  delete patch.annotations;
  const result = await state.client.callTool("update_chart", {
    chartId: state.selectedShapeChartId,
    patch,
  });
  const updated = parseChartEnvelope(result);
  const pngBase64 = await rasterizeSvgToPng(updated.svg, updated.widthPt, updated.heightPt);

  await PowerPoint.run(async (context) => {
    const sel = await context.presentation.getSelectedShapes();
    sel.load("items");
    await context.sync();
    if (sel.items.length === 0) return;
    const old = sel.items[0];
    old.load(["top", "left", "width", "height"]);
    await context.sync();
    const slide = old.parentSlide ?? context.presentation.slides.getItemAt(0);
    const shape = slide.shapes.addImage(pngBase64, {
      top: old.top,
      left: old.left,
      width: old.width,
      height: old.height,
    });
    shape.tags.add(CHART_TAG_KEY, updated.chartId);
    shape.altTextDescription = els.title.value || "Chartsmith chart";
    old.delete();
    await context.sync();
  });
  status("updated", "ok");
}

async function checkSelection() {
  if (typeof PowerPoint === "undefined") return;
  try {
    await PowerPoint.run(async (context) => {
      const sel = await context.presentation.getSelectedShapes();
      sel.load("items");
      await context.sync();
      if (sel.items.length === 0) {
        state.selectedShapeChartId = null;
      } else {
        const sh = sel.items[0];
        sh.load("tags");
        await context.sync();
        const tag = sh.tags.getItemOrNullObject(CHART_TAG_KEY);
        tag.load("value");
        await context.sync();
        state.selectedShapeChartId = tag.isNullObject ? null : tag.value;
      }
      els.update.disabled = !state.selectedShapeChartId;
      // If the selected shape has a chartId, hydrate the form from server spec.
      if (state.selectedShapeChartId && !state.lastEnvelope) {
        await hydrateFromChartId(state.selectedShapeChartId);
      }
    });
  } catch (e) {
    console.warn("selection check failed", e);
  }
}

async function hydrateFromChartId(id) {
  try {
    await ensureClient();
    const result = await state.client.callTool("get_chart_spec", { chartId: id });
    const obj = JSON.parse(result.content[0].text);
    const spec = obj.spec;
    if (!TYPES[spec.type]) return;
    state.type = spec.type;
    setType(spec.type);
    // Coerce spec into the grid state shape and rebuild grid.
    const seed = {
      ...TYPES[spec.type].defaults(),
      ...spec,
    };
    mountGridForType(els.gridHost, spec.type, seed);
    els.title.value = spec.title ?? "";
    scheduleRender();
  } catch (e) {
    console.warn("hydrate failed", e);
  }
}

// ----------------------------------------------------------------- wire up

function wire() {
  els.url.addEventListener("change", () => { saveSettings(); state.client = null; ensureClient(); });
  els.ds.addEventListener("change", () => { saveSettings(); scheduleRender(); });
  els.refresh.addEventListener("click", refreshDesignSystems);
  els.title.addEventListener("input", scheduleRender);
  els.cagr.addEventListener("change", scheduleRender);
  els.totals.addEventListener("change", scheduleRender);
  els.gridHost.addEventListener("change", scheduleRender);
  els.addRow.addEventListener("click", () => els.gridHost.__grid?.addRow());
  els.delRow.addEventListener("click", () => els.gridHost.__grid?.delRow());
  els.addCol.addEventListener("click", () => els.gridHost.__grid?.addCol());
  els.delCol.addEventListener("click", () => els.gridHost.__grid?.delCol());
  els.insert.addEventListener("click", insertChart);
  els.update.addEventListener("click", updateSelectedChart);
}

function bootstrapPreviewOnly() {
  // Used outside Office (dev mode).
  loadSettings();
  buildPicker();
  setType(state.type);
  wire();
}

if (typeof Office !== "undefined") {
  Office.onReady(({ host }) => {
    if (host !== Office.HostType.PowerPoint) {
      // Still allow dev/preview in browser
      bootstrapPreviewOnly();
      return;
    }
    loadSettings();
    buildPicker();
    setType(state.type);
    wire();
    // Detect selection changes for the Update flow.
    Office.context.document.addHandlerAsync(
      Office.EventType.DocumentSelectionChanged,
      checkSelection,
    );
    checkSelection();
  });
} else {
  // Office.js not present (e.g. open the file directly during dev).
  bootstrapPreviewOnly();
}
