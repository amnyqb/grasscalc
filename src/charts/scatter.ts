import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import { createFrame, drawAxes, drawLegend, serialize } from "./common.js";

export const ScatterChartSchema = z.object({
  type: z.literal("scatter"),
  title: z.string().optional(),
  width: z.number().int().positive().default(720),
  height: z.number().int().positive().default(480),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
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

export function renderScatter(
  input: ScatterChartInput,
  ds: DesignSystem,
): string {
  const frame = createFrame(ds, input.width, input.height, input.title);
  const { inner, innerWidth, innerHeight } = frame;
  const colors = ds.palette.categorical;

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
  });

  const sizes = allPoints.map((p) => p.size ?? 0).filter((s) => s > 0);
  const sizeScale =
    sizes.length > 0
      ? d3
          .scaleSqrt()
          .domain([d3.min(sizes)!, d3.max(sizes)!])
          .range([3, 14])
      : null;

  input.series.forEach((s, i) => {
    const color = colors[i % colors.length]!;
    inner
      .append("g")
      .attr("fill", color)
      .attr("fill-opacity", 0.75)
      .attr("stroke", color)
      .attr("stroke-width", 1)
      .selectAll("circle")
      .data(s.points)
      .enter()
      .append("circle")
      .attr("cx", (d) => xScale(d.x))
      .attr("cy", (d) => yScale(d.y))
      .attr("r", (d) =>
        sizeScale && d.size != null
          ? sizeScale(d.size)
          : ds.series.pointRadius + 1,
      );
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

  return serialize(frame);
}
