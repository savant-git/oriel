/**
 * physics_truss.ts
 * Applies cause–effect and spatial relationships among shards.
 */
import { BaseTruss } from "./truss";
export class PhysicsTruss extends BaseTruss {
    tick(delta) {
        for (const shard of this.shards.values()) {
            shard.meta.updated = new Date().toISOString();
        }
    }
    linkCauseEffect(cause, effect) {
        if (!cause.fibers)
            cause.fibers = [];
        cause.fibers.push(effect.id);
    }
}
