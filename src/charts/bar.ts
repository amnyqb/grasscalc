import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import type { BarLayout, BarRef } from "../types.js";
import {
  ChartFrame,
  buildAxisDescriptor,
  createFrame,
  drawAxes,
  drawLegend,
} from "./common.js";

export const BarChartSchema = z.object({
  type: z.literal("bar"),
  title: z.string().optional(),
  subtitle: z.string().optional(),
  source: z.string().optional(),
  description: z.string().optional(),
  widthPt: z.number().int().positive().default(720),
  heightPt: z.number().int().positive().default(420),
  background: z.enum(["default", "transparent"]).default("default"),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  orientation: z.enum(["vertical", "horizontal"]).default("vertical"),
  stacked: z.boolean().default(false),
  showValues: z.boolean().default(false),
  valueFormat: z.string().default(",.0f"),
  categories: z.array(z.string()).min(1),
  series: z
    .array(
      z.object({
        name: z.string(),
        values: z.array(z.number()),
      }),
    )
    .min(1),
});

export type BarChartInput = z.infer<typeof BarChartSchema>;

function hasAboveAnnotation(arr: unknown): boolean {
  if (!Array.isArray(arr)) return false;
  return arr.some(
    (a: any) =>
      a &&
      (a.type === "cagr_arrow" ||
        a.type === "delta" ||
        a.type === "bracket") &&
      (a.placement === undefined || a.placement === "above"),
  );
}

export interface RenderResult {
  frame: ChartFrame;
  layout: BarLayout;
}

