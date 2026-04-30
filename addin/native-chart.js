/**
 * Insert a chartsmith spec as a NATIVE PowerPoint chart (editable, animatable,
 * theme-linked) using Office.js `slide.shapes.addChart()`.
 *
 * Trade-offs vs. SVG/PNG mode:
 *   + double-click to edit data; respects PPT animations; renders in PPT's
 *     own engine so it always matches whatever theme tweaks the user makes
 *     after insertion
 *   - chartsmith's annotation overlays (cagr_arrow, delta, bracket, callout,
 *     reference_line, range_band, total_labels) are NOT preserved — those
 *     live in our SVG layer, not in the OOXML chart part
 *   - some chartsmith-specific styling (corner radii, custom spacing) is
 *     replaced by PowerPoint's default chart visuals
 *
 * Public API:
 *   - mapChartType(spec) → PowerPoint.ChartType string
 *   - shapeData(spec)    → { values, seriesNames, categories }   (pure)
 *   - insertNativeChart(spec, palette, opts)                     (Office.js)
 *
 * The first two are pure and unit-testable without PowerPoint.
 */

/**
 * Map our chartsmith chart type (and option flags) to a PowerPoint.ChartType
 * string. We use string-typed names so this works whether the host exposes
 * a numeric enum or a string accessor.
 */
export function mapChartType(spec) {
  switch (spec.type) {
    case "bar": {
      const stacked = !!spec.stacked;
      const horizontal = spec.orientation === "horizontal";
      if (horizontal) return stacked ? "barStacked" : "barClustered";
      return stacked ? "columnStacked" : "columnClustered";
    }
    case "line":
      return "line";
    case "scatter":
      return "xyscatter";
    case "area":
      return spec.stacked === false ? "area" : "areaStacked";
    case "pie":
      return spec.donut ? "doughnut" : "pie";
    case "waterfall":
      // PowerPoint 2016+ supports a native waterfall.
      return "waterfall";
    default:
      throw new Error(`mapChartType: unsupported type "${spec.type}"`);
  }
}

/**
 * Convert a chartsmith spec into the (values, seriesNames, categories) shape
 * that `addChart` expects.
 *
 *   values: number[][]          // values[seriesIdx][categoryIdx]
 *   seriesNames: string[]       // length = values.length
 *   categories: string[]|number[]
 *
 * Pure, deterministic. Throws on shape mismatches.
 */
export function shapeData(spec) {
  switch (spec.type) {
    case "bar":
    case "area": {
      const categories = spec.categories.slice();
      const seriesNames = spec.series.map((s) => s.name);
      const values = spec.series.map((s) => {
        if (s.values.length !== categories.length) {
          throw new Error(
            `shapeData: series "${s.name}" has ${s.values.length} values, expected ${categories.length}`,
          );
        }
        return s.values.slice();
      });
      return { values, seriesNames, categories };
    }
    case "line": {
      // Use the union of x values across all series, sorted naturally.
      const xs = unionXs(spec.series);
      const seriesNames = spec.series.map((s) => s.name);
      const values = spec.series.map((s) => {
        const ymap = new Map(s.points.map((p) => [String(p.x), p.y]));
        return xs.map((x) => (ymap.has(String(x)) ? ymap.get(String(x)) : 0));
      });
      return { values, seriesNames, categories: xs };
    }
    case "scatter": {
      // Scatter has no shared category axis; native xyscatter is the only
      // chart type that takes (x, y) pairs. We flatten one series per call
      // and let PowerPoint handle the rest. For multi-series we still pad
      // x values to align positions; PowerPoint does (x, y) pair plotting.
      const xs = unionXs(spec.series);
      const seriesNames = spec.series.map((s) => s.name);
      const values = spec.series.map((s) => {
        const ymap = new Map(s.points.map((p) => [String(p.x), p.y]));
        return xs.map((x) => (ymap.has(String(x)) ? ymap.get(String(x)) : 0));
      });
      return { values, seriesNames, categories: xs };
    }
    case "pie": {
      // Pie: one "series" with all slice values; categories = slice labels.
      const categories = spec.slices.map((s) => s.label);
      const seriesNames = [spec.title || "Series 1"];
      const values = [spec.slices.map((s) => s.value)];
      return { values, seriesNames, categories };
    }
    case "waterfall": {
      // Native PPT waterfall takes a single series with category labels.
      // Subtotals are usually marked via a separate property; for the
      // initial pass we let PowerPoint auto-detect totals from the data.
      const seriesNames = [spec.title || "Series 1"];
      const values = [spec.values.slice()];
      return { values, seriesNames, categories: spec.categories.slice() };
    }
    default:
      throw new Error(`shapeData: unsupported type "${spec.type}"`);
  }
}

