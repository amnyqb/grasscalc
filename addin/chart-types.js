// Per-type chart definitions: thumbnail icon, default data shape, supported
// annotation toggles, and a function that turns the editable grid + form
// state into a chartsmith chart-input object.
//
// Each "grid shape" defines what the data table looks like:
//   - rowsByCategory:   rows = categories,        cols = series   (bar/area/waterfall)
//   - pointsBySeries:   rows = points,            cols = {x, y} per series (line/scatter)
//   - slices:           rows = slices,            cols = label/value (pie)

export const TYPES = {
  bar: {
    label: "Bar",
    grid: "rowsByCategory",
    annotations: { cagr: true, totals: true },
    defaults: () => ({
      categories: ["Q1", "Q2", "Q3", "Q4"],
      series: [
        { name: "EMEA", values: [40, 50, 60, 75] },
        { name: "AMER", values: [60, 70, 85, 100] },
      ],
      stacked: true,
      showValues: false,
    }),
    icon: thumb`<g fill="currentColor">
      <rect x="6"  y="22" width="6" height="16"/>
      <rect x="16" y="14" width="6" height="24"/>
      <rect x="26" y="18" width="6" height="20"/>
      <rect x="36" y="8"  width="6" height="30"/>
    </g>`,
  },

  waterfall: {
    label: "Waterfall",
    grid: "waterfall",
    annotations: { cagr: false, totals: false },
    defaults: () => ({
      categories: ["FY24", "Volume", "Price", "Cost", "FY25"],
      values: [120, 18, 12, -8, 142],
      subtotalIndices: [0, 4],
    }),
    icon: thumb`<g>
      <rect x="4"  y="14" width="6" height="24" fill="#1f3a68"/>
      <rect x="12" y="10" width="6" height="6"  fill="#5b8def"/>
      <rect x="20" y="6"  width="6" height="8"  fill="#5b8def"/>
      <rect x="28" y="14" width="6" height="6"  fill="#a33333"/>
      <rect x="38" y="6"  width="6" height="32" fill="#1f3a68"/>
      <line x1="10" y1="14" x2="12" y2="14" stroke="#888" stroke-dasharray="2,2"/>
      <line x1="18" y1="10" x2="20" y2="10" stroke="#888" stroke-dasharray="2,2"/>
      <line x1="26" y1="6"  x2="28" y2="6"  stroke="#888" stroke-dasharray="2,2"/>
      <line x1="34" y1="20" x2="38" y2="20" stroke="#888" stroke-dasharray="2,2"/>
    </g>`,
  },

  line: {
    label: "Line",
    grid: "pointsBySeries",
    annotations: { cagr: true, totals: false },
    defaults: () => ({
      series: [
        {
          name: "WAU",
          points: [
            { x: 1, y: 100 },
            { x: 2, y: 130 },
            { x: 3, y: 150 },
            { x: 4, y: 200 },
            { x: 5, y: 240 },
          ],
        },
      ],
      smoothing: "monotone",
      showPoints: true,
    }),
    icon: thumb`<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <polyline points="4,32 12,24 20,28 28,14 36,18 44,8"/>
      <circle cx="4" cy="32" r="2.5" fill="currentColor"/>
      <circle cx="12" cy="24" r="2.5" fill="currentColor"/>
      <circle cx="20" cy="28" r="2.5" fill="currentColor"/>
      <circle cx="28" cy="14" r="2.5" fill="currentColor"/>
      <circle cx="36" cy="18" r="2.5" fill="currentColor"/>
      <circle cx="44" cy="8"  r="2.5" fill="currentColor"/>
    </g>`,
  },

  scatter: {
    label: "Scatter",
    grid: "pointsBySeries",
    annotations: { cagr: false, totals: false },
    defaults: () => ({
      series: [
        {
          name: "Series A",
          points: [
            { x: 5, y: 22 },
            { x: 12, y: 18 },
            { x: 18, y: 30 },
            { x: 25, y: 12 },
            { x: 32, y: 25 },
          ],
        },
      ],
    }),
    icon: thumb`<g fill="currentColor">
      <circle cx="8"  cy="30" r="3"/>
      <circle cx="16" cy="20" r="3"/>
      <circle cx="22" cy="32" r="3"/>
      <circle cx="30" cy="14" r="3"/>
      <circle cx="36" cy="22" r="3"/>
      <circle cx="42" cy="10" r="3"/>
    </g>`,
  },

  area: {
    label: "Area",
    grid: "rowsByCategory",
    annotations: { cagr: true, totals: false },
    defaults: () => ({
      categories: ["Jan", "Feb", "Mar", "Apr", "May"],
      series: [
        { name: "Free", values: [120, 150, 180, 200, 240] },
        { name: "Pro", values: [30, 45, 60, 90, 120] },
      ],
      stacked: true,
      smoothing: "monotone",
    }),
    icon: thumb`<g>
      <path d="M4 38 L4 24 L14 18 L24 22 L34 12 L44 16 L44 38 Z" fill="currentColor" opacity="0.4"/>
      <polyline points="4,24 14,18 24,22 34,12 44,16" fill="none" stroke="currentColor" stroke-width="1.5"/>
    </g>`,
  },

  pie: {
    label: "Pie",
    grid: "slices",
    annotations: { cagr: false, totals: false },
    defaults: () => ({
      slices: [
        { label: "Direct", value: 38 },
        { label: "Search", value: 32 },
        { label: "Social", value: 18 },
        { label: "Referral", value: 12 },
      ],
      donut: true,
    }),
    icon: thumb`<g transform="translate(24 24)">
      <path d="M0 -16 A16 16 0 0 1 13.86 8 L0 0 Z" fill="#1f3a68"/>
      <path d="M13.86 8 A16 16 0 0 1 -13.86 8 L0 0 Z" fill="#5b8def"/>
      <path d="M-13.86 8 A16 16 0 0 1 0 -16 L0 0 Z" fill="#9ec5fe"/>
      <circle r="6" fill="white"/>
    </g>`,
  },
};

