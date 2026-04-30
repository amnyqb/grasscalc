import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import type { AreaLayout, LinePointRef } from "../types.js";
import {
  ChartFrame,
  buildAxisDescriptor,
  createFrame,
  drawAxes,
  drawLegend,
} from "./common.js";

export const AreaChartSchema = z.object({
  type: z.literal("area"),
  title: z.string().optional(),
  description: z.string().optional(),
  widthPt: z.number().int().positive().default(720),
  heightPt: z.number().int().positive().default(420),
  background: z.enum(["default", "transparent"]).default("default"),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  smoothing: z.enum(["linear", "monotone", "step"]).default("monotone"),
  stacked: z.boolean().default(true),
  valueFormat: z.string().default(",.0f"),
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

export interface RenderResult {
  frame: ChartFrame;
  layout: AreaLayout;
}

export function renderArea(
  input: AreaChartInput,
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

  for (const s of input.series) {
    if (s.values.length !== input.categories.length) {
      throw new Error(
        `series "${s.name}" has ${s.values.length} values; expected ${input.categories.length}`,
      );
    }
  }

  const xIsNumeric = input.categories.every((v) => typeof v === "number");
  const xScale: any = xIsNumeric
    ? d3
        .scaleLinear()
        .domain([
          d3.min(input.categories as number[])!,
          d3.max(input.categories as number[])!,
        ])
        .range([0, innerWidth])
    : d3
        .scalePoint<string>()
        .domain(input.categories.map(String))
        .range([0, innerWidth])
        .padding(0.5);

  const xAt = (i: number) =>
    (xScale(xIsNumeric ? input.categories[i] : String(input.categories[i])) ??
      0) as number;

  const curve =
    input.smoothing === "monotone"
      ? d3.curveMonotoneX
      : input.smoothing === "step"
        ? d3.curveStepAfter
        : d3.curveLinear;

  const layoutSeries: AreaLayout["series"] = [];

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

    drawAxes(frame, xScale, yScale, {
      xLabel: input.xLabel,
      yLabel: input.yLabel,
      yTickFormat: fmt as any,
    });

    const areaGen = d3
      .area<d3.SeriesPoint<Record<string, number>>>()
      .x((_d, i) => xAt(i))
      .y0((d) => yScale(d[0]))
      .y1((d) => yScale(d[1]))
      .curve(curve);

    stack.forEach((layer, i) => {
      const color = colors[i % colors.length]!;
      inner
        .append("path")
        .datum(layer)
        .attr("fill", color)
        .attr("fill-opacity", 0.85)
        .attr("d", areaGen as any);
      const points: LinePointRef[] = layer.map((d, idx) => ({
        xValue: input.categories[idx]!,
        yValue: d[1] - d[0],
        x: xAt(idx),
        y: yScale(d[1]) as number,
      }));
      layoutSeries.push({ name: input.series[i]!.name, points, color });
    });
  } else {
    const yMax = d3.max(input.series.flatMap((s) => s.values)) ?? 0;
    const yScale = d3
      .scaleLinear()
      .domain([0, yMax])
      .nice()
      .range([innerHeight, 0]);

    drawAxes(frame, xScale, yScale, {
      xLabel: input.xLabel,
      yLabel: input.yLabel,
      yTickFormat: fmt as any,
    });

    const areaGen = d3
      .area<{ v: number; i: number }>()
      .x((d) => xAt(d.i))
      .y0(yScale(0) as number)
      .y1((d) => yScale(d.v) as number)
      .curve(curve);

    input.series.forEach((s, i) => {
      const color = colors[i % colors.length]!;
      const data = s.values.map((v, idx) => ({ v, i: idx }));
      inner
        .append("path")
        .datum(data)
        .attr("fill", color)
        .attr("fill-opacity", 0.4)
        .attr("stroke", color)
        .attr("stroke-width", ds.series.strokeWidth)
        .attr("d", areaGen as any);
      const points: LinePointRef[] = data.map((d) => ({
        xValue: input.categories[d.i]!,
        yValue: d.v,
        x: xAt(d.i),
        y: yScale(d.v) as number,
      }));
      layoutSeries.push({ name: s.name, points, color });
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

  const yScaleForDesc = d3
    .scaleLinear()
    .domain([0, d3.max(input.series.flatMap((s) => s.values)) ?? 0])
    .nice()
    .range([innerHeight, 0]);

  const layout: AreaLayout = {
    kind: "area",
    plot: frame.plot,
    series: layoutSeries,
    axes: {
      x: buildAxisDescriptor(xScale, [0, innerWidth]),
      y: buildAxisDescriptor(yScaleForDesc, [innerHeight, 0], fmt as any),
    },
  };

  return { frame, layout };
}
