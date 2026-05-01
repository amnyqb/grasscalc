import { JSDOM } from "jsdom";
import * as d3 from "d3";
import type { DesignSystem } from "../design-system.js";
import type { Rect, AxisDescriptor } from "../types.js";

export interface ChartFrame {
  document: Document;
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  inner: d3.Selection<SVGGElement, unknown, null, undefined>;
  /** Annotation overlay group, drawn on top of base chart. */
  overlay: d3.Selection<SVGGElement, unknown, null, undefined>;
  widthPt: number;
  heightPt: number;
  innerWidth: number;
  innerHeight: number;
  plot: Rect;
  ds: DesignSystem;
  warnings: string[];
  hasSource: boolean;
}

export interface FrameOptions {
  title?: string;
  subtitle?: string;
  source?: string;
  description?: string;
  background?: "default" | "transparent";
  /** Extra padding ADDED to ds.layout.padding (per side, in pt). Used by
   *  renderers that need to reserve room for content sized at runtime —
   *  e.g. line charts with `showEndpointLabels` need extra right padding
   *  big enough to fit the longest series label. */
  paddingExtra?: { top?: number; right?: number; bottom?: number; left?: number };
}

// All header/footer/legend spacing now reads from ds.spacing — no magic
// numbers in this file.

export function createFrame(
  ds: DesignSystem,
  widthPt: number,
  heightPt: number,
  options: FrameOptions = {},
): ChartFrame {
  const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
  const document = dom.window.document;

  const svg = d3
    .select(document.body)
    .append("svg")
    .attr("xmlns", "http://www.w3.org/2000/svg")
    .attr("width", widthPt)
    .attr("height", heightPt)
    .attr("viewBox", `0 0 ${widthPt} ${heightPt}`)
    .attr("font-family", ds.typography.fontFamily)
    .attr("role", "img") as unknown as d3.Selection<
    SVGSVGElement,
    unknown,
    null,
    undefined
  >;

  // a11y: <title> / <desc> for screen readers + PowerPoint alt text.
  if (options.title) {
    svg.append("title").text(options.title);
  }
  if (options.description) {
    svg.append("desc").text(options.description);
  }

  if (options.background !== "transparent") {
    svg
      .append("rect")
      .attr("width", widthPt)
      .attr("height", heightPt)
      .attr("fill", ds.palette.background);
  }

  // Title (pinned per the design system, regardless of annotation-driven
  // padding bumps). Subtitle sits just below using ds.spacing.subtitleGap.
  if (options.title) {
    const titleY = ds.spacing.titleTopMargin + ds.typography.titleSize;
    svg
      .append("text")
      .attr("class", "chart-title")
      .attr("x", ds.layout.padding.left)
      .attr("y", titleY)
      .attr("font-size", ds.typography.titleSize)
      .attr("font-weight", ds.typography.titleWeight)
      .attr("fill", ds.palette.foreground)
      .text(options.title);

    if (options.subtitle) {
      svg
        .append("text")
        .attr("class", "chart-subtitle")
        .attr("x", ds.layout.padding.left)
        .attr("y", titleY + ds.typography.labelSize + ds.spacing.subtitleGap)
        .attr("font-size", ds.typography.labelSize)
        .attr("font-weight", 400)
        .attr("fill", ds.palette.muted)
        .text(options.subtitle);
    }
  }

  // Source / footnote anchored to the bottom-left.
  if (options.source) {
    svg
      .append("text")
      .attr("class", "chart-source")
      .attr("x", ds.layout.padding.left)
      .attr("y", heightPt - ds.spacing.sourceBottomMargin)
      .attr("font-size", ds.typography.tickSize)
      .attr("font-weight", 400)
      .attr("fill", ds.palette.muted)
      .text(options.source);
  }

  // Effective padding: ds.layout.padding + per-side runtime overrides
  // (paddingExtra) + the source-line reserve at the bottom.
  const extra = options.paddingExtra ?? {};
  const padTop = ds.layout.padding.top + (extra.top ?? 0);
  const padRight = ds.layout.padding.right + (extra.right ?? 0);
  const padBottom = ds.layout.padding.bottom + (extra.bottom ?? 0);
  const padLeft = ds.layout.padding.left + (extra.left ?? 0);
  const sourceReserve = options.source
    ? ds.spacing.legendBottomMarginWithSource - ds.spacing.legendBottomMargin
    : 0;
  const effectiveBottom = padBottom + sourceReserve;

  const innerWidth = widthPt - padLeft - padRight;
  const innerHeight = heightPt - padTop - effectiveBottom;

  const inner = svg
    .append("g")
    .attr("class", "chart-inner")
    .attr("transform", `translate(${padLeft},${padTop})`) as unknown as d3.Selection<
    SVGGElement,
    unknown,
    null,
    undefined
  >;

  const overlay = svg
    .append("g")
    .attr("class", "chart-overlay")
    .attr("transform", `translate(${padLeft},${padTop})`) as unknown as d3.Selection<
    SVGGElement,
    unknown,
    null,
    undefined
  >;

  const plot: Rect = {
    x: padLeft,
    y: padTop,
    width: innerWidth,
    height: innerHeight,
  };

  return {
    document,
    svg,
    inner,
    overlay,
    widthPt,
    heightPt,
    innerWidth,
    innerHeight,
    plot,
    ds,
    warnings: [],
    hasSource: Boolean(options.source),
  };
}

