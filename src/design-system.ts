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
    titleSize: z.number().default(16),
    titleWeight: z.number().default(600),
    labelSize: z.number().default(12),
    labelWeight: z.number().default(400),
    tickSize: z.number().default(11),
  }),

  layout: z.object({
    padding: z
      .object({
        top: z.number().default(32),
        right: z.number().default(24),
        bottom: z.number().default(48),
        left: z.number().default(56),
      })
      .default({}),
    cornerRadius: z.number().default(2),
  }),

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
    padding: { top: 32, right: 24, bottom: 48, left: 56 },
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
      titleSize: 16,
      titleWeight: 600,
      labelSize: 12,
      labelWeight: 400,
      tickSize: 11,
    },
    ...baseDefaults,
  }),

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
      titleSize: 15,
      titleWeight: 700,
      labelSize: 11,
      labelWeight: 400,
      tickSize: 10,
    },
    ...baseDefaults,
  }),

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
      titleSize: 14,
      titleWeight: 500,
      labelSize: 11,
      labelWeight: 400,
      tickSize: 10,
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
