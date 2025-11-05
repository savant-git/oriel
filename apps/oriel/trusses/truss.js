/**
 * truss.ts
 * Defines the Truss interface and base class.
 * A Truss organizes and manages groups of shards.
 */
export class BaseTruss {
    constructor(cfg) {
        this.active = true;
        this.shards = new Map();
        this.id = cfg.id;
        this.label = cfg.label;
        this.strength = cfg.strength ?? 1;
    }
    addShard(shard) {
        this.shards.set(shard.id, shard);
    }
    removeShard(id) {
        this.shards.delete(id);
    }
    getShard(id) {
        return this.shards.get(id);
    }
}
