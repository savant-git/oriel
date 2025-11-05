/**
 * resonance_truss.ts
 * Calculates emotional "resonance" across shards.
 */

import { BaseTruss } from "./truss";
import { Shard } from "../src/shards/shard";

export class ResonanceTruss extends BaseTruss {
  resonanceValue = 0;

  tick(delta: number): void {
    this.resonanceValue += Math.sin(delta / 1000);
  }

  computeFromShards(): void {
    let total = 0;
    for (const shard of this.shards.values()) {
      const weight = (shard.meta.position ?? 1) * this.strength;
      total += weight;
    }
    this.resonanceValue = total / (this.shards.size || 1);
  }
}
