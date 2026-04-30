import http from "node:http";
import { randomUUID } from "node:crypto";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { buildServer } from "./server.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { DesignSystemRegistry } from "./design-system.js";

export interface HttpOptions {
  port: number;
  host?: string;
  path?: string;
  /** CORS origins to allow. '*' allows any (dev only). */
  corsOrigins?: string[];
  /**
   * If set, every request must carry `Authorization: Bearer <token>` matching
   * this value. Recommended for any non-localhost deployment. Keep undefined
   * to disable auth (localhost dev only).
   */
  authToken?: string;
}

interface Session {
  server: McpServer;
  transport: StreamableHTTPServerTransport;
}

/**
 * Stateful Streamable HTTP server. Each MCP client gets its own session
 * (and its own design-system registry, so brand state is per-deck/per-user).
 */
export async function startHttp(options: HttpOptions): Promise<http.Server> {
  const path = options.path ?? "/mcp";
  const cors = options.corsOrigins ?? ["*"];

  const sessions = new Map<string, Session>();

  function applyCors(req: http.IncomingMessage, res: http.ServerResponse): boolean {
    const origin = req.headers.origin;
    const allow =
      cors.includes("*") ? "*" : origin && cors.includes(origin) ? origin : null;
    if (allow) {
      res.setHeader("Access-Control-Allow-Origin", allow);
      res.setHeader("Vary", "Origin");
      res.setHeader(
        "Access-Control-Allow-Headers",
        "Content-Type, Mcp-Session-Id, Last-Event-ID, Authorization",
      );
      res.setHeader(
        "Access-Control-Allow-Methods",
        "GET, POST, DELETE, OPTIONS",
      );
      res.setHeader("Access-Control-Expose-Headers", "Mcp-Session-Id");
    }
    if (req.method === "OPTIONS") {
      res.statusCode = 204;
      res.end();
      return true;
    }
    return false;
  }

  function readBody(req: http.IncomingMessage): Promise<unknown> {
    return new Promise((resolve, reject) => {
      const chunks: Buffer[] = [];
      req.on("data", (c) => chunks.push(c as Buffer));
      req.on("end", () => {
        const raw = Buffer.concat(chunks).toString("utf8");
        if (!raw) return resolve(undefined);
        try {
          resolve(JSON.parse(raw));
        } catch (e) {
          reject(e);
        }
      });
      req.on("error", reject);
    });
  }

  function checkAuth(
    req: http.IncomingMessage,
    res: http.ServerResponse,
  ): boolean {
    if (!options.authToken) return true;
    const auth = req.headers.authorization;
    const value = Array.isArray(auth) ? auth[0] : auth;
    const expected = `Bearer ${options.authToken}`;
    if (value === expected) return true;
    res.statusCode = 401;
    res.setHeader("Content-Type", "application/json");
    res.setHeader("WWW-Authenticate", 'Bearer realm="chartsmith-mcp"');
    res.end(
      JSON.stringify({
        jsonrpc: "2.0",
        error: { code: -32001, message: "unauthorized" },
        id: null,
      }),
    );
    return false;
  }

  async function handleMcp(
    req: http.IncomingMessage,
    res: http.ServerResponse,
  ): Promise<void> {
    if (!checkAuth(req, res)) return;
    const sessionHeader = req.headers["mcp-session-id"];
    const sessionId = Array.isArray(sessionHeader)
      ? sessionHeader[0]
      : sessionHeader;

    let session = sessionId ? sessions.get(sessionId) : undefined;
    let parsedBody: unknown;

    if (req.method === "POST") {
      parsedBody = await readBody(req);
    }

    if (!session) {
      // Fresh session — only legal on POST initialize; the SDK validates.
      const { server } = buildServer({ registry: new DesignSystemRegistry() });
      const transport: StreamableHTTPServerTransport =
        new StreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          onsessioninitialized: (id: string) => {
            sessions.set(id, { server, transport });
          },
        });
      transport.onclose = () => {
        if (transport.sessionId) sessions.delete(transport.sessionId);
      };
      await server.connect(transport);
      session = { server, transport };
    }

    await session.transport.handleRequest(req, res, parsedBody);
  }

  const server = http.createServer(async (req, res) => {
    try {
      if (applyCors(req, res)) return;
      const url = new URL(req.url ?? "/", `http://${req.headers.host}`);
      if (url.pathname !== path) {
        res.statusCode = 404;
        res.end(JSON.stringify({ error: "not found" }));
        return;
      }
      await handleMcp(req, res);
    } catch (err) {
      process.stderr.write(
        `chartsmith-mcp http error: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`,
      );
      if (!res.headersSent) {
        res.statusCode = 500;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ error: "internal error" }));
      } else {
        res.end();
      }
    }
  });

  await new Promise<void>((resolve) =>
    server.listen(options.port, options.host ?? "127.0.0.1", resolve),
  );
  process.stderr.write(
    `chartsmith-mcp listening at http://${options.host ?? "127.0.0.1"}:${options.port}${path}\n`,
  );
  return server;
}
