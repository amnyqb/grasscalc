import * as d3 from "d3";
import { z } from "zod";
import type { DesignSystem } from "../design-system.js";
import { createFrame, drawAxes, drawLegend, serialize } from "./common.js";

export const BarChartSchema = z.object({
  type: z.literal("bar"),
  title: z.string().optional(),
  width: z.number().int().positive().default(720),
  height: z.number().int().positive().default(420),
  xLabel: z.string().optional(),
  yLabel: z.string().optional(),
  orientation: z.enum(["vertical", "horizontal"]).default("vertical"),
  stacked: z.boolean().default(false),
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

export function renderBar(input: BarChartInput, ds: DesignSystem): string {
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

    const yMax =
      d3.max(stack[stack.length - 1] ?? [], (d) => d[1]) ?? 0;
    const yScale = d3
      .scaleLinear()
      .domain([0, yMax])
      .nice()
      .range(
        input.orientation === "vertical"
          ? [innerHeight, 0]
          : [0, innerWidth],
      );

    if (input.orientation === "vertical") {
      drawAxes(frame, x0, yScale, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
      });
    } else {
      drawAxes(frame, yScale, x0, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
      });
    }

    stack.forEach((layer, layerIdx) => {
      const color = colors[layerIdx % colors.length];
      inner
        .append("g")
        .attr("fill", color)
        .selectAll("rect")
        .data(layer)
        .enter()
        .append("rect")
        .attr("rx", ds.layout.cornerRadius)
        .attr("x", (_d, i) =>
          input.orientation === "vertical"
            ? (x0(input.categories[i]!) ?? 0)
            : yScale(layer[i]![0]) as number,
        )
        .attr("y", (d, i) =>
          input.orientation === "vertical"
            ? (yScale(d[1]) as number)
            : (x0(input.categories[i]!) ?? 0),
        )
        .attr("width", (d) =>
          input.orientation === "vertical"
            ? x0.bandwidth()
            : (yScale(d[1]) as number) - (yScale(d[0]) as number),
        )
        .attr("height", (d) =>
          input.orientation === "vertical"
            ? (yScale(d[0]) as number) - (yScale(d[1]) as number)
            : x0.bandwidth(),
        );
    });
  } else {
    const x1 = d3
      .scaleBand<string>()
      .domain(input.series.map((s) => s.name))
      .range([0, x0.bandwidth()])
      .padding(0.05);

    const yMax = d3.max(input.series.flatMap((s) => s.values)) ?? 0;
    const yMin = Math.min(0, d3.min(input.series.flatMap((s) => s.values)) ?? 0);
    const yScale = d3
      .scaleLinear()
      .domain([yMin, yMax])
      .nice()
      .range(
        input.orientation === "vertical"
          ? [innerHeight, 0]
          : [0, innerWidth],
      );

    if (input.orientation === "vertical") {
      drawAxes(frame, x0, yScale, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
      });
    } else {
      drawAxes(frame, yScale, x0, {
        xLabel: input.xLabel,
        yLabel: input.yLabel,
      });
    }

    input.series.forEach((s, sIdx) => {
      const color = colors[sIdx % colors.length];
      inner
        .append("g")
        .attr("fill", color)
        .selectAll("rect")
        .data(s.values)
        .enter()
        .append("rect")
        .attr("rx", ds.layout.cornerRadius)
        .attr("x", (_v, i) =>
          input.orientation === "vertical"
            ? (x0(input.categories[i]!) ?? 0) + (x1(s.name) ?? 0)
            : Math.min(yScale(0) as number, yScale(_v) as number),
        )
        .attr("y", (v, i) =>
          input.orientation === "vertical"
            ? Math.min(yScale(0) as number, yScale(v) as number)
            : (x0(input.categories[i]!) ?? 0) + (x1(s.name) ?? 0),
        )
        .attr("width", (v) =>
          input.orientation === "vertical"
            ? x1.bandwidth()
            : Math.abs((yScale(v) as number) - (yScale(0) as number)),
        )
        .attr("height", (v) =>
          input.orientation === "vertical"
            ? Math.abs((yScale(v) as number) - (yScale(0) as number))
            : x1.bandwidth(),
        );
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
