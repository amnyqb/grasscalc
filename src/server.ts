import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import {
  DesignSystemRegistry,
  DesignSystemSchema,
} from "./design-system.js";
import { ChartInputSchema, renderChart } from "./render.js";
import {
  designSystemFromPptxThemeXml,
  designSystemFromTokens,
} from "./pptx-theme.js";

export interface BuildOptions {
  registry?: DesignSystemRegistry;
}

export function buildServer(opts: BuildOptions = {}): {
  server: McpServer;
  registry: DesignSystemRegistry;
} {
  const registry = opts.registry ?? new DesignSystemRegistry();

  const server = new McpServer(
    { name: "chartsmith-mcp", version: "0.2.0" },
    {
      capabilities: { tools: {} },
      instructions:
        "Chartsmith renders publication-quality SVG charts with d3 while applying a user-defined design system. " +
        "Workflow: 1) (Optional) call theme_to_design_system with PowerPoint theme tokens or theme1.xml to register a deck-matched system. " +
        "2) Call create_chart with chart input and a design_system id (or inline tokens). " +
        "Output is an SVG string; pass output_path to also save to disk.",
    },
  );

  server.registerTool(
    "list_design_systems",
    {
      title: "List design systems",
      description:
        "List all registered design systems (built-in and user-registered). Returns id, name, palette and typography summary.",
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
      return {
        content: [{ type: "text", text: JSON.stringify(systems, null, 2) }],
      };
    },
  );

  server.registerTool(
    "register_design_system",
    {
      title: "Register a design system",
      description:
        "Register or overwrite a design system with palette, typography, layout, axes and series tokens.",
      inputSchema: {
        design_system: z
          .unknown()
          .describe(
            "A DesignSystem object. Required: id, palette.categorical (array of hex colors).",
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
      description:
        "Retrieve the full token definition for a registered design system by id.",
      inputSchema: {
        id: z
          .string()
          .describe("Design system id, e.g. 'default', 'thinkcell', 'minimal'."),
      },
    },
    async ({ id }) => {
      const ds = registry.get(id);
      if (!ds) {
        return {
          isError: true,
          content: [{ type: "text", text: `No design system with id "${id}".` }],
        };
      }
      return {
        content: [{ type: "text", text: JSON.stringify(ds, null, 2) }],
      };
    },
  );

  server.registerTool(
    "theme_to_design_system",
    {
      title: "Convert PowerPoint theme to design system",
      description:
        "Translate a PowerPoint deck's theme into a chartsmith design system, then register it. " +
        "Accepts either structured tokens (the JSON shape an Office.js add-in produces from theme1.xml) " +
        "or the raw theme1.xml string itself. Returns the registered id so subsequent create_chart calls match the deck.",
      inputSchema: {
        source: z
          .enum(["tokens", "xml"])
          .describe(
            "'tokens' for structured JSON ({accents, light1, dark1, majorFont, minorFont, ...}); 'xml' for a raw theme1.xml string.",
          ),
        payload: z
          .union([z.string(), z.record(z.unknown())])
          .describe("The tokens object or the XML string."),
        id: z
          .string()
          .optional()
          .describe(
            "Id to register under. Defaults to 'pptx-theme' (overwrites any prior).",
          ),
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

  server.registerTool(
    "create_chart",
    {
      title: "Create a chart",
      description:
        "Render a chart as SVG using d3, styled by a design system. " +
        "Chart types: bar (vertical/horizontal, grouped/stacked), line (smoothing/points), " +
        "scatter (bubble), area (stacked/overlapping), pie (donut option). " +
        "Returns the SVG markup. If output_path is provided, the SVG is also written to disk.",
      inputSchema: {
        chart: z
          .unknown()
          .describe(
            "ChartInput discriminated by 'type'. Examples: " +
              "{ type:'bar', categories:['Q1','Q2'], series:[{name:'Revenue', values:[10,12]}] }.",
          ),
        design_system: z
          .union([z.string(), z.record(z.unknown())])
          .optional()
          .describe(
            "Either a registered design system id or an inline DesignSystem object overriding tokens.",
          ),
        output_path: z
          .string()
          .optional()
          .describe(
            "Optional absolute path to write the SVG file. Parent directories are created.",
          ),
      },
    },
    async ({ chart, design_system, output_path }) => {
      const input = ChartInputSchema.parse(chart);
      const ds = registry.resolve(design_system as any);
      const svg = renderChart(input, ds);

      let savedTo: string | undefined;
      if (output_path) {
        const abs = resolve(output_path);
        await mkdir(dirname(abs), { recursive: true });
        await writeFile(abs, svg, "utf8");
        savedTo = abs;
      }

      const summary =
        `Rendered ${input.type} chart with design system "${ds.id}"` +
        (savedTo ? ` and saved to ${savedTo}.` : ".");

      return {
        content: [
          { type: "text", text: summary },
          { type: "text", text: svg },
        ],
      };
    },
  );

  return { server, registry };
}
