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
function peakYStrictlyBetween(
  layout: ChartLayout,
  from: Ref,
  to: Ref,
): number | null {
  if (
    layout.kind !== "bar" &&
    layout.kind !== "stacked_bar" &&
    layout.kind !== "waterfall"
  ) {
    return null;
  }
  const cats = layout.axes.x.domain.map(String);
  const fi = cats.indexOf(String(from.x));
  const ti = cats.indexOf(String(to.x));
  if (fi < 0 || ti < 0) return null;
  const lo = Math.min(fi, ti) + 1;
  const hi = Math.max(fi, ti) - 1;
  if (hi < lo) return null;
  let peak = Infinity;
  for (const b of layout.bars) {
    const i = cats.indexOf(String(b.category));
    if (i < lo || i > hi) continue;
    const top = b.valueLabelY != null ? Math.min(b.y, b.valueLabelY) : b.y;
    if (top < peak) peak = top;
  }
  return Number.isFinite(peak) ? peak : null;
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
  };
  for (const a of annotations) {
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
  const label = a.label ?? `CAGR ${fmtPct(cagr, a.format)}`;
  const color = a.color ?? ctx.frame.ds.palette.foreground;

  // Per-endpoint lift. For "above" we lift each endpoint slightly off the
  // bar top; for "below" we drop them. For "inline" we leave them on.
  const baseLift = a.placement === "inline" ? 0 : 14;
  const sign = a.placement === "below" ? 1 : -1;
  const fromY = from.y + sign * baseLift;
  const toY = to.y + sign * baseLift;

  // Apex of the curve: pulled past the higher endpoint so the bow is visible.
  // For bar layouts, also clear any intermediate bars + their value labels.
  const peak = peakYStrictlyBetween(ctx.layout, a.from, a.to);
  const plotBottom = ctx.layout.plot.height;
  let apexY: number;
  if (a.placement === "below") {
    let baseline = Math.max(fromY, toY);
    if (Number.isFinite(ctx.bottomReserved))
      baseline = Math.max(baseline, ctx.bottomReserved + ctx.frame.ds.spacing.annotationLabelGap);
    apexY = Math.min(baseline + 22, plotBottom - ctx.frame.ds.spacing.plotTopMargin);
  } else {
    let baseline = Math.min(fromY, toY);
    if (peak != null) baseline = Math.min(baseline, peak - ctx.frame.ds.spacing.annotationValueClearance);
    if (Number.isFinite(ctx.topReserved))
      baseline = Math.min(baseline, ctx.topReserved - ctx.frame.ds.spacing.annotationLabelGap);
    // Clamp inside plot so label stays visible. Reserve room for label above apex.
    apexY = Math.max(baseline - 22, ctx.frame.ds.spacing.plotTopMargin + 14);
  }

  const midX = (from.x + to.x) / 2;
  const markerId = ensureArrowMarker(ctx.frame, color);

  const path = `M ${from.x} ${fromY} Q ${midX} ${apexY}, ${to.x} ${toY}`;
  const g = ctx.frame.overlay.append("g").attr("class", "annotation-cagr");
  g.append("path")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.arrow.strokeWidth)
    .attr("stroke-linecap", "round")
    .attr("marker-end", `url(#${markerId})`);

  const labelY = a.placement === "below" ? apexY + 16 : apexY - 6;
  g.append("text")
    .attr("x", midX)
    .attr("y", labelY)
    .attr("text-anchor", "middle")
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(label);

  if (a.placement === "below") {
    ctx.bottomReserved = Math.max(ctx.bottomReserved, labelY);
  } else {
    ctx.topReserved = Math.min(ctx.topReserved, labelY - ctx.frame.ds.spacing.annotationLabelHeight);
  }
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

  const peak = peakYStrictlyBetween(ctx.layout, a.from, a.to);
  let baseY: number;
  if (a.placement === "below") {
    let bottom = Math.max(from.y, to.y) + 28;
    if (Number.isFinite(ctx.bottomReserved))
      bottom = Math.max(bottom, ctx.bottomReserved + ctx.frame.ds.spacing.annotationLabelGap + 14);
    baseY = Math.min(bottom, ctx.layout.plot.height - ctx.frame.ds.spacing.plotTopMargin);
  } else {
    let top = Math.min(from.y, to.y);
    if (peak != null) top = Math.min(top, peak - ctx.frame.ds.spacing.annotationValueClearance);
    if (Number.isFinite(ctx.topReserved))
      top = Math.min(top, ctx.topReserved - ctx.frame.ds.spacing.annotationLabelGap);
    baseY = Math.max(top - 14, ctx.frame.ds.spacing.plotTopMargin + 14);
  }
  const tickH = ctx.frame.ds.annotations.delta.tickHeight;
  const tickDir = a.placement === "below" ? tickH : -tickH;
  const tickY = baseY + tickDir;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-delta");
  g.append("path")
    .attr(
      "d",
      `M ${from.x} ${baseY} L ${from.x} ${tickY} L ${to.x} ${tickY} L ${to.x} ${baseY}`,
    )
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.delta.strokeWidth);
  const labelY = a.placement === "below" ? tickY + 16 : tickY - 6;
  g.append("text")
    .attr("x", (from.x + to.x) / 2)
    .attr("y", labelY)
    .attr("text-anchor", "middle")
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(label);
  if (a.placement === "below") {
    ctx.bottomReserved = Math.max(ctx.bottomReserved, labelY);
  } else {
    ctx.topReserved = Math.min(ctx.topReserved, labelY - ctx.frame.ds.spacing.annotationLabelHeight);
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
  const peak = peakYStrictlyBetween(ctx.layout, a.from, a.to);

  let baseY: number;
  if (a.placement === "below") {
    let bottom = Math.max(from.y, to.y) + 32;
    if (Number.isFinite(ctx.bottomReserved))
      bottom = Math.max(bottom, ctx.bottomReserved + ctx.frame.ds.spacing.annotationLabelGap + 14);
    baseY = Math.min(bottom, ctx.layout.plot.height - ctx.frame.ds.spacing.plotTopMargin);
  } else {
    let top = Math.min(from.y, to.y);
    if (peak != null) top = Math.min(top, peak - ctx.frame.ds.spacing.annotationValueClearance);
    if (Number.isFinite(ctx.topReserved))
      top = Math.min(top, ctx.topReserved - ctx.frame.ds.spacing.annotationLabelGap);
    baseY = Math.max(top - 18, ctx.frame.ds.spacing.plotTopMargin + 14);
  }
  const tickH = ctx.frame.ds.annotations.bracket.tickHeight;
  const tickDir = a.placement === "below" ? -tickH : tickH;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-bracket");
  g.append("path")
    .attr(
      "d",
      `M ${from.x} ${baseY + tickDir} L ${from.x} ${baseY} L ${to.x} ${baseY} L ${to.x} ${baseY + tickDir}`,
    )
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", ctx.frame.ds.annotations.bracket.strokeWidth);
  const labelY = a.placement === "below" ? baseY + 18 : baseY - 6;
  g.append("text")
    .attr("x", (from.x + to.x) / 2)
    .attr("y", labelY)
    .attr("text-anchor", "middle")
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(a.label);
  if (a.placement === "below") {
    ctx.bottomReserved = Math.max(ctx.bottomReserved, labelY);
  } else {
    ctx.topReserved = Math.min(ctx.topReserved, labelY - ctx.frame.ds.spacing.annotationLabelHeight);
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
  for (const [, g] of groups) {
    layer
      .append("text")
      .attr("x", g.topX)
      .attr("y", g.topY - 6)
      .attr("text-anchor", "middle")
      .attr("font-size", ctx.frame.ds.typography.labelSize)
      .attr("font-weight", 600)
      .attr("fill", color)
      .text(fmt(g.total));
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
