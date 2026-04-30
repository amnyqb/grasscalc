import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import type { PieLayout, PieSliceRef } from "../types.js";
import { ChartFrame, createFrame, drawLegend } from "./common.js";

export const PieChartSchema = z.object({
  type: z.literal("pie"),
  title: z.string().optional(),
  description: z.string().optional(),
  widthPt: z.number().int().positive().default(520),
  heightPt: z.number().int().positive().default(420),
  background: z.enum(["default", "transparent"]).default("default"),
  donut: z.boolean().default(false),
  showValues: z.boolean().default(true),
  valueFormat: z.string().default(".1%"),
  slices: z
    .array(z.object({ label: z.string(), value: z.number().nonnegative() }))
    .min(1),
});

export type PieChartInput = z.infer<typeof PieChartSchema>;

export interface RenderResult {
  frame: ChartFrame;
  layout: PieLayout;
}

export function renderPie(
  input: PieChartInput,
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

  const radius = Math.min(innerWidth, innerHeight) / 2;
  const cx = innerWidth / 2;
  const cy = innerHeight / 2;
  const center = inner.append("g").attr("transform", `translate(${cx},${cy})`);

  const total = d3.sum(input.slices, (s) => s.value) || 1;
  const pie = d3
    .pie<{ label: string; value: number }>()
    .sort(null)
    .value((d) => d.value);

  const inner_r = input.donut ? radius * 0.55 : 0;
  const arc = d3
    .arc<d3.PieArcDatum<{ label: string; value: number }>>()
    .innerRadius(inner_r)
    .outerRadius(radius)
    .cornerRadius(ds.layout.cornerRadius);

  const arcs = pie(input.slices);

  center
    .selectAll("path")
    .data(arcs)
    .enter()
    .append("path")
    .attr("d", arc as any)
    .attr("fill", (_d, i) => colors[i % colors.length]!)
    .attr("stroke", ds.palette.background)
    .attr("stroke-width", 1);

  if (input.showValues) {
    center
      .selectAll("text")
      .data(arcs)
      .enter()
      .append("text")
      .attr("transform", (d) => `translate(${arc.centroid(d as any)})`)
      .attr("text-anchor", "middle")
      .attr("font-size", ds.typography.tickSize)
      .attr("fill", "#ffffff")
      .text((d) => {
        const pct = d.data.value / total;
        return pct >= 0.05 ? fmt(pct) : "";
      });
  }

  drawLegend(
    frame,
    input.slices.map((s, i) => ({
      label: s.label,
      color: colors[i % colors.length]!,
    })),
  );

  const slices: PieSliceRef[] = arcs.map((d) => {
    const cen = arc.centroid(d as any);
    const outer = d3
      .arc<d3.PieArcDatum<{ label: string; value: number }>>()
      .innerRadius(radius)
      .outerRadius(radius)
      .centroid(d as any);
    return {
      label: d.data.label,
      value: d.data.value,
      percent: d.data.value / total,
      centroid: { x: cx + cen[0]!, y: cy + cen[1]! },
      outerCentroid: { x: cx + outer[0]!, y: cy + outer[1]! },
      startAngle: d.startAngle,
      endAngle: d.endAngle,
    };
  });

  const layout: PieLayout = {
    kind: "pie",
    plot: frame.plot,
    slices,
    center: { x: frame.plot.x + cx, y: frame.plot.y + cy },
    radius,
  };

  return { frame, layout };
}
