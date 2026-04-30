#!/usr/bin/env node
import { startStdio } from "./stdio.js";
import { startHttp } from "./http.js";

interface CliOptions {
  transport: "stdio" | "http";
  port: number;
  host: string;
  path: string;
  corsOrigins?: string[];
}

function parseArgs(argv: string[]): CliOptions {
  const opts: CliOptions = {
    transport: "stdio",
    port: 3333,
    host: "127.0.0.1",
    path: "/mcp",
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case "--http":
        opts.transport = "http";
        break;
      case "--stdio":
        opts.transport = "stdio";
        break;
      case "--port":
        opts.port = Number(argv[++i]);
        break;
      case "--host":
        opts.host = String(argv[++i]);
        break;
      case "--path":
        opts.path = String(argv[++i]);
        break;
      case "--cors":
        opts.corsOrigins = String(argv[++i]).split(",").map((s) => s.trim());
        break;
      case "--help":
      case "-h":
        printHelp();
        process.exit(0);
        break;
      default:
        process.stderr.write(`Unknown argument: ${a}\n`);
        printHelp();
        process.exit(2);
    }
  }
  if (opts.transport === "http" && (!opts.port || Number.isNaN(opts.port))) {
    throw new Error("--port is required when --http is used.");
  }
  return opts;
}

function printHelp(): void {
  process.stderr.write(
    [
      "chartsmith-mcp [options]",
      "",
      "Transports:",
      "  --stdio                 (default) MCP stdio transport for local clients",
      "  --http                  Streamable HTTP transport for remote/web clients",
      "",
      "HTTP options:",
      "  --port <n>              Port to listen on (default 3333)",
      "  --host <h>              Host to bind (default 127.0.0.1)",
      "  --path <p>              Endpoint path (default /mcp)",
      "  --cors <a,b,c>          Comma-separated allowed origins (default *)",
      "",
    ].join("\n"),
  );
}

async function main(): Promise<void> {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.transport === "stdio") {
    await startStdio();
  } else {
    await startHttp({
      port: opts.port,
      host: opts.host,
      path: opts.path,
      corsOrigins: opts.corsOrigins,
    });
  }
}

main().catch((err) => {
  process.stderr.write(
    `chartsmith-mcp fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`,
  );
  process.exit(1);
});