export function drawAxes(
  frame: ChartFrame,
  xScale: any,
  yScale: any,
  options: {
    xLabel?: string;
    yLabel?: string;
    xTickFormat?: (d: any) => string;
    yTickFormat?: (d: any) => string;
  } = {},
): void {
  const { inner, innerWidth, innerHeight, ds } = frame;

  if (ds.axes.showGridY) {
    const ticks =
      typeof yScale.ticks === "function" ? yScale.ticks(5) : yScale.domain();
    inner
      .append("g")
      .attr("class", "grid-y")
      .selectAll("line")
      .data(ticks)
      .enter()
      .append("line")
      .attr("x1", 0)
      .attr("x2", innerWidth)
      .attr("y1", (d: any) => yScale(d) as number)
      .attr("y2", (d: any) => yScale(d) as number)
      .attr("stroke", ds.palette.grid)
      .attr("stroke-width", 1);
  }

  const xAxis = d3.axisBottom(xScale).tickSize(ds.axes.tickLength);
  if (options.xTickFormat) xAxis.tickFormat(options.xTickFormat as any);

  inner
    .append("g")
    .attr("class", "axis-x")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(xAxis as any)
    .call((g) =>
      g
        .select(".domain")
        .attr("stroke", ds.palette.foreground)
        .attr("stroke-width", ds.axes.axisLineWidth),
    )
    .call((g) =>
      g
        .selectAll(".tick text")
        .attr("font-size", ds.typography.tickSize)
        .attr("fill", ds.palette.muted),
    )
    .call((g) => g.selectAll(".tick line").attr("stroke", ds.palette.muted));

  const yAxis = d3.axisLeft(yScale).tickSize(ds.axes.tickLength);
  if (options.yTickFormat) yAxis.tickFormat(options.yTickFormat as any);

  inner
    .append("g")
    .attr("class", "axis-y")
    .call(yAxis as any)
    .call((g) =>
      g
        .select(".domain")
        .attr("stroke", ds.palette.foreground)
        .attr("stroke-width", ds.axes.axisLineWidth),
    )
    .call((g) =>
      g
        .selectAll(".tick text")
        .attr("font-size", ds.typography.tickSize)
        .attr("fill", ds.palette.muted),
    )
    .call((g) => g.selectAll(".tick line").attr("stroke", ds.palette.muted));

  if (options.xLabel) {
    inner
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 40)
      .attr("text-anchor", "middle")
      .attr("font-size", ds.typography.labelSize)
      .attr("font-weight", ds.typography.labelWeight)
      .attr("fill", ds.palette.foreground)
      .text(options.xLabel);
  }
  if (options.yLabel) {
    inner
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -44)
      .attr("text-anchor", "middle")
      .attr("font-size", ds.typography.labelSize)
      .attr("font-weight", ds.typography.labelWeight)
      .attr("fill", ds.palette.foreground)
      .text(options.yLabel);
  }
}

export function drawLegend(
  frame: ChartFrame,
  entries: { label: string; color: string }[],
): void {
  const { svg, ds, widthPt, hasSource } = frame;
  const legendY = hasSource
    ? frame.heightPt - ds.spacing.legendBottomMarginWithSource
    : frame.heightPt - ds.spacing.legendBottomMargin;
  const g = svg
    .append("g")
    .attr("class", "legend")
    .attr("transform", `translate(${ds.layout.padding.left}, ${legendY})`);
  let cursor = 0;
  for (const e of entries) {
    const item = g.append("g").attr("transform", `translate(${cursor},0)`);
    item
      .append("rect")
      .attr("width", 12)
      .attr("height", 12)
      .attr("y", -10)
      .attr("rx", ds.layout.cornerRadius)
      .attr("fill", e.color);
    const text = item
      .append("text")
      .attr("x", 16)
      .attr("font-size", ds.typography.labelSize)
      .attr("fill", ds.palette.foreground)
      .text(e.label);
    const node = text.node();
    const w = node?.getComputedTextLength?.() ?? e.label.length * 7;
    cursor += 16 + w + 18;
    if (cursor > widthPt - ds.layout.padding.left - ds.layout.padding.right) {
      frame.warnings.push("Legend wrapped — some series may be hidden.");
      break;
    }
  }
}

export function buildAxisDescriptor(
  scale: any,
  range: [number, number],
  formatter?: (d: any) => string,
): AxisDescriptor {
  const ticks =
    typeof scale.ticks === "function"
      ? scale.ticks(5)
      : typeof scale.domain === "function"
        ? scale.domain()
        : [];
  const fmt =
    formatter ??
    (typeof scale.tickFormat === "function" ? scale.tickFormat() : String);
  const kind: AxisDescriptor["scale"] =
    typeof scale.bandwidth === "function"
      ? "band"
      : typeof scale.step === "function"
        ? "point"
        : "linear";
  return {
    scale: kind,
    domain: scale.domain ? [...scale.domain()] : [],
    range,
    ticks: ticks.map((t: any) => ({
      value: t,
      pos: scale(t) as number,
      label: String(fmt(t)),
    })),
  };
}

export function serialize(frame: ChartFrame): string {
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    (frame.svg.node()?.outerHTML ?? "")
  );
}
