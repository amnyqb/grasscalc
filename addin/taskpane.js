import { TYPES, buildChartInput, buildAnnotations } from "./chart-types.js";
import { mountGridForType } from "./grids.js";
import { McpClient, parseChartEnvelope } from "./mcp-client.js";
import { readDeckTheme } from "./deck-theme.js";
import { insertNativeChart } from "./native-chart.js";

const CHART_TAG_KEY = "CHARTSMITH_ID";

const els = {
  status: document.getElementById("status-pill"),
  url: document.getElementById("mcp-url"),
  ds: document.getElementById("design-system"),
  refresh: document.getElementById("refresh-ds"),
  useDeckTheme: document.getElementById("use-deck-theme"),
  deckThemeStatus: document.getElementById("deck-theme-status"),
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
  modeImage: document.getElementById("mode-image"),
  modeNative: document.getElementById("mode-native"),
};

const NATIVE_MODE_KEY = "CHARTSMITH_NATIVE";

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
  const mode = localStorage.getItem("cs.insertMode") ?? "image";
  if (mode === "native" && els.modeNative) els.modeNative.checked = true;
  else if (els.modeImage) els.modeImage.checked = true;
}
function saveSettings() {
  localStorage.setItem("cs.mcpUrl", els.url.value);
  localStorage.setItem("cs.designSystem", els.ds.value);
  localStorage.setItem("cs.insertMode", nativeModeOn() ? "native" : "image");
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

// ----------------------------------------------------------------- deck theme

async function pullDeckTheme() {
  els.useDeckTheme.disabled = true;
  els.deckThemeStatus.textContent = "reading deck…";
  try {
    await ensureClient();
    const xml = await readDeckTheme();
    const result = await state.client.callTool("theme_to_design_system", {
      source: "xml",
      payload: xml,
      id: "deck",
      name: "Active deck",
    });
    const text = result.content?.[0]?.text ?? "";
    // Surface the categorical palette summary back to the user.
    const m = text.match(/Categorical palette: \[([^\]]+)\]/);
    els.deckThemeStatus.textContent = m
      ? `loaded — ${m[1].split(",").length} accents`
      : "loaded";
    await refreshDesignSystems();
    els.ds.value = "deck";
    saveSettings();
    scheduleRender();
  } catch (e) {
    els.deckThemeStatus.textContent = "";
    status("error", "err");
    showWarnings([`deck theme: ${e.message ?? e}`]);
  } finally {
    els.useDeckTheme.disabled = false;
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

function nativeModeOn() {
  return els.modeNative?.checked === true;
}

async function insertChart() {
  if (!state.lastEnvelope) return;
  if (typeof PowerPoint === "undefined") {
    alert("Insert is only available inside PowerPoint. Preview works fine here.");
    return;
  }

  if (nativeModeOn()) {
    return insertChartNative();
  }
  return insertChartImage();
}

/**
 * SVG/PNG path: preserves chartsmith annotation overlays and design-system
 * spacing exactly as the preview shows. Inserts as a picture.
 */
async function insertChartImage() {
  const env = state.lastEnvelope;
  const pngBase64 = await rasterizeSvgToPng(env.svg, env.widthPt, env.heightPt);

  await PowerPoint.run(async (context) => {
    const slide = context.presentation.slides.getItemAt(
      context.presentation.getSelectedSlides
        ? (await context.presentation.getSelectedSlides()).items[0].id
        : 0,
    );
    const shape = slide.shapes.addImage(pngBase64, {
      width: env.widthPt,
      height: env.heightPt,
    });
    shape.tags.add(CHART_TAG_KEY, env.chartId);
    shape.tags.add(NATIVE_MODE_KEY, "0");
    shape.altTextDescription = els.title.value || "Chartsmith chart";
    await context.sync();
  });
  status("inserted (image)", "ok");
}

/**
 * Native path: drops annotations (warned in UI), inserts a real PowerPoint
 * chart shape via slide.shapes.addChart. Editable, animatable, theme-linked.
 */
async function insertChartNative() {
  // Build a fresh spec from the grid (don't reuse the SVG envelope's
  // implicit annotations — they don't translate to native PPT charts).
  const grid = els.gridHost.__grid.getState();
  const spec = buildChartInput(state.type, grid, { title: els.title.value }, []);

  // Warn the user if they had annotations toggled on.
  const hadAnnotations = els.cagr.checked || els.totals.checked;
  if (hadAnnotations) {
    showWarnings([
      "native chart: chartsmith annotations (CAGR arrow, totals) are not preserved in native PowerPoint charts. Switch to Image mode to keep them.",
    ]);
  } else {
    showWarnings([]);
  }

  // Pull the active design system's categorical palette to color series.
  let palette = [];
  try {
    const dsResult = await state.client.callTool("get_design_system", { id: els.ds.value });
    const ds = JSON.parse(dsResult.content[0].text);
    palette = ds.palette?.categorical ?? [];
  } catch {
    /* fall back to PPT theme defaults */
  }

  const env = state.lastEnvelope;
  const chartId = env?.chartId ?? "native-" + Date.now();

  status("inserting native chart…", "working");
  await insertNativeChart(spec, palette, {
    widthPt: env?.widthPt ?? 480,
    heightPt: env?.heightPt ?? 270,
    title: spec.title,
    altText: spec.title || "Chartsmith chart",
    tags: { [CHART_TAG_KEY]: chartId, [NATIVE_MODE_KEY]: "1" },
  });
  status("inserted (native)", "ok");
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
  if (state.selectedShapeIsNative) {
    alert(
      "The selected shape is a native PowerPoint chart. Edit its data " +
        "directly in PowerPoint (double-click), or delete it and re-insert " +
        "from chartsmith.",
    );
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
        state.selectedShapeIsNative = false;
      } else {
        const sh = sel.items[0];
        sh.load("tags");
        await context.sync();
        const tag = sh.tags.getItemOrNullObject(CHART_TAG_KEY);
        const nativeTag = sh.tags.getItemOrNullObject(NATIVE_MODE_KEY);
        tag.load("value");
        nativeTag.load("value");
        await context.sync();
        state.selectedShapeChartId = tag.isNullObject ? null : tag.value;
        state.selectedShapeIsNative =
          !nativeTag.isNullObject && nativeTag.value === "1";
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
  els.useDeckTheme.addEventListener("click", pullDeckTheme);
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
  els.modeImage?.addEventListener("change", saveSettings);
  els.modeNative?.addEventListener("change", saveSettings);
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
