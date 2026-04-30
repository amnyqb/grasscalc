# Chartsmith — PowerPoint task-pane add-in

A structured chart authoring tool for PowerPoint, backed by the
chartsmith MCP server. **No chat input** — you pick a chart type,
edit data in a grid, toggle annotations, preview, then insert.

```
PowerPoint  ──►  Chartsmith task pane  ──HTTP──►  chartsmith-mcp
                  │                                │
                  ├─ chart type picker             ├─ create_chart
                  ├─ editable data grid            ├─ update_chart
                  ├─ live SVG preview              └─ get_chart_spec
                  ├─ annotation toggles
                  └─ insert / update buttons
```

## What's in here

| File | Purpose |
|---|---|
| `manifest.xml` | Office add-in manifest (sideload-only id; replace before publishing). |
| `taskpane.html` | Single-page UI shell. |
| `taskpane.css` | Styles. Uses Segoe UI to match Office. |
| `taskpane.js` | Orchestrator — picker, preview debounce, Insert/Update wiring. |
| `chart-types.js` | Type registry, SVG thumbnails, annotation capability map, default data. |
| `grids.js` | Editable data grids per type (rowsByCategory / pointsBySeries / slices / waterfall). Excel-paste supported. |
| `mcp-client.js` | Tiny browser-side MCP Streamable HTTP client (initialize + tools/call, SSE-aware). |

## What it does

1. **Connect.** On open, the task pane connects to `http://localhost:3333/mcp`
   (configurable in the Server section). It calls `list_design_systems` to
   populate the design-system picker.
2. **Pick a type.** Six thumbnails: bar, waterfall, line, scatter, area, pie.
3. **Edit data.** Per-type grid; double-click a header to rename a series.
   Excel paste (TSV / CSV with newlines) works on any cell.
4. **Toggle annotations.** CAGR arrow + total labels. The toggles auto-disable
   for chart types that don't support them (e.g. CAGR doesn't apply to pie).
5. **Live preview.** Edits debounce 200ms, then call `create_chart` with
   `persistent: true`. The returned SVG is injected into the preview pane.
   Warnings (label collisions, unresolved refs) appear below the preview.
6. **Insert.** Rasterizes SVG → PNG (2× DPI) and inserts into the active slide
   via `slide.shapes.addImage`. Tags the shape with the chartId.
7. **Update.** When a previously-inserted chartsmith shape is selected,
   the Update button is enabled. It pushes a data patch via `update_chart`
   (preserves chartId server-side), rasterizes the new SVG, and replaces
   the picture at the original position/size.
8. **Round-trip edits.** Selecting a chartsmith shape hydrates the form
   via `get_chart_spec` so you can edit the values that produced it.

## Running it

### 1. Start the MCP server in HTTP mode

From the repo root:

```bash
npm install
npm run build
node dist/index.js --http --port 3333 --cors '*'
```

### 2. Serve the add-in over HTTPS

PowerPoint requires HTTPS for the task-pane source. Quickest path:

```bash
# Install once
npm install -g office-addin-dev-certs
npx office-addin-dev-certs install

# Serve the addin/ directory on https://localhost:3000
npx http-server addin -p 3000 -S \
  -C ~/.office-addin-dev-certs/localhost.crt \
  -K ~/.office-addin-dev-certs/localhost.key
```

(or use `npx office-addin-debugging start manifest.xml desktop`)

### 3. Sideload the manifest

- **PowerPoint Web:** Insert → Add-ins → Upload My Add-in → pick `manifest.xml`.
- **PowerPoint Desktop (Mac):** copy `manifest.xml` to
  `~/Library/Containers/com.microsoft.Powerpoint/Data/Documents/wef/`,
  then Insert → My Add-ins → Chartsmith.
- **PowerPoint Desktop (Windows):** create a network share or use the
  Microsoft 365 Admin Center; for sideload-only set
  `Insert → Add-ins → My Add-ins → SHARED FOLDER` to a local folder
  containing `manifest.xml`.

### 4. Open the task pane

Insert tab → **Chartsmith** group → **Open**. The pane auto-connects to
`localhost:3333`. Tweak the URL in the Server section if needed.

## Dev-mode preview without PowerPoint

