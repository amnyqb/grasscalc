#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import {
  DesignSystemRegistry,
  DesignSystemSchema,
} from "./design-system.js";
import { ChartInputSchema, renderChart } from "./render.js";

const registry = new DesignSystemRegistry();

const server = new McpServer(
  {
    name: "chartsmith-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
    instructions:
      "Chartsmith renders publication-quality SVG charts with d3 while applying a user-defined design system. " +
      "Workflow: 1) Optionally call list_design_systems and register_design_system to set up tokens. " +
      "2) Call create_chart with type ('bar'|'line'|'scatter'|'area'|'pie'), data, and design_system (id or inline). " +
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
      content: [
        { type: "text", text: JSON.stringify(systems, null, 2) },
      ],
    };
  },
);

server.registerTool(
  "register_design_system",
  {
    title: "Register a design system",
    description:
      "Register or overwrite a design system with palette, typography, layout, axes and series tokens. " +
      "Use this to encode a brand or user preference once, then reference by id when creating charts.",
    inputSchema: {
      design_system: z
        .unknown()
        .describe(
          "A DesignSystem object. Required: id, palette.categorical (array of hex colors). " +
            "Optional fields fall back to sensible defaults.",
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
    inputSchema: {
      id: z.string().describe("Design system id, e.g. 'default', 'thinkcell', 'minimal'."),
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
  "create_chart",
  {
    title: "Create a chart",
    description:
      "Render a chart as SVG using d3, styled by a design system. " +
      "Chart types: bar (vertical/horizontal, grouped/stacked), line (with optional smoothing/points), " +
      "scatter (with optional bubble sizing), area (stacked or overlapping), pie (with donut option). " +
      "Returns the SVG markup. If output_path is provided, the SVG is also written to disk.",
    inputSchema: {
      chart: z
        .unknown()
        .describe(
          "ChartInput discriminated by 'type'. Examples: " +
            "{ type:'bar', categories:['Q1','Q2'], series:[{name:'Revenue', values:[10,12]}] }, " +
            "{ type:'line', series:[{name:'A', points:[{x:1,y:2}]}] }, " +
            "{ type:'pie', slices:[{label:'Foo', value:30}] }.",
        ),
      design_system: z
        .union([z.string(), z.record(z.unknown())])
        .optional()
        .describe(
          "Either a registered design system id (e.g. 'default', 'thinkcell') or an inline DesignSystem object overriding tokens.",
        ),
      output_path: z
        .string()
        .optional()
        .describe("Optional absolute path to write the SVG file. Parent directories are created."),
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

    const summary = `Rendered ${input.type} chart with design system "${ds.id}"` +
      (savedTo ? ` and saved to ${savedTo}.` : ".");

    return {
      content: [
        { type: "text", text: summary },
        { type: "text", text: svg },
      ],
    };
  },
);

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write("chartsmith-mcp ready on stdio\n");
}

main().catch((err) => {
  process.stderr.write(
    `chartsmith-mcp fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`,
  );
  process.exit(1);
});
