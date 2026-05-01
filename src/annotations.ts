import * as d3 from "d3";
import type {
  Annotation,
  ChartLayout,
  Ref,
  BarLayout,
  LineLayout,
  AreaLayout,
  ScatterLayout,
  PieLayout,
  AxisDescriptor,
} from "./types.js";
import type { ChartFrame } from "./charts/common.js";

interface Anchor {
  x: number;
  y: number;
  /** Underlying value (for label fallback). */
  value?: number;
}

/**
 * Resolve a {x, series, y} ref to a concrete point in plot-local coordinates.
 * Returns null if not found; caller should record a warning.
 */
export function locateRef(layout: ChartLayout, ref: Ref): Anchor | null {
  switch (layout.kind) {
    case "bar":
    case "stacked_bar":
    case "waterfall": {
      const bl = layout as BarLayout;
      const matches = bl.bars.filter((b) => {
        if (ref.x !== undefined && b.category !== ref.x) return false;
        if (ref.series !== undefined && b.series !== ref.series) return false;
        return true;
      });
      if (matches.length === 0) return null;
      const b = matches[0]!;
      return { x: b.top.x, y: b.top.y, value: b.value };
    }
    case "line":
    case "area": {
      const ll = layout as LineLayout | AreaLayout;
      const series =
        ref.series !== undefined
          ? ll.series.find((s) => s.name === ref.series)
          : ll.series[0];
      if (!series) return null;
      if (ref.x === undefined) {
        const last = series.points[series.points.length - 1];
        return last ? { x: last.x, y: last.y, value: last.yValue } : null;
      }
      const p = series.points.find((pt) => String(pt.xValue) === String(ref.x));
      return p ? { x: p.x, y: p.y, value: p.yValue } : null;
    }
    case "scatter": {
      const sl = layout as ScatterLayout;
      const series = ref.series
        ? sl.series.find((s) => s.name === ref.series)
        : sl.series[0];
      if (!series) return null;
      if (ref.x === undefined) return null;
      const p = series.points.find(
        (pt) => Math.abs(pt.xValue - Number(ref.x)) < 1e-9,
      );
      return p ? { x: p.x, y: p.y, value: p.yValue } : null;
    }
    case "pie": {
      const pl = layout as PieLayout;
      if (ref.x === undefined) return null;
      const slice = pl.slices.find((s) => s.label === ref.x);
      if (!slice) return null;
      // outerCentroid is given in svg coords, but our annotations operate in plot-local.
      return {
        x: slice.outerCentroid.x - pl.plot.x,
        y: slice.outerCentroid.y - pl.plot.y,
        value: slice.value,
      };
    }
  }
}

function fmtPct(p: number, spec: string): string {
  return d3.format(spec)(p);
}

function colorSlug(color: string): string {
  return color.replace(/[^a-zA-Z0-9]/g, "");
}

/**
 * Deterministic per-color marker id. Idempotent — repeated calls with the
 * same color reuse the existing <marker> definition. Marker size pulled
 * from the design system.
 */
function ensureArrowMarker(frame: ChartFrame, color: string): string {
  const size = frame.ds.annotations.arrow.markerSize;
  const id = `cs-arrow-${colorSlug(color)}-${size}`;
  const root = frame.svg;
  const existing = root.select(`defs marker#${id}`);
  if (!existing.empty()) return id;
  let defs: any = root.select("defs");
  if ((defs as any).empty()) {
    defs = root.append("defs");
  }
  defs
    .append("marker")
    .attr("id", id)
    .attr("viewBox", "0 0 10 10")
    .attr("refX", 9)
    .attr("refY", 5)
    .attr("markerWidth", size)
    .attr("markerHeight", size)
    .attr("markerUnits", "userSpaceOnUse")
    .attr("orient", "auto-start-reverse")
    .append("path")
    .attr("d", "M 0 0 L 10 5 L 0 10 z")
    .attr("fill", color);
  return id;
}

/**
 * Peak (smallest y, i.e. visually highest) among bars whose category
 * lies STRICTLY between `from` and `to`. Endpoints are excluded so the
 * caller's own lifted-endpoint clearance isn't double-counted. Returns
 * null if not a bar layout, refs don't resolve, or there are no
 * intermediate bars.
 */
