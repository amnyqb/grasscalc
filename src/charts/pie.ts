import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import { createFrame, drawLegend, serialize } from "./common.js";

export const PieChartSchema = z.object({
  type: z.literal("pie"),
  title: z.string().optional(),
  width: z.number().int().positive().default(520),
  height: z.number().int().positive().default(420),
  donut: z.boolean().default(false),
  showValues: z.boolean().default(true),
  slices: z
    .array(
      z.object({
        label: z.string(),
        value: z.number().nonnegative(),
      }),
    )
    .min(1),
});

export type PieChartInput = z.infer<typeof PieChartSchema>;

export function renderPie(input: PieChartInput, ds: DesignSystem): string {
  const frame = createFrame(ds, input.width, input.height, input.title);
  const { inner, innerWidth, innerHeight } = frame;
  const colors = ds.palette.categorical;

  const radius = Math.min(innerWidth, innerHeight) / 2;
  const center = inner
    .append("g")
    .attr("transform", `translate(${innerWidth / 2},${innerHeight / 2})`);

  const total = d3.sum(input.slices, (s) => s.value) || 1;
  const pie = d3
    .pie<{ label: string; value: number }>()
    .sort(null)
    .value((d) => d.value);

  const arc = d3
    .arc<d3.PieArcDatum<{ label: string; value: number }>>()
    .innerRadius(input.donut ? radius * 0.55 : 0)
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
        const pct = ((d.data.value / total) * 100).toFixed(1);
        return Number(pct) >= 5 ? `${pct}%` : "";
      });
  }

  drawLegend(
    frame,
    input.slices.map((s, i) => ({
      label: s.label,
      color: colors[i % colors.length]!,
    })),
  );

  return serialize(frame);
}
