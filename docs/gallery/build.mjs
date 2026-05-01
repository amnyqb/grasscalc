// Reproducible gallery builder.
//
//   npm run build              # compile TS
//   node docs/gallery/build.mjs
//
// Imports the chartsmith engine directly (no MCP transport overhead),
// renders 9 representative scenarios, writes both SVG and PNG @1400px wide.
//
// This is the canonical "what does chartsmith look like" reference. Run it
// after any visual change; commit the resulting PNGs so README renders on
// GitHub without anyone needing to spin the engine up.

import { writeFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { Resvg } from "@resvg/resvg-js";
import { readFile } from "node:fs/promises";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "../..");
const outDir = here;

// Use the compiled engine. ChartInputSchema is the discriminated Zod union
// over every chart type — parse() applies defaults (showValues, valueFormat,
// padding, etc.) so we mirror what the MCP server does in tool handlers.
const { composeChart, ChartInputSchema } = await import(
  join(root, "dist/render.js")
);
const { DesignSystemRegistry } = await import(
  join(root, "dist/design-system.js")
);
const { designSystemFromPptxThemeXml } = await import(
  join(root, "dist/pptx-theme.js")
);

const registry = new DesignSystemRegistry();

// --- Register a "deck" design system from the sample brand theme1.xml ---
// We ship a small synthetic theme1.xml under docs/gallery/sample-theme1.xml.
// (mirrors what the addin would extract from a real .pptx)
const deckThemeXml = await readFile(join(here, "sample-theme1.xml"), "utf8");
registry.register(
  designSystemFromPptxThemeXml(deckThemeXml, { id: "deck", name: "Active deck" }),
);

let chartCounter = 0;
function nextId() {
  return `gallery-${++chartCounter}`;
}

async function render(name, input, dsId, caption) {
  const ds = registry.resolve(dsId);
  const parsed = ChartInputSchema.parse(input);
  const resp = composeChart(parsed, ds, { chartId: nextId() });
  const svgPath = join(outDir, `${name}.svg`);
  await writeFile(svgPath, resp.content);
  const png = new Resvg(resp.content, {
    fitTo: { mode: "width", value: 1400 },
  })
    .render()
    .asPng();
  const pngPath = join(outDir, `${name}.png`);
  await writeFile(pngPath, png);
  console.log(
    `${name.padEnd(36)} ${dsId.padEnd(10)}  warnings=${resp.warnings.length}  ${caption}`,
  );
}

await mkdir(outDir, { recursive: true });

// =========================================================================
// 01. Waterfall bridge — think-cell signature, all-in-one demo
// =========================================================================
await render(
  "01-waterfall-bridge",
  {
    type: "waterfall",
    title: "EBITDA Bridge — FY24 → FY25",
    subtitle: "Drivers of $20M YoY growth",
    source: "Source: Finance, FY25 plan",
    widthPt: 760,
    heightPt: 460,
    categories: ["FY24", "Volume", "Price", "Mix", "Cost", "FX", "FY25"],
    values: [120, 18, 12, -5, -8, 3, 140],
    subtotalIndices: [0, 6],
    valueFormat: "+,.0f",
    annotations: [
      { type: "bracket", from: { x: "FY24" }, to: { x: "FY25" }, label: "+18%" },
    ],
  },
  "thinkcell",
  "Subtotals, connectors, +/- coloring, headline bracket",
);

// =========================================================================
// 02. Stacked bar with CAGR arrow + total labels
// =========================================================================
await render(
  "02-stacked-bar-cagr",
  {
    type: "bar",
    title: "Revenue by Region — FY21–FY24",
    subtitle: "Stacked, with category totals and CAGR on APAC",
    widthPt: 760,
    heightPt: 460,
    categories: ["FY21", "FY22", "FY23", "FY24"],
    stacked: true,
    valueFormat: ",.0f",
    series: [
      { name: "EMEA", values: [40, 50, 60, 75] },
      { name: "AMER", values: [60, 70, 85, 100] },
      { name: "APAC", values: [20, 30, 45, 65] },
    ],
    annotations: [
      // top-of-stack series ref (auto-picked by addin in the real flow)
      {
        type: "cagr_arrow",
        from: { x: "FY21", series: "APAC" },
        to: { x: "FY24", series: "APAC" },
        format: ".1%",
      },
      { type: "total_labels", format: ",.0f" },
    ],
  },
  "thinkcell",
  "Stacked totals + APAC CAGR arrow",
);

// =========================================================================
// 03. Multi-annotation line — delta + reference line + endpoint label
// =========================================================================
await render(
  "03-line-multi-annotation",
  {
    type: "line",
    title: "Weekly Active Users — H1 vs target",
    widthPt: 760,
    heightPt: 460,
    smoothing: "monotone",
    showPoints: true,
    showEndpointLabels: true,
    valueFormat: ",.0f",
    series: [
      {
        name: "WAU",
        points: Array.from({ length: 12 }, (_, i) => ({
          x: i + 1,
          y: 100 + 18 * i + 8 * Math.sin(i * 1.1),
        })),
      },
    ],
    annotations: [
      {
        type: "delta",
        from: { x: 1, series: "WAU" },
        to: { x: 12, series: "WAU" },
        format: "+,.0f",
      },
      {
        type: "reference_line",
        axis: "y",
        value: 280,
        label: "Target",
        style: "dashed",
      },
    ],
  },
  "default",
  "Delta bracket, target reference line, endpoint label",
);