/**
 * Topmost (smallest y, "above") or bottommost (largest y, "below") rendered
 * point at a single category — the bar tops, value labels above bars, and
 * the synthetic total label (if total_labels was requested) at that
 * category. Used to anchor vertical legs of CAGR/delta brackets so they
 * start above the data label, not behind it.
 */
function dataTopAtCategory(
  ctx: ApplyContext,
  category: string | number,
  placement: "above" | "below",
): number | null {
  const layout = ctx.layout;
  if (
    layout.kind !== "bar" &&
    layout.kind !== "stacked_bar" &&
    layout.kind !== "waterfall"
  ) {
    // Line/area: caller handles via the point's own y.
    return null;
  }
  const bars = layout.bars.filter(
    (b) => String(b.category) === String(category),
  );
  if (bars.length === 0) return null;
  const totalsPresent = ctx.annotations.some(
    (a) => a.type === "total_labels",
  );
  const labelSize = ctx.frame.ds.typography.labelSize;
  if (placement === "above") {
    let top = Math.min(
      ...bars.map((b) => (b.valueLabelY != null ? Math.min(b.y, b.valueLabelY) : b.y)),
    );
    if (totalsPresent) {
      // total_labels baseline = stackTop - 6; glyph top ≈ baseline - labelSize.
      const stackTop = Math.min(...bars.map((b) => b.y));
      top = Math.min(top, stackTop - 6 - labelSize);
    }
    return top;
  } else {
    return Math.max(...bars.map((b) => b.y + b.height));
  }
}

/**
 * Visual extreme-y across the inclusive [from..to] span. For an "above"
 * placement, returns the smallest y (highest visual point) across all bars
 * + their value labels + all line/area/scatter points in the span. For
 * "below" placement, returns the largest y (lowest visual point).
 *
 * Used by the angular CAGR/delta drawers so the rail clears every data
 * label in its span — including the endpoints themselves — not just the
 * intermediate points.
 */
function spanExtremeY(
  layout: ChartLayout,
  from: Ref,
  to: Ref,
  placement: "above" | "below",
): number | null {
  const cmp = (a: number, b: number): number =>
    placement === "above" ? Math.min(a, b) : Math.max(a, b);
  let extreme = placement === "above" ? Infinity : -Infinity;

  if (
    layout.kind === "bar" ||
    layout.kind === "stacked_bar" ||
    layout.kind === "waterfall"
  ) {
    const cats = layout.axes.x.domain.map(String);
    const fi = cats.indexOf(String(from.x));
    const ti = cats.indexOf(String(to.x));
    if (fi < 0 || ti < 0) return null;
    const lo = Math.min(fi, ti);
    const hi = Math.max(fi, ti);
    for (const b of layout.bars) {
      const i = cats.indexOf(String(b.category));
      if (i < lo || i > hi) continue;
      const candidate =
        placement === "above"
          ? b.valueLabelY != null
            ? Math.min(b.y, b.valueLabelY)
            : b.y
          : b.y + b.height;
      extreme = cmp(extreme, candidate);
    }
  } else if (layout.kind === "line" || layout.kind === "area") {
    const fxRaw = (from as any).x;
    const txRaw = (to as any).x;
    const numericSpan =
      typeof fxRaw === "number" && typeof txRaw === "number";
    const lo = numericSpan ? Math.min(fxRaw, txRaw) : -Infinity;
    const hi = numericSpan ? Math.max(fxRaw, txRaw) : Infinity;
    for (const s of layout.series) {
      for (const p of s.points) {
        if (numericSpan && typeof p.xValue === "number") {
          if (p.xValue < lo || p.xValue > hi) continue;
        }
        extreme = cmp(extreme, p.y);
      }
    }
  } else {
    return null;
  }

  return Number.isFinite(extreme) ? extreme : null;
}

// All annotation spacing now reads from ds.spacing — no magic numbers
// in this file.

