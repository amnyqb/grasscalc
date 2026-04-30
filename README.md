# chartsmith-mcp

An MCP server that lets Claude (or any MCP-capable client) generate
publication-quality charts via [d3](https://d3js.org/), styled by a
**design system** the user controls.

Think of it as **think-cell for AI**: the LLM decides *what* to chart;
chartsmith decides *how* it looks, consistently, every time.

## Why

LLMs are great at picking the right chart and shaping the data, but bad at
consistent visual design. Chartsmith inverts the responsibility:

- **The LLM** sends structured chart input (type, data, labels).
- **Chartsmith** owns colors, typography, axes, spacing, gridlines,
  legend layout, corner radii — the entire visual language.
- **The user** registers a design system once (brand palette, fonts,
  whitespace, axis style). Every chart Claude renders inherits it.

The output is a self-contained SVG string — embed it in a doc, slide,
PDF, or web page.

## Tools exposed

| Tool | Purpose |
|---|---|
| `list_design_systems` | List built-in and user-registered systems. |
| `register_design_system` | Add or overwrite a design system by id. |
| `get_design_system` | Inspect a registered system's tokens. |
| `theme_to_design_system` | Convert a PowerPoint deck's theme (tokens or theme1.xml) into a registered design system — for the Office add-in flow. |
| `create_chart` | Render a chart as SVG (and optionally save to disk). |

Built-in design systems: `default`, `thinkcell`, `minimal`.

## Chart types

- **bar** — vertical/horizontal, grouped or stacked
- **line** — single/multi-series, optional smoothing and point markers
- **scatter** — optional bubble sizing
- **area** — stacked or overlapping, optional smoothing
- **pie** — with donut option

## Install / run

```bash
npm install
npm run build

# Local (Claude Desktop, Claude Code) — stdio
node dist/index.js

# Remote (Office.js add-in, web client) — Streamable HTTP
node dist/index.js --http --port 3333 --cors '*'
```

### Claude Code / Claude Desktop config (stdio)

```jsonc
{
  "mcpServers": {
    "chartsmith": {
      "command": "node",
      "args": ["/absolute/path/to/chartsmith-mcp/dist/index.js"]
    }
  }
}
```

### HTTP transport options

```
--http                 use Streamable HTTP transport
--port <n>             listen port (default 3333)
--host <h>             bind host (default 127.0.0.1)
--path <p>             endpoint path (default /mcp)
--cors <a,b,c>         allowed origins (default *)
```

The HTTP server is **stateful**: each client gets a session via the
`Mcp-Session-Id` response header and must echo it on subsequent requests.
User-registered design systems are scoped to that session — so two decks
or two users don't see each other's tokens.

## PowerPoint add-in flow

The intended client is a Claude task-pane add-in inside PowerPoint. The
add-in uses Office.js to read the deck's active theme, hands the tokens
to chartsmith via `theme_to_design_system`, then asks Claude to call
`create_chart` for whatever the user describes:

```
PowerPoint
  └─► Claude task-pane add-in (Office.js, runs in iframe)
        ├─► Anthropic API (Claude)
        │     └─► tools/call → chartsmith-mcp (HTTP/SSE)
        │           ├─ theme_to_design_system  ← deck's theme1.xml or tokens
        │           └─ create_chart            ← inherits deck palette + fonts
        └─► Office.js → insert SVG/PNG (or, future, native OOXML chart)
```

Two integration tiers:

1. **MVP today** — addon rasterizes the returned SVG to PNG and inserts
   it as a picture. Works immediately; chart is not editable in PPT.
2. **Native (future)** — add a `create_pptx_chart` tool that emits an
   OOXML `<c:chart>` part. Office.js inserts it as a real PowerPoint
   chart shape (double-click to edit data, animatable, theme-linked).
   This is the actual think-cell-grade integration.

## Design system shape

```ts
{
  id: "acme",
  name: "Acme Corp",
  palette: {
    categorical: ["#0a3d62", "#38ada9", "#e58e26", "#b71540"],
    background: "#ffffff",
    foreground: "#0b1d3a",
    muted: "#5a6b85",
    grid: "#dde3ec"
  },
  typography: {
    fontFamily: "Inter, sans-serif",
    titleSize: 16, titleWeight: 600,
    labelSize: 12, labelWeight: 400,
    tickSize: 11
  },
  layout: { padding: { top: 32, right: 24, bottom: 48, left: 56 }, cornerRadius: 4 },
  axes:   { showGridX: false, showGridY: true, axisLineWidth: 1, tickLength: 4 },
  series: { strokeWidth: 2, pointRadius: 3, barGap: 0.15, groupGap: 0.25 }
}
```

Only `id` and `palette.categorical` are required; everything else falls
back to the `default` system.

## Example calls

### Bar chart with the `thinkcell` look

```json
{
  "name": "create_chart",
  "arguments": {
    "chart": {
      "type": "bar",
      "title": "Quarterly Revenue",
      "categories": ["Q1", "Q2", "Q3", "Q4"],
      "series": [
        { "name": "EMEA", "values": [12, 18, 21, 25] },
        { "name": "AMER", "values": [22, 24, 27, 31] }
      ]
    },
    "design_system": "thinkcell",
    "output_path": "/tmp/revenue.svg"
  }
}
```

### Line chart with inline brand tokens

```json
{
  "name": "create_chart",
  "arguments": {
    "chart": {
      "type": "line",
      "smooth": true,
      "showPoints": true,
      "series": [
        { "name": "Signups", "points": [{"x":1,"y":120},{"x":2,"y":180},{"x":3,"y":260}] }
      ]
    },
    "design_system": {
      "id": "brand",
      "palette": { "categorical": ["#ff5a5f"], "background": "#fffaf0", "foreground": "#222" }
    }
  }
}
```

## Theme-to-design-system call

```json
{
  "name": "theme_to_design_system",
  "arguments": {
    "source": "tokens",
    "id": "deck",
    "payload": {
      "accents": ["#0A3D62","#38ADA9","#E58E26","#B71540","#6C5CE7","#20BF6B"],
      "light1": "#FBFBFA",
      "dark1":  "#0B1D3A",
      "light2": "#DDE3EC",
      "dark2":  "#5A6B85",
      "majorFont": "Inter",
      "minorFont": "Inter"
    }
  }
}
```

Or hand it the raw `theme1.xml` from the deck's `.pptx`:

```json
{
  "name": "theme_to_design_system",
  "arguments": { "source": "xml", "id": "deck", "payload": "<a:theme ...>...</a:theme>" }
}
```

Both register a system with the supplied id. Subsequent `create_chart`
calls reference it via `"design_system": "deck"`.

## Project layout

```
src/
  index.ts            CLI dispatcher (--stdio / --http)
  stdio.ts            stdio transport entry
  http.ts             Streamable HTTP transport (sessions + CORS)
  server.ts           MCP server + tool registrations (transport-agnostic)
  design-system.ts    Tokens + registry + Zod schema
  pptx-theme.ts       PowerPoint theme1.xml + token-bag → DesignSystem
  render.ts           Discriminated chart input + dispatcher
  charts/
    common.ts         JSDOM/d3 frame, axes, legend, serialization
    bar.ts            Grouped + stacked, vertical + horizontal
    line.ts           Multi-series, smoothing, point markers
    scatter.ts        With optional bubble sizing
    area.ts           Stacked + overlapping
    pie.ts            With donut variant
```

## Notes

- Server-side d3 runs inside JSDOM; output is a static SVG string.
- The MCP server uses stdio transport (`@modelcontextprotocol/sdk`).
- Type-safe end-to-end via Zod schemas shared between MCP input and renderers.
