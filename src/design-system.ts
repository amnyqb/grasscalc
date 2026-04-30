import { z } from "zod";

export const DesignSystemSchema = z.object({
  id: z.string(),
  name: z.string().optional(),

  palette: z.object({
    categorical: z.array(z.string()).min(1),
    sequential: z.array(z.string()).optional(),
    diverging: z.array(z.string()).optional(),
    background: z.string().default("#ffffff"),
    foreground: z.string().default("#111111"),
    muted: z.string().default("#6b7280"),
    grid: z.string().default("#e5e7eb"),
  }),

  typography: z.object({
    fontFamily: z
      .string()
      .default(
        "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      ),
    titleSize: z.number().min(14).default(18),
    titleWeight: z.number().default(600),
    labelSize: z.number().min(14).default(14),
    labelWeight: z.number().default(400),
    tickSize: z.number().min(14).default(14),
  }),

  layout: z.object({
    padding: z
      .object({
        top: z.number().default(56),
        right: z.number().default(28),
        bottom: z.number().default(56),
        left: z.number().default(64),
      })
      .default({}),
    cornerRadius: z.number().default(2),
  }),

  /**
   * The complete spacing language of the chart. Every layout decision the
   * renderer makes — title position, source position, legend offset,
   * annotation clearance, callout leader length, etc. — is parameterized
   * here. Picking a design system therefore picks a complete visual style;
   * no magic numbers leak into the renderer.
   */
  spacing: z
    .object({
      // ---------- Header zone (title + subtitle) ----------
      /** SVG-top → title baseline (additive: actual y = this + titleSize). */
      titleTopMargin: z.number().default(22),
      /** Gap between title baseline and subtitle baseline. */
      subtitleGap: z.number().default(6),

      // ---------- Footer zone (legend + source) ----------
      /** SVG-bottom → source line baseline. */
      sourceBottomMargin: z.number().default(14),
      /** SVG-bottom → legend baseline when no source is present. */
      legendBottomMargin: z.number().default(14),
      /** SVG-bottom → legend baseline when source IS present (legend sits above source). */
      legendBottomMarginWithSource: z.number().default(36),

      // ---------- Plot internals ----------
      /** Minimum y (in inner coords) any annotation may occupy. */
      plotTopMargin: z.number().default(8),
      /** Bar top → value-label baseline gap (positive bars; the label sits above). */
      valueLabelOffset: z.number().default(6),

      // ---------- Annotation behavior ----------
      /** Vertical clearance above bar tops + value labels for brackets/CAGR arcs. */
      annotationValueClearance: z.number().default(28),
      /** Gap between stacked annotations (one above the other). */
      annotationLabelGap: z.number().default(6),
      /** Approximate label height for stacking math (≈ font size + descenders). */
      annotationLabelHeight: z.number().default(16),
      /** Per-tier vertical reservation when expanding padding for annotations. */
      annotationTier: z
        .object({
          cagrArrow: z.number().default(28),
          delta: z.number().default(24),
          bracket: z.number().default(28),
        })
        .default({}),
      /** Multiplier applied to yMax when above-annotations are present so
       *  bars don't reach the plot top. e.g. 1.20 = 20% headroom. */
      domainHeadroom: z.number().default(1.2),

      // ---------- Callout placement ----------
      /** Horizontal leader length for left/right callouts. */
      calloutDx: z.number().default(56),
      /** Vertical leader length for top/bottom callouts. */
      calloutDy: z.number().default(44),
      /** Reference-line label offset from the line. */
      referenceLineLabelGap: z.number().default(4),
    })
    .default({}),

  /**
   * Stroke widths and visual weights for annotation primitives. Bumping
   * these in a brand DS makes annotations more or less prominent without
   * touching renderer code.
   */
  annotations: z
    .object({
      arrow: z
        .object({
          strokeWidth: z.number().default(1.75),
          markerSize: z.number().default(9),
        })
        .default({}),
      bracket: z
        .object({
          strokeWidth: z.number().default(1.25),
          tickHeight: z.number().default(6),
        })
        .default({}),
      delta: z
        .object({
          strokeWidth: z.number().default(1.25),
          tickHeight: z.number().default(6),
        })
        .default({}),
      callout: z
        .object({
          dotRadius: z.number().default(3),
          strokeWidth: z.number().default(1),
        })
        .default({}),
      referenceLine: z
        .object({
          strokeWidth: z.number().default(1.25),
          defaultStyle: z
            .enum(["solid", "dashed", "dotted"])
            .default("dashed"),
        })
        .default({}),
    })
    .default({}),

  axes: z.object({
    showGridX: z.boolean().default(false),
    showGridY: z.boolean().default(true),
    axisLineWidth: z.number().default(1),
    tickLength: z.number().default(4),
  }),

  series: z.object({
    strokeWidth: z.number().default(2),
    pointRadius: z.number().default(3),
    barGap: z.number().default(0.15),
    groupGap: z.number().default(0.25),
  }),
});

export type DesignSystem = z.infer<typeof DesignSystemSchema>;

const baseDefaults = {
  layout: {
    padding: { top: 56, right: 28, bottom: 56, left: 64 },
    cornerRadius: 2,
  },
  axes: { showGridX: false, showGridY: true, axisLineWidth: 1, tickLength: 4 },
  series: { strokeWidth: 2, pointRadius: 3, barGap: 0.15, groupGap: 0.25 },
};

export const BUILTIN_DESIGN_SYSTEMS: Record<string, DesignSystem> = {
  default: DesignSystemSchema.parse({
    id: "default",
    name: "Default",
    palette: {
      categorical: [
        "#2563eb",
        "#16a34a",
        "#dc2626",
        "#d97706",
        "#7c3aed",
        "#0891b2",
        "#db2777",
        "#65a30d",
      ],
      sequential: ["#eff6ff", "#bfdbfe", "#60a5fa", "#2563eb", "#1e3a8a"],
      diverging: ["#dc2626", "#fca5a5", "#f3f4f6", "#93c5fd", "#1d4ed8"],
      background: "#ffffff",
      foreground: "#111111",
      muted: "#6b7280",
      grid: "#e5e7eb",
    },
    typography: {
      fontFamily:
        "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      titleSize: 18,
      titleWeight: 600,
      labelSize: 14,
      labelWeight: 400,
      tickSize: 14,
    },
    ...baseDefaults,
  }),

  /**
   * Think-cell-inspired: bolder title, tighter callouts (think-cell
   * traditionally fits a lot of detail close to bars), thicker arrows.
   */
  thinkcell: DesignSystemSchema.parse({
    id: "thinkcell",
    name: "Think-cell inspired",
    palette: {
      categorical: [
        "#1f3a68",
        "#5b8def",
        "#9ec5fe",
        "#c9d6e8",
        "#e6b800",
        "#a33333",
      ],
      sequential: ["#eaf1fb", "#9ec5fe", "#5b8def", "#1f3a68", "#0b1d3a"],
      background: "#ffffff",
      foreground: "#0b1d3a",
      muted: "#5a6b85",
      grid: "#dde3ec",
    },
    typography: {
      fontFamily: "Calibri, Segoe UI, Arial, sans-serif",
      titleSize: 18,
      titleWeight: 700,
      labelSize: 14,
      labelWeight: 400,
      tickSize: 14,
    },
    spacing: {
      annotationValueClearance: 22, // tighter — closer to the data
      calloutDx: 48,
      calloutDy: 36,
      domainHeadroom: 1.18,
    },
    annotations: {
      arrow: { strokeWidth: 2, markerSize: 10 },
      bracket: { strokeWidth: 1.5, tickHeight: 7 },
    },
    ...baseDefaults,
  }),

  /**
   * Minimal Mono / BCG-style: airier, more whitespace, thinner strokes,
   * higher headroom, subtle annotations. Designed to look at home in
   * consultancy decks.
   */
  minimal: DesignSystemSchema.parse({
    id: "minimal",
    name: "Minimal Mono",
    palette: {
      categorical: ["#111111", "#555555", "#999999", "#cccccc"],
      background: "#ffffff",
      foreground: "#111111",
      muted: "#777777",
      grid: "#eeeeee",
    },
    typography: {
      fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      titleSize: 16,
      titleWeight: 500,
      labelSize: 14,
      labelWeight: 400,
      tickSize: 14,
    },
    spacing: {
      titleTopMargin: 28,
      subtitleGap: 8,
      annotationValueClearance: 36, // generous breathing room
      annotationLabelGap: 10,
      calloutDx: 64,
      calloutDy: 52,
      domainHeadroom: 1.25,
    },
    annotations: {
      arrow: { strokeWidth: 1.25, markerSize: 8 },
      bracket: { strokeWidth: 1, tickHeight: 5 },
      delta: { strokeWidth: 1, tickHeight: 5 },
      referenceLine: { strokeWidth: 1, defaultStyle: "dotted" },
    },
    ...baseDefaults,
    axes: { ...baseDefaults.axes, showGridY: false },
  }),
};

export class DesignSystemRegistry {
  private store = new Map<string, DesignSystem>();

  constructor() {
    for (const ds of Object.values(BUILTIN_DESIGN_SYSTEMS)) {
      this.store.set(ds.id, ds);
    }
  }

  list(): DesignSystem[] {
    return Array.from(this.store.values());
  }

  get(id: string): DesignSystem | undefined {
    return this.store.get(id);
  }

  register(ds: DesignSystem): void {
    this.store.set(ds.id, ds);
  }

  resolve(
    idOrInline: string | Partial<DesignSystem> | undefined,
  ): DesignSystem {
    if (!idOrInline) return this.store.get("default")!;
    if (typeof idOrInline === "string") {
      const ds = this.store.get(idOrInline);
      if (!ds) throw new Error(`Unknown design system: ${idOrInline}`);
      return ds;
    }
    return DesignSystemSchema.parse({
      id: idOrInline.id ?? "inline",
      ...this.store.get("default"),
      ...idOrInline,
    });
  }
}