interface ApplyContext {
  frame: ChartFrame;
  layout: ChartLayout;
  /**
   * Smallest y reserved by previously-placed "above" annotations.
   * Subsequent above-annotations lift themselves so their label top sits
   * at most `topReserved - ds.spacing.annotationLabelGap`.
   */
  topReserved: number;
  bottomReserved: number;
  /** Full annotation list — drawers can introspect to know e.g. whether
   *  total_labels was requested, so they can clear the totals' y zone
   *  at endpoint columns even when topReserved is the global min. */
  annotations: Annotation[];
}

export function applyAnnotations(
  partial: { frame: ChartFrame; layout: ChartLayout },
  annotations: Annotation[],
): void {
  const ctx: ApplyContext = {
    frame: partial.frame,
    layout: partial.layout,
    topReserved: Infinity,
    bottomReserved: -Infinity,
    annotations,
  };
  // Two-phase: place "background" annotations first (range bands, totals,
  // reference lines) so above/below-rail annotations (CAGR, delta, bracket,
  // callout) can reserve space against them. Otherwise CAGR draws first
  // and crashes through later total labels.
  const phase1: Annotation[] = annotations.filter(
    (a) =>
      a.type === "range_band" ||
      a.type === "total_labels" ||
      a.type === "reference_line",
  );
  const phase2: Annotation[] = annotations.filter((a) => !phase1.includes(a));
  for (const a of [...phase1, ...phase2]) {
    try {
      switch (a.type) {
        case "cagr_arrow":
          drawCagrArrow(ctx, a);
          break;
        case "delta":
          drawDelta(ctx, a);
          break;
        case "callout":
          drawCallout(ctx, a);
          break;
        case "reference_line":
          drawReferenceLine(ctx, a);
          break;
        case "range_band":
          drawRangeBand(ctx, a);
          break;
        case "total_labels":
          drawTotalLabels(ctx, a);
          break;
        case "bracket":
          drawBracket(ctx, a);
          break;
      }
    } catch (err) {
      ctx.frame.warnings.push(
        `Annotation ${a.type} failed: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
    }
  }
}

/**
 * Shared geometry for span-spanning annotations (cagr_arrow, delta, bracket).
 * Computes a horizontal "rail" y above (or below) all in-span data labels
 * with the user-spec clearances: 10pt between data labels and the rail,
 * and 10pt between the endpoint columns' data labels and where the
 * verticals start/end. Also computes the y for the annotation's text label
 * (6pt above the rail).
 *
 * Returns null if either ref doesn't resolve.
 */
interface RailGeometry {
  fromX: number;
  toX: number;
  fromY: number;
  toY: number;
  railY: number;
  midX: number;
  labelY: number;
  labelSize: number;
  placement: "above" | "below";
}

const DATA_LABEL_GAP = 10;
const LABEL_TO_RAIL_GAP = 6;

function computeRailGeometry(
  ctx: ApplyContext,
  fromRef: Ref,
  toRef: Ref,
  placement: "above" | "below",
): RailGeometry | null {
  const from = locateRef(ctx.layout, fromRef);
  const to = locateRef(ctx.layout, toRef);
  if (!from || !to) return null;
  const labelSize = ctx.frame.ds.typography.labelSize;

  const extreme = spanExtremeY(ctx.layout, fromRef, toRef, placement);

  let railY: number;
  if (placement === "above") {
    let baseline = Math.min(from.y, to.y);
    if (extreme != null) baseline = Math.min(baseline, extreme);
    if (Number.isFinite(ctx.topReserved)) {
      baseline = Math.min(
        baseline,
        ctx.topReserved - ctx.frame.ds.spacing.annotationLabelGap,
      );
    }
    railY = baseline - DATA_LABEL_GAP;
    railY = Math.max(
      railY,
      ctx.frame.ds.spacing.plotTopMargin + labelSize + LABEL_TO_RAIL_GAP,
    );
  } else {
    let baseline = Math.max(from.y, to.y);
    if (extreme != null) baseline = Math.max(baseline, extreme);
    if (Number.isFinite(ctx.bottomReserved)) {
      baseline = Math.max(
        baseline,
        ctx.bottomReserved + ctx.frame.ds.spacing.annotationLabelGap,
      );
    }
    railY = baseline + DATA_LABEL_GAP;
    railY = Math.min(
      railY,
      ctx.layout.plot.height -
        ctx.frame.ds.spacing.plotTopMargin -
        labelSize -
        LABEL_TO_RAIL_GAP,
    );
  }

  const fromTop =
    fromRef.x != null ? dataTopAtCategory(ctx, fromRef.x, placement) : null;
  const toTop =
    toRef.x != null ? dataTopAtCategory(ctx, toRef.x, placement) : null;
  const fromAnchor = fromTop ?? from.y;
  const toAnchor = toTop ?? to.y;
  const fromY =
    placement === "above"
      ? fromAnchor - DATA_LABEL_GAP
      : fromAnchor + DATA_LABEL_GAP;
  const toY =
    placement === "above"
      ? toAnchor - DATA_LABEL_GAP
      : toAnchor + DATA_LABEL_GAP;

  const labelY =
    placement === "above"
      ? railY - LABEL_TO_RAIL_GAP
      : railY + LABEL_TO_RAIL_GAP + labelSize;

  return {
    fromX: from.x,
    toX: to.x,
    fromY,
    toY,
    railY,
    midX: (from.x + to.x) / 2,
    labelY,
    labelSize,
    placement,
  };
}

function reserveAfterRail(ctx: ApplyContext, g: RailGeometry): void {
  if (g.placement === "above") {
    ctx.topReserved = Math.min(ctx.topReserved, g.labelY - g.labelSize);
  } else {
    ctx.bottomReserved = Math.max(ctx.bottomReserved, g.labelY);
  }
}

function drawCagrArrow(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "cagr_arrow" }>,
): void {
  const from = locateRef(ctx.layout, a.from);
  const to = locateRef(ctx.layout, a.to);
  if (!from || !to) {
    ctx.frame.warnings.push("cagr_arrow: could not resolve from/to refs.");
    return;
  }
  if (from.value == null || to.value == null || from.value === 0) {
    ctx.frame.warnings.push("cagr_arrow: missing or zero base value.");
    return;
  }
  const periods = inferPeriods(ctx.layout, a.from, a.to) ?? 1;
  const cagr = Math.pow(to.value / from.value, 1 / periods) - 1;
  const trendUp = to.value >= from.value;
  const label = a.label ?? `CAGR ${fmtPct(cagr, a.format)}`;
  const color = a.color ?? ctx.frame.ds.palette.foreground;
  const placement: "above" | "below" =
    a.placement === "below" ? "below" : "above";

  const geo = computeRailGeometry(ctx, a.from, a.to, placement);
  if (!geo) {
    ctx.frame.warnings.push("cagr_arrow: could not compute geometry.");
    return;
  }

  // Angular stairstep: vertical → horizontal rail → vertical down to to.y.
  // Marker-end orientation is determined by the last segment, which always
  // ends running toward to.y → arrow visually "lands" on the to anchor.
  const path =
    `M ${geo.fromX} ${geo.fromY} ` +
    `L ${geo.fromX} ${geo.railY} ` +
    `L ${geo.toX} ${geo.railY} ` +
    `L ${geo.toX} ${geo.toY}`;

  const markerId = ensureArrowMarker(ctx.frame, color);
  const g = ctx.frame.overlay.append("g").attr("class", "annotation-cagr");
  g.append("path")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.arrow.strokeWidth)
    .attr("stroke-linejoin", "miter")
    .attr("stroke-linecap", "butt")
    .attr("marker-end", `url(#${markerId})`);

  g.append("text")
    .attr("x", geo.midX)
    .attr("y", geo.labelY)
    .attr("text-anchor", "middle")
    .attr("font-size", geo.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(label);

  if (!trendUp) g.append("title").text(`Down trend (${label})`);

  reserveAfterRail(ctx, geo);
}

function drawDelta(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "delta" }>,
): void {
  const from = locateRef(ctx.layout, a.from);
  const to = locateRef(ctx.layout, a.to);
  if (!from || !to || from.value == null || to.value == null) {
    ctx.frame.warnings.push("delta: could not resolve refs/values.");
    return;
  }
  const delta = to.value - from.value;
  const label = d3.format(a.format)(delta);
  const color = a.color ?? ctx.frame.ds.palette.foreground;
  const placement: "above" | "below" =
    a.placement === "below" ? "below" : "above";

  const geo = computeRailGeometry(ctx, a.from, a.to, placement);
  if (!geo) {
    ctx.frame.warnings.push("delta: could not compute geometry.");
    return;
  }

  // Bracket shape: tiny tick at each end pointing TOWARD the data, with the
  // rail running between them. The 10pt data-label gap must apply to the
  // outermost geometry — i.e. the tick TIPS, not the rail. So we lift the
  // rail by tickH above the geometry baseline; tickEndY then lands exactly
  // at the user-spec 10pt clearance.
  const tickH = ctx.frame.ds.annotations.delta.tickHeight;
  const tickDir = placement === "above" ? tickH : -tickH;
  const railY = geo.railY - tickDir; // bump away from data
  const tickEndY = geo.railY; // tip at the original rail = 10pt off labels
  const labelY =
    placement === "above"
      ? railY - LABEL_TO_RAIL_GAP
      : railY + LABEL_TO_RAIL_GAP + geo.labelSize;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-delta");
  g.append("path")
    .attr(
      "d",
      `M ${geo.fromX} ${tickEndY} L ${geo.fromX} ${railY} ` +
        `L ${geo.toX} ${railY} L ${geo.toX} ${tickEndY}`,
    )
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.delta.strokeWidth)
    .attr("stroke-linejoin", "miter")
    .attr("stroke-linecap", "butt");

  g.append("text")
    .attr("x", geo.midX)
    .attr("y", labelY)
    .attr("text-anchor", "middle")
    .attr("font-size", geo.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(label);

  // Reserve up through the label, accounting for the bumped rail.
  if (placement === "above") {
    ctx.topReserved = Math.min(ctx.topReserved, labelY - geo.labelSize);
  } else {
    ctx.bottomReserved = Math.max(ctx.bottomReserved, labelY);
  }
}

function drawBracket(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "bracket" }>,
): void {
  const from = locateRef(ctx.layout, a.from);
  const to = locateRef(ctx.layout, a.to);
  if (!from || !to) {
    ctx.frame.warnings.push("bracket: could not resolve refs.");
    return;
  }
  const color = a.color ?? ctx.frame.ds.palette.foreground;
  const placement: "above" | "below" =
    a.placement === "below" ? "below" : "above";

  const geo = computeRailGeometry(ctx, a.from, a.to, placement);
  if (!geo) {
    ctx.frame.warnings.push("bracket: could not compute geometry.");
    return;
  }

  // Same shape as drawDelta. The 10pt data-label gap applies to the tick
  // tips (outermost geometry), so the rail is bumped tickH away.
  const tickH = ctx.frame.ds.annotations.bracket.tickHeight;
  const tickDir = placement === "above" ? tickH : -tickH;
  const railY = geo.railY - tickDir;
  const tickEndY = geo.railY;
  const labelY =
    placement === "above"
      ? railY - LABEL_TO_RAIL_GAP
      : railY + LABEL_TO_RAIL_GAP + geo.labelSize;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-bracket");
  g.append("path")
    .attr(
      "d",
      `M ${geo.fromX} ${tickEndY} L ${geo.fromX} ${railY} ` +
        `L ${geo.toX} ${railY} L ${geo.toX} ${tickEndY}`,
    )
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.bracket.strokeWidth)
    .attr("stroke-linejoin", "miter")
    .attr("stroke-linecap", "butt");

  g.append("text")
    .attr("x", geo.midX)
    .attr("y", labelY)
    .attr("text-anchor", "middle")
    .attr("font-size", geo.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(a.label);

  if (placement === "above") {
    ctx.topReserved = Math.min(ctx.topReserved, labelY - geo.labelSize);
  } else {
    ctx.bottomReserved = Math.max(ctx.bottomReserved, labelY);
  }
}

function drawCallout(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "callout" }>,
): void {
  const anchor = locateRef(ctx.layout, a.anchor);
  if (!anchor) {
    ctx.frame.warnings.push("callout: could not resolve anchor.");
    return;
  }
  const color = a.color ?? ctx.frame.ds.palette.foreground;
  // Leader-line lengths governed by the design system.
  const dxBase = ctx.frame.ds.spacing.calloutDx;
  const dyBase = ctx.frame.ds.spacing.calloutDy;
  const dx =
    a.placement === "left" ? -dxBase : a.placement === "right" ? dxBase : 0;
  const dy =
    a.placement === "top" ? -dyBase : a.placement === "bottom" ? dyBase : 0;
  const tx = anchor.x + dx;
  const ty = anchor.y + dy;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-callout");
  g.append("line")
    .attr("x1", anchor.x)
    .attr("y1", anchor.y)
    .attr("x2", tx)
    .attr("y2", ty)
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.callout.strokeWidth);
  g.append("circle")
    .attr("cx", anchor.x)
    .attr("cy", anchor.y)
    .attr("r", ctx.frame.ds.annotations.callout.dotRadius)
    .attr("fill", color);
  g.append("text")
    .attr("x", tx)
    .attr("y", ty)
    .attr(
      "text-anchor",
      a.placement === "right"
        ? "start"
        : a.placement === "left"
          ? "end"
          : "middle",
    )
    .attr("dy", a.placement === "bottom" ? 14 : 0)
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 500)
    .attr("fill", color)
    .text(a.text);
}

