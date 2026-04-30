import { JSDOM } from "jsdom";
import * as d3 from "d3";
import type { DesignSystem } from "../design-system.js";

export interface ChartFrame {
  document: Document;
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  inner: d3.Selection<SVGGElement, unknown, null, undefined>;
  width: number;
  height: number;
  innerWidth: number;
  innerHeight: number;
  ds: DesignSystem;
}

export function createFrame(
  ds: DesignSystem,
  width: number,
  height: number,
  title?: string,
): ChartFrame {
  const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
  const document = dom.window.document;

  const svg = d3
    .select(document.body)
    .append("svg")
    .attr("xmlns", "http://www.w3.org/2000/svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("font-family", ds.typography.fontFamily) as unknown as d3.Selection<
    SVGSVGElement,
    unknown,
    null,
    undefined
  >;

  svg
    .append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", ds.palette.background);

  if (title) {
    svg
      .append("text")
      .attr("x", ds.layout.padding.left)
      .attr("y", ds.layout.padding.top - 12)
      .attr("font-size", ds.typography.titleSize)
      .attr("font-weight", ds.typography.titleWeight)
      .attr("fill", ds.palette.foreground)
      .text(title);
  }

  const innerWidth =
    width - ds.layout.padding.left - ds.layout.padding.right;
  const innerHeight =
    height - ds.layout.padding.top - ds.layout.padding.bottom;

  const inner = svg
    .append("g")
    .attr(
      "transform",
      `translate(${ds.layout.padding.left},${ds.layout.padding.top})`,
    ) as unknown as d3.Selection<SVGGElement, unknown, null, undefined>;

  return { document, svg, inner, width, height, innerWidth, innerHeight, ds };
}

export function drawAxes(
  frame: ChartFrame,
  xScale: any,
  yScale: any,
  options: { xLabel?: string; yLabel?: string; xTickFormat?: (d: any) => string } = {},
): void {
  const { inner, innerWidth, innerHeight, ds } = frame;

  if (ds.axes.showGridY) {
    inner
      .append("g")
      .attr("class", "grid-y")
      .selectAll("line")
      .data((yScale as d3.ScaleLinear<number, number>).ticks?.(5) ?? [])
      .enter()
      .append("line")
      .attr("x1", 0)
      .attr("x2", innerWidth)
      .attr("y1", (d) => yScale(d as any) as number)
      .attr("y2", (d) => yScale(d as any) as number)
      .attr("stroke", ds.palette.grid)
      .attr("stroke-width", 1);
  }

  const xAxis = d3.axisBottom(xScale as any).tickSize(ds.axes.tickLength);
  if (options.xTickFormat) xAxis.tickFormat(options.xTickFormat as any);

  inner
    .append("g")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(xAxis as any)
    .call((g) =>
      g.select(".domain").attr("stroke", ds.palette.foreground).attr(
        "stroke-width",
        ds.axes.axisLineWidth,
      ),
    )
    .call((g) =>
      g
        .selectAll(".tick text")
        .attr("font-size", ds.typography.tickSize)
        .attr("fill", ds.palette.muted),
    )
    .call((g) => g.selectAll(".tick line").attr("stroke", ds.palette.muted));

  const yAxis = d3.axisLeft(yScale as any).tickSize(ds.axes.tickLength);
  inner
    .append("g")
    .call(yAxis as any)
    .call((g) =>
      g.select(".domain").attr("stroke", ds.palette.foreground).attr(
        "stroke-width",
        ds.axes.axisLineWidth,
      ),
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
      .attr("y", innerHeight + 36)
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
      .attr("y", -40)
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
  const { svg, ds, width } = frame;
  const g = svg
    .append("g")
    .attr(
      "transform",
      `translate(${ds.layout.padding.left}, ${frame.height - 16})`,
    );
  let cursor = 0;
  for (const e of entries) {
    const item = g.append("g").attr("transform", `translate(${cursor},0)`);
    item
      .append("rect")
      .attr("width", 10)
      .attr("height", 10)
      .attr("y", -9)
      .attr("rx", ds.layout.cornerRadius)
      .attr("fill", e.color);
    const text = item
      .append("text")
      .attr("x", 14)
      .attr("font-size", ds.typography.labelSize)
      .attr("fill", ds.palette.foreground)
      .text(e.label);
    const node = text.node();
    const w = node?.getComputedTextLength?.() ?? e.label.length * 6;
    cursor += 14 + w + 16;
    if (cursor > width - ds.layout.padding.left - ds.layout.padding.right) break;
  }
}

export function serialize(frame: ChartFrame): string {
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    (frame.svg.node()?.outerHTML ?? "")
  );
}
