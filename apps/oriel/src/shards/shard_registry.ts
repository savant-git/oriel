/**
 * shard_registry.ts
 * Tracks shard types and their corresponding numeric levels.
 */

import { ShardLevel } from "./shard_levels";

export class ShardRegistry {
  private types = new Map<string, number>();

  registerBuiltinTypes(): void {
    Object.entries(ShardLevel).forEach(([k, v]) => {
      if (typeof v === "number") this.types.set(k, v);
    });
  }

  levelMap(): Record<string, number> {
    return Object.fromEntries(this.types);
  }

  getLevel(name: string): number | undefined {
    return this.types.get(name);
  }
}
