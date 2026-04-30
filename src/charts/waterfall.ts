import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import type { BarLayout, BarRef } from "../types.js";
import {
  ChartFrame,
  buildAxisDescriptor,
  createFrame,
  drawAxes,
} from "./common.js";

export const WaterfallChartSchema = z.object({
  type: z.literal("waterfall"),
  title: z.string().optional(),
  subtitle: z.string().optional(),
  source: z.string().optional(),
  description: z.string().optional(),
  widthPt: z.number().int().positive().default(720),
  heightPt: z.number().int().positive().default(420),
  background: z.enum(["default", "transparent"]).default("default"),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  showValues: z.boolean().default(true),
  showConnectors: z.boolean().default(true),
  valueFormat: z.string().default("+,.0f"),
  /** Indices in `categories` that should be drawn as totals/subtotals
   *  (anchored to zero, no float). The first and last are commonly totals. */
  subtotalIndices: z.array(z.number().int().nonnegative()).default([]),
  colors: z
    .object({
      positive: z.string().optional(),
      negative: z.string().optional(),
      total: z.string().optional(),
    })
    .default({}),
  categories: z.array(z.string()).min(2),
  values: z.array(z.number()).min(2),
});

export type WaterfallChartInput = z.infer<typeof WaterfallChartSchema>;

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

export function renderWaterfall(
  input: WaterfallChartInput,
  ds: DesignSystem,
): RenderResult {
  if (input.values.length !== input.categories.length) {
    throw new Error(
      `waterfall: ${input.values.length} values for ${input.categories.length} categories.`,
    );
  }

  const frame = createFrame(ds, input.widthPt, input.heightPt, {
    title: input.title,
    subtitle: input.subtitle,
    source: input.source,
    description: input.description,
    background: input.background,
  });
  const { inner, innerWidth, innerHeight } = frame;
  const fmt = d3.format(input.valueFormat);

  const palette = ds.palette.categorical;
  const positiveColor = input.colors.positive ?? palette[1] ?? "#16a34a";
  const negativeColor = input.colors.negative ?? palette[2] ?? "#dc2626";
  const totalColor = input.colors.total ?? palette[0] ?? "#0a3d62";

  const totals = new Set(input.subtotalIndices);

  // Compute float starts/ends for each bar.
  let running = 0;
  const segments = input.values.map((v, i) => {
    const isTotal = totals.has(i);
    if (isTotal) {
      const seg = { start: 0, end: v, value: v, isTotal: true };
      running = v;
      return seg;
    }
    const start = running;
    const end = running + v;
    running = end;
    return { start, end, value: v, isTotal: false };
  });

  const yMin = Math.min(0, d3.min(segments.flatMap((s) => [s.start, s.end]))!);
  let yMax = Math.max(0, d3.max(segments.flatMap((s) => [s.start, s.end]))!);
  // Reserve ~12% domain headroom for above-placement annotations so brackets
  // and CAGR arcs don't crash through bar tops/value labels.
  if (hasAboveAnnotation((input as any).annotations)) {
    yMax = yMax * 1.20;
  }

  const xScale = d3
    .scaleBand<string>()
    .domain(input.categories)
    .range([0, innerWidth])
    .paddingInner(ds.series.barGap)
    .paddingOuter(ds.series.groupGap);

  const yScale = d3
    .scaleLinear()
    .domain([yMin, yMax])
    .nice()
    .range([innerHeight, 0]);

  drawAxes(frame, xScale, yScale, {
    xLabel: input.xLabel,
    yLabel: input.yLabel,
    yTickFormat: fmt as any,
  });

  const bars: BarRef[] = [];
  const connectors: BarLayout["connectors"] = [];

  segments.forEach((seg, i) => {
    const cat = input.categories[i]!;
    const bx = xScale(cat) ?? 0;
    const bw = xScale.bandwidth();
    const top = Math.min(yScale(seg.start)!, yScale(seg.end)!);
    const bottom = Math.max(yScale(seg.start)!, yScale(seg.end)!);
    const bh = bottom - top;

    const fill = seg.isTotal
      ? totalColor
      : seg.value >= 0
        ? positiveColor
        : negativeColor;

    inner
      .append("rect")
      .attr("x", bx)
      .attr("y", top)
      .attr("width", bw)
      .attr("height", bh)
      .attr("rx", ds.layout.cornerRadius)
      .attr("fill", fill);

    let valueLabelY: number | undefined;
    if (input.showValues) {
      const labelY = seg.value >= 0 || seg.isTotal ? top - 6 : bottom + 16;
      inner
        .append("text")
        .attr("x", bx + bw / 2)
        .attr("y", labelY)
        .attr("text-anchor", "middle")
        .attr("font-size", ds.typography.labelSize)
        .attr("fill", ds.palette.foreground)
        .text(seg.isTotal ? d3.format(",.0f")(seg.value) : fmt(seg.value));
      // Only positive/total labels are above the bar — those are what
      // annotation peak detection needs to clear.
      if (seg.value >= 0 || seg.isTotal) {
        valueLabelY = labelY - ds.typography.labelSize;
      }
    }

    if (input.showConnectors && i > 0) {
      const prev = segments[i - 1]!;
      const prevX = (xScale(input.categories[i - 1]!) ?? 0) + bw;
      const currX = bx;
      const yEndPrev = yScale(prev.end) as number;
      connectors.push({ x1: prevX, y1: yEndPrev, x2: currX, y2: yEndPrev });
      inner
        .append("line")
        .attr("x1", prevX)
        .attr("y1", yEndPrev)
        .attr("x2", currX)
        .attr("y2", yEndPrev)
        .attr("stroke", ds.palette.muted)
        .attr("stroke-dasharray", "3,3")
        .attr("stroke-width", 1);
    }

    bars.push({
      series: "waterfall",
      category: cat,
      x: bx,
      y: top,
      width: bw,
      height: bh,
      value: seg.value,
      top: { x: bx + bw / 2, y: top },
      valueLabelY,
      isTotal: seg.isTotal,
      sign: seg.value >= 0 ? 1 : -1,
    });
  });

  const layout: BarLayout = {
    kind: "waterfall",
    plot: frame.plot,
    bars,
    connectors,
    axes: {
      x: buildAxisDescriptor(xScale, [0, innerWidth]),
      y: buildAxisDescriptor(yScale, [innerHeight, 0], fmt as any),
    },
    orientation: "vertical",
  };

  return { frame, layout };
}