function unionXs(series) {
  const seen = new Map();
  for (const s of series) {
    for (const p of s.points) {
      const key = String(p.x);
      if (!seen.has(key)) seen.set(key, p.x);
    }
  }
  const arr = Array.from(seen.values());
  // Sort numerically when possible; otherwise insertion order.
  if (arr.every((v) => typeof v === "number" && Number.isFinite(v))) {
    arr.sort((a, b) => a - b);
  }
  return arr;
}

/**
 * Insert a native chart on the active slide. Requires Office.js and a
 * PowerPoint host. Best-effort: we attempt to color series from `palette`
 * (which mirrors the chartsmith design system's `categorical` array) but
 * silently fall back to PowerPoint's default theme colors if the host
 * doesn't expose series styling.
 *
 * Returns the new shape (loaded with id) so the caller can tag it.
 */
export async function insertNativeChart(spec, palette, opts = {}) {
  if (typeof PowerPoint === "undefined") {
    throw new Error("insertNativeChart requires PowerPoint host");
  }

  const chartTypeStr = mapChartType(spec);
  const data = shapeData(spec);
  const widthPt = opts.widthPt ?? spec.widthPt ?? 480;
  const heightPt = opts.heightPt ?? spec.heightPt ?? 270;

  let shape;
  await PowerPoint.run(async (context) => {
    const slide = await pickActiveSlide(context);
    // The host may expose ChartType either as a numeric enum or accept a
    // string. We pass the string; the typings declare ChartType but the
    // runtime usually accepts the equivalent string.
    const ct =
      (PowerPoint.ChartType && PowerPoint.ChartType[chartTypeStr]) ??
      chartTypeStr;
    shape = slide.shapes.addChart(ct, data.values, {
      seriesNames: data.seriesNames,
      categories: data.categories.map(String),
      width: widthPt,
      height: heightPt,
      ...(opts.top != null ? { top: opts.top } : {}),
      ...(opts.left != null ? { left: opts.left } : {}),
    });
    if (opts.title) {
      try {
        shape.chart.title.text = opts.title;
      } catch {
        /* host may not surface chart.title — leave default */
      }
    }
    if (opts.altText) {
      shape.altTextDescription = opts.altText;
    }
    if (opts.tags) {
      for (const [k, v] of Object.entries(opts.tags)) {
        try { shape.tags.add(k, v); } catch { /* graceful */ }
      }
    }
    shape.load("id");
    await context.sync();
    // Apply categorical palette to series (best-effort).
    await applyPaletteBestEffort(shape, palette, context);
  });
  return shape;
}

async function pickActiveSlide(context) {
  // Prefer the currently selected slide; fall back to slide 0.
  if (typeof context.presentation.getSelectedSlides === "function") {
    try {
      const sel = context.presentation.getSelectedSlides();
      sel.load("items/id");
      await context.sync();
      if (sel.items?.length) {
        return context.presentation.slides.getItem(sel.items[0].id);
      }
    } catch {
      /* fall through */
    }
  }
  return context.presentation.slides.getItemAt(0);
}

async function applyPaletteBestEffort(shape, palette, context) {
  if (!palette || palette.length === 0) return;
  try {
    const series = shape.chart.series;
    series.load("count");
    await context.sync();
    const n = series.count ?? 0;
    for (let i = 0; i < n; i++) {
      const s = series.getItemAt(i);
      const color = palette[i % palette.length];
      try {
        s.format.fill.setSolidColor(color);
      } catch {
        /* ignore — host may not expose series fill */
      }
    }
    await context.sync();
  } catch {
    /* host doesn't expose chart.series — skip silently */
  }
}
