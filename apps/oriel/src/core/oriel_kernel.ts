/**
 * oriel_kernel.ts
 * Oriel’s root orchestrator.
 * Boot order:
 *   1. Load directives / payloads
 *   2. Enforce non-negotiable rules
 *   3. Initialize store and registries
 *   4. Broadcast kernel.ready
 */

import { loadContext } from "./context_loader";
import { enforceRules } from "./auth_guard";
import { eventBus } from "./event_bus";
import { store } from "./store";
import { ShardRegistry } from "../shards/shard_registry";
import { GlyphRegistry } from "../shards/glyph_registry";

export class OrielKernel {
  static instance: OrielKernel | null = null;
  private initialized = false;
  private shardRegistry = new ShardRegistry();
  private glyphRegistry = GlyphRegistry.getInstance();

  constructor() {
    if (OrielKernel.instance) return OrielKernel.instance;
    OrielKernel.instance = this;
  }

  async boot(): Promise<void> {
    if (this.initialized) return;
    console.log("🜹 Oriel Kernel :: boot initiated");

    const ctx = await loadContext();
    enforceRules(ctx.directives);

    store.getState().initialize(ctx.payloads);
    this.shardRegistry.registerBuiltinTypes();

    eventBus.emit("kernel.ready", {
      timestamp: Date.now(),
      levels: this.shardRegistry.levelMap(),
      glyphCount: this.glyphRegistry.size()
    });

    this.initialized = true;
    console.log("🜹 Oriel Kernel ready — levels 00→7 active");
  }

  shutdown(): void {
    eventBus.emit("kernel.shutdown");
    OrielKernel.instance = null;
  }
}