function drawReferenceLine(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "reference_line" }>,
): void {
  if (!("axes" in ctx.layout)) {
    ctx.frame.warnings.push("reference_line: layout has no axes.");
    return;
  }
  const layout = ctx.layout as Exclude<ChartLayout, PieLayout>;
  const axis = a.axis === "x" ? layout.axes.x : layout.axes.y;
  const pos = positionOnAxis(axis, a.value);
  if (pos == null) {
    ctx.frame.warnings.push(
      `reference_line: could not place ${a.value} on ${a.axis} axis.`,
    );
    return;
  }
  const color = a.color ?? ctx.frame.ds.palette.muted;
  // Style: caller's a.style wins; otherwise the design system's default.
  const style = a.style ?? ctx.frame.ds.annotations.referenceLine.defaultStyle;
  const dash =
    style === "dotted" ? "1,3" : style === "solid" ? null : "5,4";
  const labelGap = ctx.frame.ds.spacing.referenceLineLabelGap;
  const stroke = ctx.frame.ds.annotations.referenceLine.strokeWidth;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-refline");
  if (a.axis === "y") {
    g.append("line")
      .attr("x1", 0)
      .attr("x2", layout.plot.width)
      .attr("y1", pos)
      .attr("y2", pos)
      .attr("stroke", color)
      .attr("stroke-width", stroke)
      .attr("stroke-dasharray", dash);
    if (a.label) {
      g.append("text")
        .attr("x", layout.plot.width - labelGap)
        .attr("y", pos - labelGap)
        .attr("text-anchor", "end")
        .attr("font-size", ctx.frame.ds.typography.labelSize)
        .attr("fill", color)
        .text(a.label);
    }
  } else {
    g.append("line")
      .attr("y1", 0)
      .attr("y2", layout.plot.height)
      .attr("x1", pos)
      .attr("x2", pos)
      .attr("stroke", color)
      .attr("stroke-width", stroke)
      .attr("stroke-dasharray", dash);
    if (a.label) {
      g.append("text")
        .attr("x", pos + labelGap)
        .attr("y", ctx.frame.ds.typography.labelSize)
        .attr("font-size", ctx.frame.ds.typography.labelSize)
        .attr("fill", color)
        .text(a.label);
    }
  }
}

