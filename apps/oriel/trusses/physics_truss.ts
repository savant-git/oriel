/**
 * physics_truss.ts
 * Applies cause–effect and spatial relationships among shards.
 */

import { BaseTruss } from "./truss";
import { Shard } from "../src/shards/shard";

export class PhysicsTruss extends BaseTruss {
  tick(delta: number): void {
    for (const shard of this.shards.values()) {
      shard.meta.updated = new Date().toISOString();
    }
  }

  linkCauseEffect(cause: Shard, effect: Shard): void {
    if (!cause.fibers) cause.fibers = [];
    cause.fibers.push(effect.id);
  }
}
