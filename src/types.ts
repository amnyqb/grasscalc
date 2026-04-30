import { z } from "zod";

export const ENGINE_VERSION = "chartsmith-mcp@0.3.0";

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AxisDescriptor {
  scale: "linear" | "band" | "point" | "time";
  domain: unknown[];
  range: [number, number];
  ticks: { value: unknown; pos: number; label: string }[];
}

export interface BarRef {
  series: string;
  category: string | number;
  x: number;
  y: number;
  width: number;
  height: number;
  value: number;
  /** Center of the bar's top edge — convenient anchor for labels/arrows. */
  top: { x: number; y: number };
  /** y of any value label drawn above the bar (smaller than `y`); annotations
   *  use this for clearance so they don't crash through value labels. */
  valueLabelY?: number;
  isTotal?: boolean;
  sign?: 1 | -1;
}

export interface LinePointRef {
  xValue: string | number;
  yValue: number;
  x: number;
  y: number;
}

export interface PieSliceRef {
  label: string;
  value: number;
  percent: number;
  centroid: { x: number; y: number };
  outerCentroid: { x: number; y: number };
  startAngle: number;
  endAngle: number;
}

export interface BarLayout {
  kind: "bar" | "waterfall" | "stacked_bar";
  plot: Rect;
  bars: BarRef[];
  /** For waterfall: connector segments from prior bar top to current bar's start edge. */
  connectors?: { x1: number; y1: number; x2: number; y2: number }[];
  axes: { x: AxisDescriptor; y: AxisDescriptor };
  orientation: "vertical" | "horizontal";
}

export interface LineLayout {
  kind: "line";
  plot: Rect;
  series: { name: string; points: LinePointRef[]; color: string }[];
  axes: { x: AxisDescriptor; y: AxisDescriptor };
}

export interface ScatterLayout {
  kind: "scatter";
  plot: Rect;
  series: {
    name: string;
    points: { xValue: number; yValue: number; x: number; y: number; r: number }[];
    color: string;
  }[];
  axes: { x: AxisDescriptor; y: AxisDescriptor };
}

export interface AreaLayout {
  kind: "area";
  plot: Rect;
  series: { name: string; points: LinePointRef[]; color: string }[];
  axes: { x: AxisDescriptor; y: AxisDescriptor };
}

export interface PieLayout {
  kind: "pie";
  plot: Rect;
  slices: PieSliceRef[];
  center: { x: number; y: number };
  radius: number;
}

export type ChartLayout =
  | BarLayout
  | LineLayout
  | ScatterLayout
  | AreaLayout
  | PieLayout;

export const RefSchema = z.object({
  x: z.union([z.string(), z.number()]).optional(),
  series: z.string().optional(),
  y: z.number().optional(),
});
export type Ref = z.infer<typeof RefSchema>;

export const AnnotationSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("cagr_arrow"),
    from: RefSchema,
    to: RefSchema,
    label: z.string().optional(),
    placement: z.enum(["above", "below", "inline"]).default("above"),
    format: z.string().default(".1%"),
    color: z.string().optional(),
  }),
  z.object({
    type: z.literal("delta"),
    from: RefSchema,
    to: RefSchema,
    placement: z.enum(["above", "below"]).default("above"),
    format: z.string().default("+,.1f"),
    color: z.string().optional(),
  }),
  z.object({
    type: z.literal("callout"),
    anchor: RefSchema,
    text: z.string(),
    placement: z.enum(["top", "bottom", "left", "right"]).default("top"),
    color: z.string().optional(),
  }),
  z.object({
    type: z.literal("reference_line"),
    axis: z.enum(["x", "y"]),
    value: z.union([z.string(), z.number()]),
    label: z.string().optional(),
    style: z.enum(["solid", "dashed", "dotted"]).default("dashed"),
    color: z.string().optional(),
  }),
  z.object({
    type: z.literal("range_band"),
    axis: z.enum(["x", "y"]),
    from: z.union([z.string(), z.number()]),
    to: z.union([z.string(), z.number()]),
    label: z.string().optional(),
    color: z.string().optional(),
    opacity: z.number().min(0).max(1).default(0.12),
  }),
  z.object({
    type: z.literal("total_labels"),
    format: z.string().default(",.0f"),
    color: z.string().optional(),
  }),
  z.object({
    type: z.literal("bracket"),
    from: RefSchema,
    to: RefSchema,
    label: z.string(),
    placement: z.enum(["above", "below"]).default("above"),
    color: z.string().optional(),
  }),
]);
export type Annotation = z.infer<typeof AnnotationSchema>;

export interface ChartResponse {
  format: "svg";
  content: string;
  widthPt: number;
  heightPt: number;
  viewBox: string;
  layout: ChartLayout;
  warnings: string[];
  chartId: string;
  engine: string;
}
