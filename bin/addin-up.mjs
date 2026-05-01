#!/usr/bin/env node
// Spawns the two servers the PowerPoint add-in needs:
//   1. chartsmith MCP HTTP server on :3333 (--cors '*')
//   2. HTTPS static host for addin/ on :3000
//
// Both run in the foreground; Ctrl+C kills both cleanly. Use this before
// opening PowerPoint with the Chartsmith add-in. For Claude Code stdio
// usage you don't need this at all — the stdio MCP auto-spawns per session.

import { spawn } from "node:child_process";
import { existsSync, readFileSync, statSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { createServer } from "node:https";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __filename = fileURLToPath(import.meta.url);
const root = resolve(__filename, "../..");
const addinDir = join(root, "addin");
const distEntry = join(root, "dist", "index.js");

const MCP_PORT = Number(process.env.CHARTSMITH_MCP_PORT ?? 3333);
const ADDIN_PORT = Number(process.env.CHARTSMITH_ADDIN_PORT ?? 3000);
const CERT_DIR = join(homedir(), ".office-addin-dev-certs");
const CERT = join(CERT_DIR, "localhost.crt");
const KEY = join(CERT_DIR, "localhost.key");
const CA = join(CERT_DIR, "ca.crt");

// ---------------------------------------------------------------- preflight

function fail(msg) {
  console.error(`\x1b[31m✗\x1b[0m ${msg}`);
  process.exit(1);
}

if (!existsSync(distEntry)) {
  fail(`dist/index.js not found. Run: npm run build`);
}
if (!existsSync(addinDir)) {
  fail(`addin/ directory not found at ${addinDir}`);
}
if (!existsSync(CERT) || !existsSync(KEY)) {
  fail(
    `Dev certificate not found at ${CERT_DIR}.\n  Run: npx office-addin-dev-certs install`,
  );
}

// ----------------------------------------------------------------- MCP HTTP

const mcp = spawn(
  process.execPath,
  [distEntry, "--http", "--port", String(MCP_PORT), "--cors", "*"],
  { stdio: ["ignore", "pipe", "pipe"] },
);
mcp.stdout.on("data", (d) => process.stdout.write(`\x1b[36m[mcp]\x1b[0m ${d}`));
mcp.stderr.on("data", (d) => process.stderr.write(`\x1b[36m[mcp]\x1b[0m ${d}`));
mcp.on("exit", (code) => {
  console.error(`\x1b[31m[mcp]\x1b[0m exited (${code})`);
  shutdown(code ?? 1);
});

// ----------------------------------------------------------------- HTTPS static host

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".mjs": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".xml": "text/xml; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".ico": "image/x-icon",
};

const httpsOpts = {
  cert: readFileSync(CERT),
  key: readFileSync(KEY),
  ...(existsSync(CA) ? { ca: readFileSync(CA) } : {}),
};

const httpsServer = createServer(httpsOpts, async (req, res) => {
  // CORS so the addin (running inside the Office host iframe at a different
  // origin) can fetch its own JS/manifest if needed.
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");

  const urlPath = decodeURIComponent((req.url ?? "/").split("?")[0]);
  const safe = normalize(urlPath).replace(/^(\.\.[/\\])+/, "");
  let filePath = join(addinDir, safe === "/" ? "/taskpane.html" : safe);
  if (!filePath.startsWith(addinDir)) {
    res.statusCode = 403;
    return res.end("forbidden");
  }
  try {
    const st = statSync(filePath);
    if (st.isDirectory()) filePath = join(filePath, "index.html");
    const body = await readFile(filePath);
    const type = MIME[extname(filePath).toLowerCase()] ?? "application/octet-stream";
    res.setHeader("Content-Type", type);
    res.statusCode = 200;
    res.end(body);
    console.log(`\x1b[35m[addin]\x1b[0m 200 ${urlPath}`);
  } catch (e) {
    res.statusCode = 404;
    res.end("not found");
    console.log(`\x1b[35m[addin]\x1b[0m 404 ${urlPath}`);
  }
});

httpsServer.on("error", (e) => {
  console.error(`\x1b[31m[addin]\x1b[0m ${e.message}`);
  shutdown(1);
});

httpsServer.listen(ADDIN_PORT, "127.0.0.1", () => {
  console.log(
    `\n\x1b[32m✓\x1b[0m chartsmith add-in stack up:\n` +
      `  • MCP server      http://127.0.0.1:${MCP_PORT}/mcp\n` +
      `  • Add-in (HTTPS)  https://localhost:${ADDIN_PORT}/taskpane.html\n` +
      `\n  Ctrl+C to stop both.\n`,
  );
});

// ------------------------------------------------------------- shutdown

let shuttingDown = false;
function shutdown(code = 0) {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log("\n\x1b[33m›\x1b[0m shutting down…");
  try { httpsServer.close(); } catch {}
  if (mcp.exitCode == null) mcp.kill("SIGTERM");
  setTimeout(() => process.exit(code), 200).unref();
}
process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));