You can open `https://localhost:3000/taskpane.html` in a normal browser.
Office.js degrades gracefully: chart picker, grid, and live preview all
work; the Insert/Update buttons just alert ("Insert is only available
inside PowerPoint").

## Deck-theme bridge ("Use deck theme" button)

In the Server section, the **Use deck theme** button:

1. Calls `Office.context.document.getFileAsync(Office.FileType.Compressed)`
   and assembles the .pptx bytes from slices.
2. Loads them with [JSZip](https://stuk.github.io/jszip/) (CDN-loaded in
   `taskpane.html`) and pulls `ppt/theme/theme1.xml` (with fallback to
   any `ppt/theme/themeN.xml`).
3. Posts the XML to chartsmith's `theme_to_design_system` tool with
   `id: "deck"`. The server parses `a:clrScheme` (accent1–6 → categorical
   palette, `lt1`/`dk1` → bg/fg, `lt2`/`dk2` → grid/muted) and
   `a:fontScheme` (major/minor Latin → font stack), registers the result.
4. Selects "deck" in the design-system dropdown and triggers a re-render.

Implementation: `addin/deck-theme.js` (extractor, transport-agnostic).
Verified end-to-end with a synthetic .pptx in
`/tmp/deck-theme-smoke.mjs` — the addin's exact JS modules pull the
theme, hit a real chartsmith server, and render charts in deck colors
without any PowerPoint involvement.

## Insert mode: image vs native

The action area has a radio toggle:

- **Image (with annotations)** — default. Renders SVG via chartsmith
  (with all annotation overlays — CAGR arrow, totals, brackets, etc.),
  rasterizes to PNG @2× DPI, inserts via `slide.shapes.addImage`. The
  picture is tagged with `CHARTSMITH_ID` so Update can replace it in
  place; selecting the picture later hydrates the form via
  `get_chart_spec`.

- **Native chart (editable)** — inserts a real PowerPoint chart shape
  via `slide.shapes.addChart`. Double-click in PowerPoint to edit the
  data; respects animations; theme-linked. Trade-offs:
    - chartsmith annotations (CAGR, totals, brackets, callouts,
      reference lines, range bands) are dropped — they live in our
      SVG overlay layer, not in the OOXML chart part. The UI surfaces
      a warning when annotations were toggled on.
    - chart visuals are PowerPoint's defaults, not chartsmith's
      design-system spacing — but we apply the design system's
      categorical palette to the series fills via
      `series.format.fill.setSolidColor`, best-effort.
    - Update flow is a no-op in native mode: edit the chart's data
      directly in PowerPoint, or delete + re-insert from chartsmith.

The chartsmith → PowerPoint chart-type mapping (see `native-chart.js`):

| chartsmith | PowerPoint.ChartType |
|---|---|
| bar (grouped/stacked, vertical/horizontal) | columnClustered / columnStacked / barClustered / barStacked |
| line | line |
| scatter | xyscatter |
| area (stacked/unstacked) | areaStacked / area |
| pie / donut | pie / doughnut |
| waterfall | waterfall (PowerPoint 2016+) |

Pure transforms (`mapChartType`, `shapeData`) are tested in
`addin/__tests__/native-chart.test.mjs` (20 cases, runs with plain
`node` — no PowerPoint or browser needed).

## Why not full hand-rolled OOXML?

We intentionally use Office.js `addChart` instead of emitting an OOXML
`<c:chart>` part by hand. PowerPoint generates the OOXML internally
when we hand it data + a chart type, which gives us native editability
without a multi-day schema-tracking effort. Hand-rolled OOXML is still
on the table for things `addChart` doesn't expose (custom fill
patterns, exotic chart subtypes), but for 95% of decks the Office.js
path is the right call.

## Known gaps / next iterations
- **Auth / non-localhost MCP.** Dev mode assumes the server is on
  `localhost`. Real deployment needs auth (bearer token at minimum) and
  a non-`*` CORS allowlist.
- **Manifest icons.** The 16/32/80 icons are referenced but not yet
  shipped. Add PNGs to `addin/assets/` before publishing.
- **Annotation surface area.** Only CAGR + totals are exposed as
  toggles. Delta, bracket, callout, reference_line, range_band are all
  supported by the engine — they need UI affordances (drag-to-anchor,
  label inputs).
