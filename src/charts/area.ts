import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import { createFrame, drawAxes, drawLegend, serialize } from "./common.js";

export const AreaChartSchema = z.object({
  type: z.literal("area"),
  title: z.string().optional(),
  width: z.number().int().positive().default(720),
  height: z.number().int().positive().default(420),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  smooth: z.boolean().default(true),
  stacked: z.boolean().default(true),
  categories: z.array(z.union([z.number(), z.string()])).min(1),
  series: z
    .array(
      z.object({
        name: z.string(),
        values: z.array(z.number()),
      }),
    )
    .min(1),
});

export type AreaChartInput = z.infer<typeof AreaChartSchema>;

export function renderArea(input: AreaChartInput, ds: DesignSystem): string {
  const frame = createFrame(ds, input.width, input.height, input.title);
  const { inner, innerWidth, innerHeight } = frame;
  const colors = ds.palette.categorical;

  for (const s of input.series) {
    if (s.values.length !== input.categories.length) {
      throw new Error(
        `series "${s.name}" has ${s.values.length} values; expected ${input.categories.length}`,
      );
    }
  }

  const xIsNumeric = input.categories.every((v) => typeof v === "number");
  const xScale = xIsNumeric
    ? d3
        .scaleLinear()
        .domain([
          d3.min(input.categories as number[])!,
          d3.max(input.categories as number[])!,
        ])
        .range([0, innerWidth])
    : (d3
        .scalePoint<string>()
        .domain(input.categories.map(String))
        .range([0, innerWidth])
        .padding(0.5) as unknown as d3.ScaleLinear<number, number>);

  if (input.stacked) {
    const rows = input.categories.map((_c, i) => {
      const r: Record<string, number> = { __i: i };
      for (const s of input.series) r[s.name] = s.values[i] ?? 0;
      return r;
    });

    const stack = d3
      .stack<Record<string, number>>()
      .keys(input.series.map((s) => s.name))(rows);

    const yMax = d3.max(stack[stack.length - 1] ?? [], (d) => d[1]) ?? 0;
    const yScale = d3
      .scaleLinear()
      .domain([0, yMax])
      .nice()
      .range([innerHeight, 0]);

    drawAxes(frame, xScale as any, yScale, {
      xLabel: input.xLabel,
      yLabel: input.yLabel,
    });

    const areaGen = d3
      .area<d3.SeriesPoint<Record<string, number>>>()
      .x((_d, i) =>
        xIsNumeric
          ? (xScale as d3.ScaleLinear<number, number>)(
              input.categories[i] as number,
            )
          : (xScale as any)(String(input.categories[i])),
      )
      .y0((d) => yScale(d[0]))
      .y1((d) => yScale(d[1]))
      .curve(input.smooth ? d3.curveMonotoneX : d3.curveLinear);

    stack.forEach((layer, i) => {
      const color = colors[i % colors.length]!;
      inner
        .append("path")
        .datum(layer)
        .attr("fill", color)
        .attr("fill-opacity", 0.85)
        .attr("d", areaGen as any);
    });
  } else {
    const yMax = d3.max(input.series.flatMap((s) => s.values)) ?? 0;
    const yScale = d3
      .scaleLinear()
      .domain([0, yMax])
      .nice()
      .range([innerHeight, 0]);

    drawAxes(frame, xScale as any, yScale, {
      xLabel: input.xLabel,
      yLabel: input.yLabel,
    });

    const areaGen = d3
      .area<{ v: number; i: number }>()
      .x((d) =>
        xIsNumeric
          ? (xScale as d3.ScaleLinear<number, number>)(
              input.categories[d.i] as number,
            )
          : (xScale as any)(String(input.categories[d.i])),
      )
      .y0(yScale(0))
      .y1((d) => yScale(d.v))
      .curve(input.smooth ? d3.curveMonotoneX : d3.curveLinear);

    input.series.forEach((s, i) => {
      const color = colors[i % colors.length]!;
      inner
        .append("path")
        .datum(s.values.map((v, idx) => ({ v, i: idx })))
        .attr("fill", color)
        .attr("fill-opacity", 0.4)
        .attr("stroke", color)
        .attr("stroke-width", ds.series.strokeWidth)
        .attr("d", areaGen as any);
    });
  }

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
