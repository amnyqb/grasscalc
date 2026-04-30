import { XMLParser } from "fast-xml-parser";
import type { DesignSystem } from "./design-system.js";
import { DesignSystemSchema, BUILTIN_DESIGN_SYSTEMS } from "./design-system.js";

/**
 * Tokens an Office.js add-in can hand us after reading the active deck's theme.
 * Designed to map cleanly to PowerPoint OOXML (theme1.xml) but consumable as plain JSON.
 */
export interface PptxThemeTokens {
  id?: string;
  name?: string;
  /** Accent colors 1..6 from theme1.xml (a:clrScheme/a:accentN). */
  accents?: string[];
  /** Light/Dark scheme colors (a:lt1/a:dk1/a:lt2/a:dk2). */
  light1?: string;
  dark1?: string;
  light2?: string;
  dark2?: string;
  /** Major (heading) and minor (body) Latin typeface names from a:fontScheme. */
  majorFont?: string;
  minorFont?: string;
}

const DEFAULT_DS = BUILTIN_DESIGN_SYSTEMS.default!;

function normalizeHex(c: string | undefined): string | undefined {
  if (!c) return undefined;
  const v = c.trim().replace(/^#/, "");
  if (!/^[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$/.test(v)) return undefined;
  return "#" + v.slice(0, 6).toLowerCase();
}

/**
 * Build a chartsmith DesignSystem from a structured token bag (what Office.js produces).
 * Anything missing falls back to the `default` design system.
 */
export function designSystemFromTokens(tokens: PptxThemeTokens): DesignSystem {
  const accents = (tokens.accents ?? [])
    .map(normalizeHex)
    .filter((v): v is string => Boolean(v));

  const categorical =
    accents.length >= 2 ? accents : DEFAULT_DS.palette.categorical;

  const background =
    normalizeHex(tokens.light1) ?? DEFAULT_DS.palette.background;
  const foreground =
    normalizeHex(tokens.dark1) ?? DEFAULT_DS.palette.foreground;
  const muted = normalizeHex(tokens.dark2) ?? DEFAULT_DS.palette.muted;
  const grid = normalizeHex(tokens.light2) ?? DEFAULT_DS.palette.grid;

  const headingFont = (tokens.majorFont ?? "").trim();
  const bodyFont = (tokens.minorFont ?? "").trim();
  const stack: string[] = [];
  if (bodyFont) stack.push(quote(bodyFont));
  if (headingFont && headingFont !== bodyFont) stack.unshift(quote(headingFont));
  stack.push(DEFAULT_DS.typography.fontFamily);
  const fontFamily = stack.join(", ");

  return DesignSystemSchema.parse({
    id: tokens.id ?? "pptx-theme",
    name: tokens.name ?? "PowerPoint theme",
    palette: {
      categorical,
      sequential: DEFAULT_DS.palette.sequential,
      diverging: DEFAULT_DS.palette.diverging,
      background,
      foreground,
      muted,
      grid,
    },
    typography: { ...DEFAULT_DS.typography, fontFamily },
    layout: DEFAULT_DS.layout,
    axes: DEFAULT_DS.axes,
    series: DEFAULT_DS.series,
  });
}

function quote(name: string): string {
  return /[\s,]/.test(name) ? `"${name}"` : name;
}

/**
 * Parse a PowerPoint theme1.xml string and extract the tokens we care about.
 * Schema reference: ECMA-376 DrawingML a:theme/a:themeElements/{a:clrScheme, a:fontScheme}.
 */
export function parsePptxThemeXml(xml: string): PptxThemeTokens {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "@_",
    removeNSPrefix: true,
    allowBooleanAttributes: true,
  });
  const doc = parser.parse(xml);

  const themeElements =
    doc?.theme?.themeElements ?? doc?.["a:theme"]?.["a:themeElements"];
  if (!themeElements) {
    throw new Error(
      "Could not find a:theme/a:themeElements in the supplied XML.",
    );
  }

  const clr = themeElements.clrScheme ?? {};
  const accents = [
    extractColor(clr.accent1),
    extractColor(clr.accent2),
    extractColor(clr.accent3),
    extractColor(clr.accent4),
    extractColor(clr.accent5),
    extractColor(clr.accent6),
  ].filter((v): v is string => Boolean(v));

  const tokens: PptxThemeTokens = {
    accents,
    light1: extractColor(clr.lt1),
    dark1: extractColor(clr.dk1),
    light2: extractColor(clr.lt2),
    dark2: extractColor(clr.dk2),
  };

  const fonts = themeElements.fontScheme ?? {};
  tokens.majorFont = extractLatinFont(fonts.majorFont);
  tokens.minorFont = extractLatinFont(fonts.minorFont);

  const themeName = doc?.theme?.["@_name"] ?? doc?.["a:theme"]?.["@_name"];
  if (themeName) tokens.name = themeName;

  return tokens;
}

function extractColor(node: any): string | undefined {
  if (!node) return undefined;
  const srgb = node.srgbClr;
  if (srgb?.["@_val"]) return normalizeHex(srgb["@_val"]);
  const sys = node.sysClr;
  if (sys?.["@_lastClr"]) return normalizeHex(sys["@_lastClr"]);
  return undefined;
}

function extractLatinFont(node: any): string | undefined {
  if (!node) return undefined;
  const latin = node.latin;
  if (latin?.["@_typeface"]) return String(latin["@_typeface"]);
  return undefined;
}

/**
 * One-shot helper: parse XML → tokens → DesignSystem.
 */
export function designSystemFromPptxThemeXml(
  xml: string,
  overrides: { id?: string; name?: string } = {},
): DesignSystem {
  const tokens = parsePptxThemeXml(xml);
  return designSystemFromTokens({ ...tokens, ...overrides });
}