function drawRangeBand(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "range_band" }>,
): void {
  if (!("axes" in ctx.layout)) {
    ctx.frame.warnings.push("range_band: layout has no axes.");
    return;
  }
  const layout = ctx.layout as Exclude<ChartLayout, PieLayout>;
  const axis = a.axis === "x" ? layout.axes.x : layout.axes.y;
  const pFrom = positionOnAxis(axis, a.from);
  const pTo = positionOnAxis(axis, a.to);
  if (pFrom == null || pTo == null) {
    ctx.frame.warnings.push("range_band: could not place from/to.");
    return;
  }
  const color = a.color ?? ctx.frame.ds.palette.foreground;
  const g = ctx.frame.overlay.append("g").attr("class", "annotation-band");
  if (a.axis === "x") {
    const x = Math.min(pFrom, pTo);
    const w = Math.abs(pTo - pFrom);
    g.append("rect")
      .attr("x", x)
      .attr("y", 0)
      .attr("width", w)
      .attr("height", layout.plot.height)
      .attr("fill", color)
      .attr("opacity", a.opacity);
    if (a.label) {
      g.append("text")
        .attr("x", x + w / 2)
        .attr("y", 14)
        .attr("text-anchor", "middle")
        .attr("font-size", ctx.frame.ds.typography.labelSize)
        .attr("fill", color)
        .text(a.label);
    }
  } else {
    const y = Math.min(pFrom, pTo);
    const h = Math.abs(pTo - pFrom);
    g.append("rect")
      .attr("x", 0)
      .attr("y", y)
      .attr("width", layout.plot.width)
      .attr("height", h)
      .attr("fill", color)
      .attr("opacity", a.opacity);
    if (a.label) {
      g.append("text")
        .attr("x", 4)
        .attr("y", y + 14)
        .attr("font-size", ctx.frame.ds.typography.labelSize)
        .attr("fill", color)
        .text(a.label);
    }
  }
}

