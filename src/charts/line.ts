import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import { createFrame, drawAxes, drawLegend, serialize } from "./common.js";

export const LineChartSchema = z.object({
  type: z.literal("line"),
  title: z.string().optional(),
  width: z.number().int().positive().default(720),
  height: z.number().int().positive().default(420),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  showPoints: z.boolean().default(false),
  smooth: z.boolean().default(false),
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

export function renderLine(input: LineChartInput, ds: DesignSystem): string {
  const frame = createFrame(ds, input.width, input.height, input.title);
  const { inner, innerWidth, innerHeight } = frame;
  const colors = ds.palette.categorical;

  const allPoints = input.series.flatMap((s) => s.points);
  const xValues = allPoints.map((p) => p.x);
  const xIsNumeric = xValues.every((v) => typeof v === "number");

  let xScale: d3.AxisScale<d3.AxisDomain>;
  if (xIsNumeric) {
    const xs = xValues as number[];
    xScale = d3
      .scaleLinear()
      .domain([d3.min(xs)!, d3.max(xs)!])
      .nice()
      .range([0, innerWidth]) as unknown as d3.AxisScale<d3.AxisDomain>;
  } else {
    const cats = Array.from(new Set(xValues.map(String)));
    xScale = d3
      .scalePoint<string>()
      .domain(cats)
      .range([0, innerWidth])
      .padding(0.5) as unknown as d3.AxisScale<d3.AxisDomain>;
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
  });

  const lineGen = d3
    .line<{ x: number | string; y: number }>()
    .x((d) => (xScale as any)(xIsNumeric ? d.x : String(d.x)) as number)
    .y((d) => yScale(d.y) as number)
    .curve(input.smooth ? d3.curveMonotoneX : d3.curveLinear);

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

    if (input.showPoints) {
      inner
        .append("g")
        .attr("fill", color)
        .selectAll("circle")
        .data(s.points)
        .enter()
        .append("circle")
        .attr(
          "cx",
          (d) => (xScale as any)(xIsNumeric ? d.x : String(d.x)) as number,
        )
        .attr("cy", (d) => yScale(d.y) as number)
        .attr("r", ds.series.pointRadius);
    }
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
