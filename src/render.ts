import { z } from "zod";
import type { DesignSystem } from "./design-system.js";
import { BarChartSchema, renderBar } from "./charts/bar.js";
import { LineChartSchema, renderLine } from "./charts/line.js";
import { ScatterChartSchema, renderScatter } from "./charts/scatter.js";
import { AreaChartSchema, renderArea } from "./charts/area.js";
import { PieChartSchema, renderPie } from "./charts/pie.js";
import { WaterfallChartSchema, renderWaterfall } from "./charts/waterfall.js";
import { applyAnnotations } from "./annotations.js";
import { serialize } from "./charts/common.js";
import {
  AnnotationSchema,
  ENGINE_VERSION,
  type ChartResponse,
} from "./types.js";

const SharedExtras = {
  annotations: z.array(AnnotationSchema).optional(),
};

export const ChartInputSchema = z.discriminatedUnion("type", [
  BarChartSchema.extend(SharedExtras),
  LineChartSchema.extend(SharedExtras),
  ScatterChartSchema.extend(SharedExtras),
  AreaChartSchema.extend(SharedExtras),
  PieChartSchema.extend(SharedExtras),
  WaterfallChartSchema.extend(SharedExtras),
]);

export type ChartInput = z.infer<typeof ChartInputSchema>;

export interface ComposeOptions {
  chartId: string;
}

export function composeChart(
  input: ChartInput,
  ds: DesignSystem,
  opts: ComposeOptions,
): ChartResponse {
  let result: { frame: any; layout: any };
  switch (input.type) {
    case "bar":
      result = renderBar(input, ds);
      break;
    case "line":
      result = renderLine(input, ds);
      break;
    case "scatter":
      result = renderScatter(input, ds);
      break;
    case "area":
      result = renderArea(input, ds);
      break;
    case "pie":
      result = renderPie(input, ds);
      break;
    case "waterfall":
      result = renderWaterfall(input, ds);
      break;
  }

  const annotations = (input as any).annotations as
    | z.infer<typeof AnnotationSchema>[]
    | undefined;
  if (annotations && annotations.length) {
    applyAnnotations({ frame: result.frame, layout: result.layout }, annotations);
  }

  const svg = serialize(result.frame);
  const widthPt = (input as any).widthPt as number;
  const heightPt = (input as any).heightPt as number;

  return {
    format: "svg",
    content: svg,
    widthPt,
    heightPt,
    viewBox: `0 0 ${widthPt} ${heightPt}`,
    layout: result.layout,
    warnings: result.frame.warnings,
    chartId: opts.chartId,
    engine: ENGINE_VERSION,
  };
}
