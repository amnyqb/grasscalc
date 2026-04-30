import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { buildServer } from "./server.js";

export async function startStdio(): Promise<void> {
  const { server } = buildServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write("chartsmith-mcp ready on stdio\n");
}
