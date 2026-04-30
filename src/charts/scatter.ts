import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import type { ScatterLayout } from "../types.js";
import {
  ChartFrame,
  buildAxisDescriptor,
  createFrame,
  drawAxes,
  drawLegend,
} from "./common.js";

export const ScatterChartSchema = z.object({
  type: z.literal("scatter"),
  title: z.string().optional(),
  description: z.string().optional(),
  widthPt: z.number().int().positive().default(720),
  heightPt: z.number().int().positive().default(480),
  background: z.enum(["default", "transparent"]).default("default"),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  valueFormat: z.string().default(",.1f"),
  series: z
    .array(
      z.object({
        name: z.string(),
        points: z
          .array(
            z.object({
              x: z.number(),
              y: z.number(),
              size: z.number().optional(),
            }),
          )
          .min(1),
      }),
    )
    .min(1),
});

export type ScatterChartInput = z.infer<typeof ScatterChartSchema>;

export interface RenderResult {
  frame: ChartFrame;
  layout: ScatterLayout;
}

export function renderScatter(
  input: ScatterChartInput,
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
  const xs = allPoints.map((p) => p.x);
  const ys = allPoints.map((p) => p.y);

  const xScale = d3
    .scaleLinear()
    .domain([d3.min(xs)!, d3.max(xs)!])
    .nice()
    .range([0, innerWidth]);

  const yScale = d3
    .scaleLinear()
    .domain([d3.min(ys)!, d3.max(ys)!])
    .nice()
    .range([innerHeight, 0]);

  drawAxes(frame, xScale, yScale, {
    xLabel: input.xLabel,
    yLabel: input.yLabel,
    yTickFormat: fmt as any,
  });

  const sizes = allPoints.map((p) => p.size ?? 0).filter((s) => s > 0);
  const sizeScale =
    sizes.length > 0
      ? d3
          .scaleSqrt()
          .domain([d3.min(sizes)!, d3.max(sizes)!])
          .range([4, 16])
      : null;

  const layoutSeries: ScatterLayout["series"] = [];

  input.series.forEach((s, i) => {
    const color = colors[i % colors.length]!;
    const points = s.points.map((p) => ({
      xValue: p.x,
      yValue: p.y,
      x: xScale(p.x) as number,
      y: yScale(p.y) as number,
      r:
        sizeScale && p.size != null
          ? sizeScale(p.size)
          : ds.series.pointRadius + 1,
    }));
    inner
      .append("g")
      .attr("fill", color)
      .attr("fill-opacity", 0.75)
      .attr("stroke", color)
      .attr("stroke-width", 1)
      .selectAll("circle")
      .data(points)
      .enter()
      .append("circle")
      .attr("cx", (d) => d.x)
      .attr("cy", (d) => d.y)
      .attr("r", (d) => d.r);
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

  const layout: ScatterLayout = {
    kind: "scatter",
    plot: frame.plot,
    series: layoutSeries,
    axes: {
      x: buildAxisDescriptor(xScale, [0, innerWidth]),
      y: buildAxisDescriptor(yScale, [innerHeight, 0]),
    },
  };

  return { frame, layout };
}