export function renderBar(
  input: BarChartInput,
  ds: DesignSystem,
): RenderResult {
  const frame = createFrame(ds, input.widthPt, input.heightPt, {
    title: input.title,
    subtitle: input.subtitle,
    source: input.source,
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

  const bars: BarRef[] = [];

  const x0 = d3
    .scaleBand<string>()
    .domain(input.categories)
    .range(input.orientation === "vertical" ? [0, innerWidth] : [0, innerHeight])
    .paddingInner(ds.series.barGap)
    .paddingOuter(ds.series.groupGap);

  if (input.stacked) {
    const stack = d3
      .stack<Record<string, number>>()
      .keys(input.series.map((s) => s.name))(
      input.categories.map((_cat, i) => {
        const row: Record<string, number> = { __i: i };
        for (const s of input.series) row[s.name] = s.values[i] ?? 0;
        return row;
      }),
    );

    let yMax = d3.max(stack[stack.length - 1] ?? [], (d) => d[1]) ?? 0;
    if (hasAboveAnnotation((input as any).annotations)) yMax = yMax * 1.20;
    const yScale = d3
      .scaleLinear()
      .domain([0, yMax])
      .nice()
      .range(
        input.orientation === "vertical" ? [innerHeight, 0] : [0, innerWidth],
      );

    if (input.orientation === "vertical") {
      drawAxes(frame, x0, yScale, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
        yTickFormat: fmt as any,
      });
    } else {
      drawAxes(frame, yScale, x0, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
        xTickFormat: fmt as any,
      });
    }

    stack.forEach((layer, layerIdx) => {
      const color = colors[layerIdx % colors.length]!;
      const seriesName = input.series[layerIdx]!.name;
      const g = inner.append("g").attr("fill", color);
      layer.forEach((d, i) => {
        const cat = input.categories[i]!;
        const value = d[1] - d[0];
        let bx: number, by: number, bw: number, bh: number;
        if (input.orientation === "vertical") {
          bx = x0(cat) ?? 0;
          by = yScale(d[1]) as number;
          bw = x0.bandwidth();
          bh = (yScale(d[0]) as number) - (yScale(d[1]) as number);
        } else {
          bx = yScale(d[0]) as number;
          by = x0(cat) ?? 0;
          bw = (yScale(d[1]) as number) - (yScale(d[0]) as number);
          bh = x0.bandwidth();
        }
        g.append("rect")
          .attr("rx", ds.layout.cornerRadius)
          .attr("x", bx)
          .attr("y", by)
          .attr("width", bw)
          .attr("height", bh);
        if (input.showValues && value !== 0 && bh > 18) {
          inner
            .append("text")
            .attr("x", bx + bw / 2)
            .attr("y", by + bh / 2 + 5)
            .attr("text-anchor", "middle")
            .attr("font-size", ds.typography.labelSize)
            .attr("fill", "#ffffff")
            .text(fmt(value));
        }
        bars.push({
          series: seriesName,
          category: cat,
          x: bx,
          y: by,
          width: bw,
          height: bh,
          value,
          top: { x: bx + bw / 2, y: by },
        });
      });
    });
  } else {
    const x1 = d3
      .scaleBand<string>()
      .domain(input.series.map((s) => s.name))
      .range([0, x0.bandwidth()])
      .padding(0.05);

    const allValues = input.series.flatMap((s) => s.values);
    let yMax = d3.max(allValues) ?? 0;
    if (hasAboveAnnotation((input as any).annotations)) yMax = yMax * 1.20;
    const yMin = Math.min(0, d3.min(allValues) ?? 0);
    const yScale = d3
      .scaleLinear()
      .domain([yMin, yMax])
      .nice()
      .range(
        input.orientation === "vertical" ? [innerHeight, 0] : [0, innerWidth],
      );

    if (input.orientation === "vertical") {
      drawAxes(frame, x0, yScale, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
        yTickFormat: fmt as any,
      });
    } else {
      drawAxes(frame, yScale, x0, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
        xTickFormat: fmt as any,
      });
    }

    input.series.forEach((s, sIdx) => {
      const color = colors[sIdx % colors.length]!;
      const g = inner.append("g").attr("fill", color);
      s.values.forEach((v, i) => {
        const cat = input.categories[i]!;
        let bx: number, by: number, bw: number, bh: number;
        if (input.orientation === "vertical") {
          bx = (x0(cat) ?? 0) + (x1(s.name) ?? 0);
          by = Math.min(yScale(0) as number, yScale(v) as number);
          bw = x1.bandwidth();
          bh = Math.abs((yScale(v) as number) - (yScale(0) as number));
        } else {
          bx = Math.min(yScale(0) as number, yScale(v) as number);
          by = (x0(cat) ?? 0) + (x1(s.name) ?? 0);
          bw = Math.abs((yScale(v) as number) - (yScale(0) as number));
          bh = x1.bandwidth();
        }
        g.append("rect")
          .attr("rx", ds.layout.cornerRadius)
          .attr("x", bx)
          .attr("y", by)
          .attr("width", bw)
          .attr("height", bh);
        let valueLabelY: number | undefined;
        if (input.showValues) {
          const ly =
            input.orientation === "vertical" ? by - 6 : by + bh / 2 + 5;
          inner
            .append("text")
            .attr("x", bx + bw / 2)
            .attr("y", ly)
            .attr("text-anchor", "middle")
            .attr("font-size", ds.typography.labelSize)
            .attr("fill", ds.palette.foreground)
            .text(fmt(v));
          if (input.orientation === "vertical") {
            valueLabelY = ly - ds.typography.labelSize;
          }
        }
        bars.push({
          series: s.name,
          category: cat,
          x: bx,
          y: by,
          width: bw,
          height: bh,
          value: v,
          top: { x: bx + bw / 2, y: by },
          valueLabelY,
          sign: v >= 0 ? 1 : -1,
        });
      });
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

  const xAxisDesc = buildAxisDescriptor(x0, [0, innerWidth]);
  const yAxisDesc = buildAxisDescriptor(
    d3
      .scaleLinear()
      .domain([0, d3.max(input.series.flatMap((s) => s.values)) ?? 0])
      .nice()
      .range([innerHeight, 0]),
    [innerHeight, 0],
    fmt as any,
  );

  const layout: BarLayout = {
    kind: input.stacked ? "stacked_bar" : "bar",
    plot: frame.plot,
    bars,
    axes: { x: xAxisDesc, y: yAxisDesc },
    orientation: input.orientation,
  };

  return { frame, layout };
}
