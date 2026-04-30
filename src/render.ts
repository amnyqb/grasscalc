import { z } from "zod";
import type { DesignSystem } from "./design-system.js";
import { BarChartSchema, renderBar } from "./charts/bar.js";
import { LineChartSchema, renderLine } from "./charts/line.js";
import { ScatterChartSchema, renderScatter } from "./charts/scatter.js";
import { AreaChartSchema, renderArea } from "./charts/area.js";
import { PieChartSchema, renderPie } from "./charts/pie.js";

export const ChartInputSchema = z.discriminatedUnion("type", [
  BarChartSchema,
  LineChartSchema,
  ScatterChartSchema,
  AreaChartSchema,
  PieChartSchema,
]);

export type ChartInput = z.infer<typeof ChartInputSchema>;

export function renderChart(input: ChartInput, ds: DesignSystem): string {
  switch (input.type) {
    case "bar":
      return renderBar(input, ds);
    case "line":
      return renderLine(input, ds);
    case "scatter":
      return renderScatter(input, ds);
    case "area":
      return renderArea(input, ds);
    case "pie":
      return renderPie(input, ds);
  }
}
