/**
 * resonance_truss.ts
 * Calculates emotional "resonance" across shards.
 */
import { BaseTruss } from "./truss";
export class ResonanceTruss extends BaseTruss {
    constructor() {
        super(...arguments);
        this.resonanceValue = 0;
    }
    tick(delta) {
        this.resonanceValue += Math.sin(delta / 1000);
    }
    computeFromShards() {
        let total = 0;
        for (const shard of this.shards.values()) {
            const weight = (shard.meta.position ?? 1) * this.strength;
            total += weight;
        }
        this.resonanceValue = total / (this.shards.size || 1);
    }
}
