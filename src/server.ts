import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import {
  DesignSystemRegistry,
  DesignSystemSchema,
} from "./design-system.js";
import { ChartInputSchema, composeChart, type ChartInput } from "./render.js";
import {
  designSystemFromPptxThemeXml,
  designSystemFromTokens,
} from "./pptx-theme.js";
import { ChartStore } from "./chart-store.js";
import { ENGINE_VERSION, type ChartResponse } from "./types.js";

import { BarChartSchema } from "./charts/bar.js";
import { LineChartSchema } from "./charts/line.js";
import { ScatterChartSchema } from "./charts/scatter.js";
import { AreaChartSchema } from "./charts/area.js";
import { PieChartSchema } from "./charts/pie.js";
import { WaterfallChartSchema } from "./charts/waterfall.js";

export interface BuildOptions {
  registry?: DesignSystemRegistry;
  store?: ChartStore;
}

const ChartTypes = [
  {
    name: "bar",
    description:
      "Vertical/horizontal bar; grouped or stacked. Options: stacked, orientation, showValues, valueFormat.",
  },
  {
    name: "line",
    description:
      "Single/multi-series line. Options: smoothing (linear|monotone|step), showPoints, showEndpointLabels.",
  },
  {
    name: "scatter",
    description: "Scatter / bubble (with optional size encoding).",
  },
  {
    name: "area",
    description: "Stacked or overlapping area; smoothing options.",
  },
  {
    name: "pie",
    description: "Pie/donut. Options: donut, showValues.",
  },
  {
    name: "waterfall",
    description:
      "Waterfall (think-cell signature). Options: subtotalIndices, colors {positive, negative, total}, showConnectors.",
  },
];

const SupportedAnnotations = [
  { type: "cagr_arrow", refs: ["from", "to"], options: ["format", "placement", "label"] },
  { type: "delta", refs: ["from", "to"], options: ["format", "placement"] },
  { type: "bracket", refs: ["from", "to"], options: ["label", "placement"] },
  { type: "callout", refs: ["anchor"], options: ["text", "placement"] },
  { type: "reference_line", refs: ["axis", "value"], options: ["label", "style"] },
  { type: "range_band", refs: ["axis", "from", "to"], options: ["label", "opacity"] },
  { type: "total_labels", refs: [], options: ["format"] },
];

function envelopeContent(
  resp: ChartResponse,
  savedTo: string | undefined,
): { type: "text"; text: string }[] {
  const summary = {
    chartId: resp.chartId,
    format: resp.format,
    widthPt: resp.widthPt,
    heightPt: resp.heightPt,
    viewBox: resp.viewBox,
    engine: resp.engine,
    warnings: resp.warnings,
    savedTo,
    layout: resp.layout,
  };
  return [
    { type: "text", text: JSON.stringify(summary, null, 2) },
    { type: "text", text: resp.content },
  ];
}

async function maybeSave(
  output_path: string | undefined,
  svg: string,
): Promise<string | undefined> {
  if (!output_path) return undefined;
  const abs = resolve(output_path);
  await mkdir(dirname(abs), { recursive: true });
  await writeFile(abs, svg, "utf8");
  return abs;
}

