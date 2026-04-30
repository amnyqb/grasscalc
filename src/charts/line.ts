import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import type { LineLayout, LinePointRef } from "../types.js";
import {
  ChartFrame,
  buildAxisDescriptor,
  createFrame,
  drawAxes,
  drawLegend,
} from "./common.js";

export const LineChartSchema = z.object({
  type: z.literal("line"),
  title: z.string().optional(),
  description: z.string().optional(),
  widthPt: z.number().int().positive().default(720),
  heightPt: z.number().int().positive().default(420),
  background: z.enum(["default", "transparent"]).default("default"),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  showPoints: z.boolean().default(false),
  smoothing: z.enum(["linear", "monotone", "step"]).default("linear"),
  showEndpointLabels: z.boolean().default(false),
  showLastValueOnly: z.boolean().default(false),
  valueFormat: z.string().default(",.0f"),
  series: z
    .array(
      z.object({
        name: z.string(),
        points: z
          .array(
            z.object({
              x: z.union([z.number(), z.string()]),
              y: z.number(),
            }),
          )
          .min(1),
      }),
    )
    .min(1),
});

export type LineChartInput = z.infer<typeof LineChartSchema>;

export interface RenderResult {
  frame: ChartFrame;
  layout: LineLayout;
}

export function renderLine(
  input: LineChartInput,
  ds: DesignSystem,
): RenderResult {
  const frame = createFrame(ds, input.widthPt, input.heightPt, {
    title: input.title,
    description: input.description,
    background: input.background,
  });
  const { inner, innerWidth, innerHeight } = frame;
  const colors = ds.palette.categorical;
  const fmt = d3.format(input.valueFormat);

  const allPoints = input.series.flatMap((s) => s.points);
  const xValues = allPoints.map((p) => p.x);
  const xIsNumeric = xValues.every((v) => typeof v === "number");

  let xScale: any;
  if (xIsNumeric) {
    const xs = xValues as number[];
    xScale = d3
      .scaleLinear()
      .domain([d3.min(xs)!, d3.max(xs)!])
      .nice()
      .range([0, innerWidth]);
  } else {
    const cats = Array.from(new Set(xValues.map(String)));
    xScale = d3
      .scalePoint<string>()
      .domain(cats)
      .range([0, innerWidth])
      .padding(0.5);
  }

  const ys = allPoints.map((p) => p.y);
  const yMin = Math.min(0, d3.min(ys) ?? 0);
  const yScale = d3
    .scaleLinear()
    .domain([yMin, d3.max(ys) ?? 1])
    .nice()
    .range([innerHeight, 0]);

  drawAxes(frame, xScale, yScale, {
    xLabel: input.xLabel,
    yLabel: input.yLabel,
    yTickFormat: fmt as any,
  });

  const curve =
    input.smoothing === "monotone"
      ? d3.curveMonotoneX
      : input.smoothing === "step"
        ? d3.curveStepAfter
        : d3.curveLinear;

  const lineGen = d3
    .line<{ x: number | string; y: number }>()
    .x((d) => xScale(xIsNumeric ? d.x : String(d.x)) as number)
    .y((d) => yScale(d.y) as number)
    .curve(curve);

  const layoutSeries: LineLayout["series"] = [];

  input.series.forEach((s, i) => {
    const color = colors[i % colors.length]!;
    inner
      .append("path")
      .datum(s.points)
      .attr("fill", "none")
      .attr("stroke", color)
      .attr("stroke-width", ds.series.strokeWidth)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", lineGen as any);

    const points: LinePointRef[] = s.points.map((p) => ({
      xValue: p.x,
      yValue: p.y,
      x: xScale(xIsNumeric ? p.x : String(p.x)) as number,
      y: yScale(p.y) as number,
    }));

    if (input.showPoints) {
      inner
        .append("g")
        .attr("fill", color)
        .selectAll("circle")
        .data(points)
        .enter()
        .append("circle")
        .attr("cx", (d) => d.x)
        .attr("cy", (d) => d.y)
        .attr("r", ds.series.pointRadius);
    }

    if (input.showEndpointLabels && points.length > 0) {
      const last = points[points.length - 1]!;
      inner
        .append("text")
        .attr("x", last.x + 6)
        .attr("y", last.y + 5)
        .attr("font-size", ds.typography.labelSize)
        .attr("fill", color)
        .attr("font-weight", 600)
        .text(`${s.name}: ${fmt(last.yValue)}`);
    } else if (input.showLastValueOnly && points.length > 0) {
      const last = points[points.length - 1]!;
      inner
        .append("text")
        .attr("x", last.x + 6)
        .attr("y", last.y + 5)
        .attr("font-size", ds.typography.labelSize)
        .attr("fill", color)
        .text(fmt(last.yValue));
    }

    layoutSeries.push({ name: s.name, points, color });
  });

  if (input.series.length > 1) {
    drawLegend(
      frame,
      input.series.map((s, i) => ({
        label: s.name,
        color: colors[i % colors.length]!,
      })),
    );
  }

  const layout: LineLayout = {
    kind: "line",
    plot: frame.plot,
    series: layoutSeries,
    axes: {
      x: buildAxisDescriptor(xScale, [0, innerWidth]),
      y: buildAxisDescriptor(yScale, [innerHeight, 0], fmt as any),
    },
  };

  return { frame, layout };
}
