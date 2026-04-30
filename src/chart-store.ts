import { randomUUID } from "node:crypto";
import type { ChartInput } from "./render.js";
import type { ChartResponse } from "./types.js";

export interface StoredChart {
  spec: ChartInput;
  designSystemId: string;
  response: ChartResponse;
  createdAt: number;
  expiresAt?: number;
  persistent: boolean;
}

/**
 * In-memory chart spec store. Powers update_chart (linked-data refresh)
 * and get_chart_spec. Per-session by construction (one store per
 * server instance / MCP session).
 */
export class ChartStore {
  private store = new Map<string, StoredChart>();
  /** Default TTL for non-persistent specs (24h). */
  defaultTtlMs = 24 * 60 * 60 * 1000;

  newId(): string {
    return randomUUID();
  }

  put(
    id: string,
    spec: ChartInput,
    designSystemId: string,
    response: ChartResponse,
    opts: { persistent?: boolean; ttlMs?: number } = {},
  ): void {
    this.gc();
    const persistent = opts.persistent ?? false;
    const ttl = opts.ttlMs ?? this.defaultTtlMs;
    this.store.set(id, {
      spec,
      designSystemId,
      response,
      createdAt: Date.now(),
      expiresAt: persistent ? undefined : Date.now() + ttl,
      persistent,
    });
  }

  get(id: string): StoredChart | undefined {
    this.gc();
    return this.store.get(id);
  }

  delete(id: string): boolean {
    return this.store.delete(id);
  }

  size(): number {
    return this.store.size;
  }

  private gc(): void {
    const now = Date.now();
    for (const [id, s] of this.store) {
      if (s.expiresAt != null && s.expiresAt < now) this.store.delete(id);
    }
  }
}
