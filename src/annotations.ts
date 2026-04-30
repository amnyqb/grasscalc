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

function ensureArrowMarker(
  frame: ChartFrame,
  id: string,
  color: string,
): void {
  const root = frame.svg;
  const existing = root.select(`defs marker#${id}`);
  if (!existing.empty()) return;
  let defs: any = root.select("defs");
  if ((defs as any).empty()) {
    defs = root.append("defs");
  }
  defs
    .append("marker")
    .attr("id", id)
    .attr("viewBox", "0 0 10 10")
    .attr("refX", 8)
    .attr("refY", 5)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto-start-reverse")
    .append("path")
    .attr("d", "M 0 0 L 10 5 L 0 10 z")
    .attr("fill", color);
}

interface ApplyContext {
  frame: ChartFrame;
  layout: ChartLayout;
}

export function applyAnnotations(
  ctx: ApplyContext,
  annotations: Annotation[],
): void {
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
  // Period count: for bar/line layouts, use category-index distance if available.
  const periods = inferPeriods(ctx.layout, a.from, a.to) ?? 1;
  const cagr = Math.pow(to.value / from.value, 1 / periods) - 1;
  const label = a.label ?? `CAGR ${fmtPct(cagr, a.format)}`;
  const color = a.color ?? ctx.frame.ds.palette.foreground;

  const offset =
    a.placement === "below" ? 24 : a.placement === "inline" ? 0 : -22;
  const y = Math.min(from.y, to.y) + offset;

  const markerId = `cagr-arrow-${Math.random().toString(36).slice(2, 8)}`;
  ensureArrowMarker(ctx.frame, markerId, color);

  const path = `M ${from.x} ${y} Q ${(from.x + to.x) / 2} ${y - 18}, ${to.x} ${y}`;
  const g = ctx.frame.overlay.append("g").attr("class", "annotation-cagr");
  g.append("path")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 1.5)
    .attr("marker-end", `url(#${markerId})`);
  g.append("text")
    .attr("x", (from.x + to.x) / 2)
    .attr("y", y - 22)
    .attr("text-anchor", "middle")
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(label);
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

  const baseY = Math.min(from.y, to.y) - (a.placement === "below" ? -24 : 14);
  const tickY = baseY - 6;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-delta");
  // Bracket: ⌐ ¬ shape with label centered above.
  g.append("path")
    .attr(
      "d",
      `M ${from.x} ${baseY} L ${from.x} ${tickY} L ${to.x} ${tickY} L ${to.x} ${baseY}`,
    )
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 1.25);
  g.append("text")
    .attr("x", (from.x + to.x) / 2)
    .attr("y", tickY - 6)
    .attr("text-anchor", "middle")
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(label);
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
  const baseY = Math.min(from.y, to.y) - (a.placement === "below" ? -28 : 18);
  const g = ctx.frame.overlay.append("g").attr("class", "annotation-bracket");
  g.append("path")
    .attr(
      "d",
      `M ${from.x} ${baseY + 6} L ${from.x} ${baseY} L ${to.x} ${baseY} L ${to.x} ${baseY + 6}`,
    )
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 1.25);
  g.append("text")
    .attr("x", (from.x + to.x) / 2)
    .attr("y", baseY - 6)
    .attr("text-anchor", "middle")
    .attr("font-size", ctx.frame.ds.typography.labelSize)
    .attr("font-weight", 600)
    .attr("fill", color)
    .text(a.label);
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
  const dx =
    a.placement === "left" ? -36 : a.placement === "right" ? 36 : 0;
  const dy =
    a.placement === "top" ? -28 : a.placement === "bottom" ? 28 : 0;
  const tx = anchor.x + dx;
  const ty = anchor.y + dy;

  const g = ctx.frame.overlay.append("g").attr("class", "annotation-callout");
  g.append("line")
    .attr("x1", anchor.x)
    .attr("y1", anchor.y)
    .attr("x2", tx)
    .attr("y2", ty)
    .attr("stroke", color)
    .attr("stroke-width", 1);
  g.append("circle")
    .attr("cx", anchor.x)
    .attr("cy", anchor.y)
    .attr("r", 3)
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
  const dash =
    a.style === "dotted" ? "1,3" : a.style === "solid" ? null : "5,4";
  const g = ctx.frame.overlay.append("g").attr("class", "annotation-refline");
  if (a.axis === "y") {
    g.append("line")
      .attr("x1", 0)
      .attr("x2", layout.plot.width)
      .attr("y1", pos)
      .attr("y2", pos)
      .attr("stroke", color)
      .attr("stroke-width", 1.25)
      .attr("stroke-dasharray", dash);
    if (a.label) {
      g.append("text")
        .attr("x", layout.plot.width - 4)
        .attr("y", pos - 4)
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
      .attr("stroke-width", 1.25)
      .attr("stroke-dasharray", dash);
    if (a.label) {
      g.append("text")
        .attr("x", pos + 4)
        .attr("y", 14)
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