export function buildServer(opts: BuildOptions = {}): {
  server: McpServer;
  registry: DesignSystemRegistry;
  store: ChartStore;
} {
  const registry = opts.registry ?? new DesignSystemRegistry();
  const store = opts.store ?? new ChartStore();

  const server = new McpServer(
    { name: "chartsmith-mcp", version: "0.3.0" },
    {
      capabilities: { tools: {} },
      instructions:
        `Chartsmith ${ENGINE_VERSION} renders publication-quality SVG charts with d3, ` +
        "applies a user-defined design system (palette/typography/spacing), and supports a " +
        "declarative annotation layer (CAGR arrows, delta brackets, callouts, reference lines, " +
        "range bands, totals). Workflow: 1) (optional) theme_to_design_system to match a deck. " +
        "2) render_<type> or create_chart with chart input + annotations. " +
        "Each response returns { chartId, widthPt, heightPt, layout, warnings, svg }; layout " +
        "exposes computed bar/point/slice positions for native add-on overlays. " +
        "3) update_chart(chartId, newData) to refresh values without rebuilding (linked-data flow). " +
        "Sizes are in points; SVG viewBox px == pt for trivial PowerPoint sizing.",
    },
  );

  // ---------- Design system tools ----------

  server.registerTool(
    "list_design_systems",
    {
      title: "List design systems",
      description:
        "List all registered design systems (built-in and user-registered).",
      inputSchema: {},
    },
    async () => {
      const systems = registry.list().map((d) => ({
        id: d.id,
        name: d.name ?? d.id,
        categorical: d.palette.categorical,
        background: d.palette.background,
        foreground: d.palette.foreground,
        fontFamily: d.typography.fontFamily,
      }));
      return { content: [{ type: "text", text: JSON.stringify(systems, null, 2) }] };
    },
  );

  server.registerTool(
    "register_design_system",
    {
      title: "Register a design system",
      description:
        "Register or overwrite a design system with palette, typography, layout, axes and series tokens.",
      inputSchema: {
        design_system: z.unknown().describe(
          "DesignSystem object: id + palette.categorical (>=2 hex colors); other fields optional.",
        ),
      },
    },
    async ({ design_system }) => {
      const ds = DesignSystemSchema.parse(design_system);
      registry.register(ds);
      return {
        content: [
          {
            type: "text",
            text: `Registered design system "${ds.id}". Reference it via design_system: "${ds.id}".`,
          },
        ],
      };
    },
  );

  server.registerTool(
    "get_design_system",
    {
      title: "Get a design system",
      description: "Retrieve the full token definition for a registered design system by id.",
      inputSchema: { id: z.string() },
    },
    async ({ id }) => {
      const ds = registry.get(id);
      if (!ds) {
        return {
          isError: true,
          content: [{ type: "text", text: `No design system with id "${id}".` }],
        };
      }
      return { content: [{ type: "text", text: JSON.stringify(ds, null, 2) }] };
    },
  );

  server.registerTool(
    "theme_to_design_system",
    {
      title: "Convert PowerPoint theme to design system",
      description:
        "Translate a PowerPoint deck's theme into a chartsmith design system, then register it. " +
        "Accepts structured tokens (the JSON shape Office.js produces from theme1.xml) " +
        "or the raw theme1.xml string.",
      inputSchema: {
        source: z.enum(["tokens", "xml"]),
        payload: z.union([z.string(), z.record(z.unknown())]),
        id: z.string().optional(),
        name: z.string().optional(),
      },
    },
    async ({ source, payload, id, name }) => {
      let ds;
      if (source === "xml") {
        if (typeof payload !== "string") {
          throw new Error("source='xml' requires a string payload.");
        }
        ds = designSystemFromPptxThemeXml(payload, { id, name });
      } else {
        const tokens =
          typeof payload === "string" ? JSON.parse(payload) : payload;
        ds = designSystemFromTokens({ ...tokens, id, name });
      }
      registry.register(ds);
      return {
        content: [
          {
            type: "text",
            text:
              `Registered "${ds.id}" from PowerPoint theme. ` +
              `Categorical palette: [${ds.palette.categorical.join(", ")}]. ` +
              `Font: ${ds.typography.fontFamily}.`,
          },
        ],
      };
    },
  );

  // ---------- Chart introspection ----------

  server.registerTool(
    "list_chart_types",
    {
      title: "List supported chart types and capabilities",
      description:
        "Returns the chart types this server can render, plus the supported annotation types. " +
        "Use this for runtime introspection instead of hardcoding tool names.",
      inputSchema: {},
    },
    async () => ({
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              engine: ENGINE_VERSION,
              chart_types: ChartTypes,
              annotations: SupportedAnnotations,
              sizing: {
                unit: "points",
                viewBox: "px == pt; SVG scales 1pt-per-unit",
              },
              outputs: {
                format: "svg",
                widthPt: "echoed in response",
                heightPt: "echoed in response",
                layout:
                  "computed positions of bars/points/slices in plot-local coordinates",
                warnings: "soft warnings (label collisions, missing refs, etc.)",
              },
            },
            null,
            2,
          ),
        },
      ],
    }),
  );

  // ---------- Chart rendering ----------

  async function runChart(
    input: ChartInput,
    design_system: unknown,
    output_path: string | undefined,
    opts: { persistent?: boolean; ttlMs?: number } = {},
  ) {
    const ds = registry.resolve(design_system as any);
    const id = store.newId();
    const response = composeChart(input, ds, { chartId: id });
    const savedTo = await maybeSave(output_path, response.content);
    store.put(id, input, ds.id, response, opts);
    return { content: envelopeContent(response, savedTo) };
  }

  const RenderCommonExtras = {
    design_system: z
      .union([z.string(), z.record(z.unknown())])
      .optional()
      .describe("Registered id (e.g. 'deck') or inline DesignSystem object."),
    output_path: z
      .string()
      .optional()
      .describe("Optional absolute path to write the SVG file."),
    persistent: z
      .boolean()
      .optional()
      .describe("If true, the spec is kept indefinitely (else ~24h TTL)."),
    ttlMs: z.number().int().positive().optional(),
  };

  // Generic create_chart (kept for the "I'll send a discriminated input" flow)
  server.registerTool(
    "create_chart",
    {
      title: "Create a chart (generic, type-discriminated)",
      description:
        "Render a chart as SVG. Accepts a discriminated input via 'chart' (type: bar|line|scatter|area|pie|waterfall) " +
        "plus optional design_system (id or inline), annotations, and output_path. Returns chartId, layout, viewBox, " +
        "widthPt/heightPt, and the SVG markup.",
      inputSchema: {
        chart: z.unknown().describe("ChartInput discriminated by 'type'."),
        ...RenderCommonExtras,
      },
    },
    async ({ chart, design_system, output_path, persistent, ttlMs }) => {
      const input = ChartInputSchema.parse(chart);
      return runChart(input, design_system, output_path, { persistent, ttlMs });
    },
  );

  function registerTypedChartTool(
    toolName: string,
    typeLiteral: ChartInput["type"],
    schema: z.ZodTypeAny,
    title: string,
    description: string,
  ) {
    server.registerTool(
      toolName,
      {
        title,
        description,
        inputSchema: {
          chart: z
            .unknown()
            .describe(
              `Chart input matching '${typeLiteral}' (omit 'type', it is set automatically).`,
            ),
          ...RenderCommonExtras,
        },
      },
      async ({ chart, design_system, output_path, persistent, ttlMs }) => {
        const withType = { ...(chart as object), type: typeLiteral };
        const input = schema.parse(withType) as ChartInput;
        return runChart(input, design_system, output_path, {
          persistent,
          ttlMs,
        });
      },
    );
  }

  registerTypedChartTool(
    "render_bar",
    "bar",
    BarChartSchema.extend({
      annotations: z.array(z.unknown()).optional(),
    }),
    "Render a bar chart",
    "Vertical/horizontal bar; grouped or stacked (set stacked: true). Returns the standard chart envelope.",
  );
  registerTypedChartTool(
    "render_waterfall",
    "waterfall",
    WaterfallChartSchema.extend({
      annotations: z.array(z.unknown()).optional(),
    }),
    "Render a waterfall chart",
    "Waterfall (think-cell signature). Use subtotalIndices to anchor bars to zero (totals/subtotals).",
  );
  registerTypedChartTool(
    "render_line",
    "line",
    LineChartSchema.extend({ annotations: z.array(z.unknown()).optional() }),
    "Render a line chart",
    "Single/multi-series line. Supports smoothing, point markers, endpoint labels.",
  );
  registerTypedChartTool(
    "render_scatter",
    "scatter",
    ScatterChartSchema.extend({ annotations: z.array(z.unknown()).optional() }),
    "Render a scatter / bubble chart",
    "Points in (x, y); per-point 'size' produces a bubble chart.",
  );
  registerTypedChartTool(
    "render_area",
    "area",
    AreaChartSchema.extend({ annotations: z.array(z.unknown()).optional() }),
    "Render an area chart",
    "Stacked or overlapping area; smoothing options.",
  );
  registerTypedChartTool(
    "render_pie",
    "pie",
    PieChartSchema.extend({ annotations: z.array(z.unknown()).optional() }),
    "Render a pie / donut chart",
    "Pie or donut (donut: true); auto-labeled slices >= 5%.",
  );

  // ---------- Linked-data refresh (think-cell-style) ----------

  server.registerTool(
    "update_chart",
    {
      title: "Update a stored chart with new data",
      description:
        "Re-render a previously created chart (by chartId) with replacement data. " +
        "Preserves design system, dimensions, annotations, and chart type. " +
        "Replace any of: series, values, points, slices, categories, annotations.",
      inputSchema: {
        chartId: z.string(),
        patch: z
          .record(z.unknown())
          .describe(
            "Object with replacement fields (e.g. {series:[...], categories:[...]}).",
          ),
        output_path: z.string().optional(),
      },
    },
    async ({ chartId, patch, output_path }) => {
      const stored = store.get(chartId);
      if (!stored) {
        return {
          isError: true,
          content: [{ type: "text", text: `No chart with id "${chartId}".` }],
        };
      }
      const merged = { ...(stored.spec as any), ...(patch as object) };
      const input = ChartInputSchema.parse(merged);
      const ds = registry.resolve(stored.designSystemId);
      const response = composeChart(input, ds, { chartId });
      const savedTo = await maybeSave(output_path, response.content);
      store.put(chartId, input, ds.id, response, {
        persistent: stored.persistent,
      });
      return { content: envelopeContent(response, savedTo) };
    },
  );

  server.registerTool(
    "get_chart_spec",
    {
      title: "Get the stored spec for a chart",
      description:
        "Return the original spec used to render a chart, plus the design system id. Useful for round-tripping edits.",
      inputSchema: { chartId: z.string() },
    },
    async ({ chartId }) => {
      const s = store.get(chartId);
      if (!s) {
        return {
          isError: true,
          content: [{ type: "text", text: `No chart with id "${chartId}".` }],
        };
      }
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                chartId,
                designSystemId: s.designSystemId,
                createdAt: s.createdAt,
                expiresAt: s.expiresAt,
                persistent: s.persistent,
                spec: s.spec,
              },
              null,
              2,
            ),
          },
        ],
      };
    },
  );

  return { server, registry, store };
}