function thumb(strings, ...values) {
  let inner = "";
  strings.forEach((s, i) => {
    inner += s;
    if (i < values.length) inner += String(values[i]);
  });
  return `<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;
}

/** Build a chartsmith chart input from the grid state + form. */
export function buildChartInput(type, gridState, form, annotations) {
  const t = TYPES[type];
  if (!t) throw new Error(`Unknown chart type: ${type}`);

  const base = {
    type,
    title: form.title || undefined,
    widthPt: 720,
    heightPt: 420,
  };

  let body;
  if (t.grid === "rowsByCategory") {
    body = {
      categories: gridState.categories,
      series: gridState.series,
    };
    if (type === "bar") {
      body.stacked = !!gridState.stacked;
    } else if (type === "area") {
      body.stacked = gridState.stacked !== false;
      body.smoothing = "monotone";
    }
  } else if (t.grid === "pointsBySeries") {
    body = { series: gridState.series };
    if (type === "line") {
      body.smoothing = "monotone";
      body.showPoints = true;
    }
  } else if (t.grid === "slices") {
    body = { slices: gridState.slices, donut: !!gridState.donut };
  } else if (t.grid === "waterfall") {
    body = {
      categories: gridState.categories,
      values: gridState.values,
      subtotalIndices: gridState.subtotalIndices ?? [],
      showValues: true,
      showConnectors: true,
    };
  }

  return { ...base, ...body, annotations };
}

/** Build the annotation list from the toggles. */
export function buildAnnotations(type, toggles, gridState) {
  const result = [];
  const caps = TYPES[type].annotations;
  if (toggles.cagr && caps.cagr) {
    // Pick first/last category in first series.
    let from, to, seriesName;
    if (gridState.series && gridState.series.length) {
      seriesName = gridState.series[0].name;
      if (gridState.categories) {
        from = { x: gridState.categories[0], series: seriesName };
        to = { x: gridState.categories[gridState.categories.length - 1], series: seriesName };
      } else if (gridState.series[0].points && gridState.series[0].points.length >= 2) {
        const pts = gridState.series[0].points;
        from = { x: pts[0].x, series: seriesName };
        to = { x: pts[pts.length - 1].x, series: seriesName };
      }
    }
    if (from && to) {
      result.push({ type: "cagr_arrow", from, to, format: ".1%", placement: "above" });
    }
  }
  if (toggles.totals && caps.totals) {
    result.push({ type: "total_labels", format: ",.0f" });
  }
  return result;
}