// =========================================================================
// 04. Deck-theme bridge — same chart, default vs deck
// =========================================================================
const sameStackedBar = (extra = {}) => ({
  type: "bar",
  title: "Pipeline by Stage — Q1",
  widthPt: 720,
  heightPt: 440,
  categories: ["Lead", "Qualified", "Proposal", "Won"],
  stacked: true,
  valueFormat: ",.0f",
  series: [
    { name: "EMEA", values: [40, 30, 20, 10] },
    { name: "AMER", values: [50, 40, 30, 20] },
  ],
  ...extra,
});
await render(
  "04a-default-theme",
  sameStackedBar(),
  "default",
  "Out-of-the-box default DS",
);
await render(
  "04b-deck-theme",
  sameStackedBar(),
  "deck",
  "Same chart, deck DS extracted from theme1.xml",
);

// =========================================================================
// 05. Three design systems, same waterfall — proves DS-driven layout
// =========================================================================
const sameWaterfall = () => ({
  type: "waterfall",
  title: "Quarterly Bridge",
  widthPt: 640,
  heightPt: 380,
  categories: ["Q1", "Vol", "Px", "Cost", "Q2"],
  values: [100, 12, 8, -6, 114],
  subtotalIndices: [0, 4],
  valueFormat: "+,.0f",
});
await render("05a-default", sameWaterfall(), "default", "");
await render("05b-thinkcell", sameWaterfall(), "thinkcell", "");
await render("05c-minimal", sameWaterfall(), "minimal", "");

// =========================================================================
// 06. Donut — traffic sources
// =========================================================================
await render(
  "06-donut",
  {
    type: "pie",
    title: "Traffic Sources",
    widthPt: 560,
    heightPt: 440,
    donut: true,
    showValues: true,
    slices: [
      { label: "Direct", value: 38 },
      { label: "Search", value: 32 },
      { label: "Social", value: 18 },
      { label: "Referral", value: 12 },
    ],
  },
  "deck",
  "Donut with auto-percent labels (>5%)",
);

// =========================================================================
// 07. Scatter / bubble — latency vs throughput
// =========================================================================
function pseudoRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}
const rA = pseudoRandom(1);
const rB = pseudoRandom(2);
await render(
  "07-scatter-bubble",
  {
    type: "scatter",
    title: "Latency vs Throughput by Service",
    xLabel: "Throughput (rps)",
    yLabel: "p99 latency (ms)",
    widthPt: 760,
    heightPt: 460,
    series: [
      {
        name: "service A",
        points: Array.from({ length: 24 }, () => ({
          x: rA() * 1000,
          y: 50 + rA() * 160,
          size: rA() * 30 + 5,
        })),
      },
      {
        name: "service B",
        points: Array.from({ length: 24 }, () => ({
          x: rB() * 1000,
          y: 80 + rB() * 220,
          size: rB() * 30 + 5,
        })),
      },
    ],
  },
  "default",
  "Bubble size encodes a third dimension",
);

// =========================================================================
// 08. Linked-data refresh — before/after with same chart
// =========================================================================
const cohortBefore = {
  type: "area",
  title: "Cohort Composition — actual",
  widthPt: 720,
  heightPt: 420,
  categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  stacked: true,
  smoothing: "monotone",
  series: [
    { name: "Free", values: [120, 150, 180, 200, 220, 260] },
    { name: "Pro", values: [30, 45, 60, 90, 110, 140] },
    { name: "Enterprise", values: [10, 12, 18, 25, 35, 50] },
  ],
};
const cohortAfter = {
  ...cohortBefore,
  title: "Cohort Composition — updated",
  series: [
    { name: "Free", values: [120, 150, 180, 200, 220, 260] },
    { name: "Pro", values: [30, 45, 60, 95, 130, 175] },
    { name: "Enterprise", values: [10, 12, 18, 30, 50, 80] },
  ],
};
await render("08a-cohort-before", cohortBefore, "thinkcell", "Before refresh");
await render("08b-cohort-after", cohortAfter, "thinkcell", "After update_chart");

// =========================================================================
// 09. Horizontal grouped bar (showcase orientation flag)
// =========================================================================
await render(
  "09-horizontal-grouped",
  {
    type: "bar",
    title: "Customer NPS — by Segment",
    widthPt: 720,
    heightPt: 460,
    orientation: "horizontal",
    showValues: true,
    valueFormat: "+,.0f",
    categories: ["SMB", "Mid-Market", "Enterprise", "Strategic"],
    series: [
      { name: "FY23", values: [22, 35, 41, 56] },
      { name: "FY24", values: [28, 38, 44, 62] },
    ],
  },
  "minimal",
  "Horizontal grouped bar in the minimal DS",
);

console.log(`\nDone. ${chartCounter} charts written to ${outDir}`);
