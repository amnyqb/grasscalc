import { z } from "zod";
import {
  type DesignSystem,
  DesignSystemSchema,
} from "./design-system.js";
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

/**
 * Bump top/bottom padding when annotations need vertical headroom for
 * brackets, arrow apexes and labels. Each above-annotation reserves
 * ~22px stacked; below-annotations the same. Title still gets its own
 * 14px.
 */
function expandPaddingForAnnotations(
  ds: DesignSystem,
  annotations: { type: string; placement?: string }[] | undefined,
): DesignSystem {
  if (!annotations || annotations.length === 0) return ds;
  const tiers = ds.spacing.annotationTier;
  let above = 0;
  let below = 0;
  for (const a of annotations) {
    const tier =
      a.type === "cagr_arrow" ? tiers.cagrArrow :
      a.type === "bracket" ? tiers.bracket :
      a.type === "delta" ? tiers.delta : 0;
    if (!tier) continue;
    if (a.placement === "below") below += tier;
    else above += tier;
  }
  if (!above && !below) return ds;
  return DesignSystemSchema.parse({
    ...ds,
    layout: {
      ...ds.layout,
      padding: {
        ...ds.layout.padding,
        top: ds.layout.padding.top + above,
        bottom: ds.layout.padding.bottom + below,
      },
    },
  });
}

export function composeChart(
  input: ChartInput,
  ds: DesignSystem,
  opts: ComposeOptions,
): ChartResponse {
  const annotations = (input as any).annotations as
    | z.infer<typeof AnnotationSchema>[]
    | undefined;
  const effectiveDs = expandPaddingForAnnotations(ds, annotations);

  let result: { frame: any; layout: any };
  switch (input.type) {
    case "bar":
      result = renderBar(input, effectiveDs);
      break;
    case "line":
      result = renderLine(input, effectiveDs);
      break;
    case "scatter":
      result = renderScatter(input, effectiveDs);
      break;
    case "area":
      result = renderArea(input, effectiveDs);
      break;
    case "pie":
      result = renderPie(input, effectiveDs);
      break;
    case "waterfall":
      result = renderWaterfall(input, effectiveDs);
      break;
  }

  if (annotations && annotations.length) {
    applyAnnotations(
      { frame: result.frame, layout: result.layout },
      annotations,
    );
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