function drawTotalLabels(
  ctx: ApplyContext,
  a: Extract<Annotation, { type: "total_labels" }>,
): void {
  if (
    ctx.layout.kind !== "stacked_bar" &&
    ctx.layout.kind !== "bar" &&
    ctx.layout.kind !== "waterfall"
  ) {
    ctx.frame.warnings.push("total_labels: only applies to bar layouts.");
    return;
  }
  const bl = ctx.layout as BarLayout;
  const fmt = d3.format(a.format);
  const color = a.color ?? ctx.frame.ds.palette.foreground;

  // Group by category; for stacked, sum series; for grouped/single, also works.
  const groups = new Map<string | number, { total: number; topY: number; topX: number; w: number }>();
  for (const b of bl.bars) {
    if (b.isTotal) continue; // waterfall totals are already labeled
    const g = groups.get(b.category);
    if (!g) {
      groups.set(b.category, {
        total: b.value,
        topY: b.y,
        topX: b.top.x,
        w: b.width,
      });
    } else {
      g.total += b.value;
      g.topY = Math.min(g.topY, b.y);
    }
  }

  const layer = ctx.frame.overlay
    .append("g")
    .attr("class", "annotation-totals");
  let topmostLabelTop = Infinity;
  for (const [, g] of groups) {
    const labelBaselineY = g.topY - 6;
    layer
      .append("text")
      .attr("x", g.topX)
      .attr("y", labelBaselineY)
      .attr("text-anchor", "middle")
      .attr("font-size", ctx.frame.ds.typography.labelSize)
      .attr("font-weight", 600)
      .attr("fill", color)
      .text(fmt(g.total));
    // Top of the rendered label glyphs ≈ baseline - labelSize.
    topmostLabelTop = Math.min(
      topmostLabelTop,
      labelBaselineY - ctx.frame.ds.typography.labelSize,
    );
  }
  // Reserve so subsequent annotations (CAGR, delta, bracket) clear the
  // total labels rather than crashing through them.
  if (Number.isFinite(topmostLabelTop)) {
    ctx.topReserved = Math.min(ctx.topReserved, topmostLabelTop);
  }
}

function positionOnAxis(
  axis: AxisDescriptor,
  value: string | number,
): number | null {
  if (axis.scale === "linear" || axis.scale === "time") {
    const [d0, d1] = axis.domain as [number, number];
    const [r0, r1] = axis.range;
    const v = Number(value);
    if (Number.isNaN(v)) return null;
    return r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  }
  // band/point: tick lookup
  const t = axis.ticks.find((tk) => String(tk.value) === String(value));
  return t ? t.pos : null;
}

function inferPeriods(
  layout: ChartLayout,
  from: Ref,
  to: Ref,
): number | null {
  const cats = (layout as any).axes?.x?.domain;
  if (!Array.isArray(cats)) return null;
  const i = cats.findIndex((c) => String(c) === String(from.x));
  const j = cats.findIndex((c) => String(c) === String(to.x));
  if (i < 0 || j < 0) return null;
  return Math.abs(j - i);
}
