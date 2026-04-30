/**
 * Minimal Streamable HTTP MCP client for the browser.
 * Handles initialize / tools/call with session-id round-tripping.
 */
export class McpClient {
  constructor(url) {
    this.url = url;
    this.sessionId = null;
    this.nextId = 0;
    this.initialized = false;
  }

  async initialize() {
    const id = ++this.nextId;
    const res = await fetch(this.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "chartsmith-addin", version: "0.1.0" },
        },
      }),
    });
    if (!res.ok) {
      throw new Error(`initialize failed: ${res.status} ${await res.text()}`);
    }
    this.sessionId = res.headers.get("mcp-session-id");
    if (!this.sessionId) throw new Error("server did not return Mcp-Session-Id");
    await this._readSseOrJson(res, id);

    // Send notifications/initialized.
    await fetch(this.url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "notifications/initialized",
      }),
    });
    this.initialized = true;
  }

  async callTool(name, args = {}) {
    if (!this.initialized) await this.initialize();
    const id = ++this.nextId;
    const res = await fetch(this.url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({
        jsonrpc: "2.0",
        id,
        method: "tools/call",
        params: { name, arguments: args },
      }),
    });
    if (!res.ok) {
      throw new Error(`tools/call ${name} failed: ${res.status} ${await res.text()}`);
    }
    const message = await this._readSseOrJson(res, id);
    if (message.error) throw new Error(`${name}: ${message.error.message}`);
    if (message.result?.isError) {
      throw new Error(message.result.content?.[0]?.text ?? `${name} returned isError`);
    }
    return message.result;
  }

  _headers() {
    return {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      "Mcp-Session-Id": this.sessionId,
    };
  }

  /**
   * Streamable HTTP responses are SSE. We only consume the first matching
   * message (id == awaited id). For our usage that's always a single
   * response per request.
   */
  async _readSseOrJson(res, expectedId) {
    const ct = res.headers.get("content-type") ?? "";
    const text = await res.text();
    if (ct.includes("application/json")) {
      const m = JSON.parse(text);
      return m;
    }
    // Parse SSE: split on \n\n, look for "data: " lines.
    for (const block of text.split(/\r?\n\r?\n/)) {
      const dataLines = block
        .split(/\r?\n/)
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trimStart());
      if (!dataLines.length) continue;
      const json = dataLines.join("\n");
      try {
        const m = JSON.parse(json);
        if (m.id === expectedId) return m;
      } catch {
        // ignore non-JSON SSE lines
      }
    }
    throw new Error("no matching SSE message in response");
  }
}

/**
 * Parses the chartsmith envelope out of an MCP tools/call result.
 * Our server returns content[0] = JSON metadata, content[1] = SVG markup.
 */
export function parseChartEnvelope(result) {
  const content = result.content ?? [];
  if (content.length < 2) throw new Error("envelope missing SVG content block");
  const meta = JSON.parse(content[0].text);
  const svg = content[1].text;
  return { ...meta, svg };
}
