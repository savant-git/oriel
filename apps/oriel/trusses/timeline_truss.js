/**
 * timeline_truss.ts
 * Maintains shard order in time and updates them per tick.
 */
import { BaseTruss } from "./truss";
export class TimelineTruss extends BaseTruss {
    constructor() {
        super(...arguments);
        this.timeline = [];
        this.currentTime = 0;
    }
    tick(delta) {
        this.currentTime += delta;
        for (const node of this.timeline) {
            if (node.timestamp <= this.currentTime) {
                // future: trigger shard activation logic here
            }
        }
    }
    addShard(shard, timestamp = 0) {
        super.addShard(shard);
        this.timeline.push({ shard, timestamp });
        this.timeline.sort((a, b) => a.timestamp - b.timestamp);
    }
}
