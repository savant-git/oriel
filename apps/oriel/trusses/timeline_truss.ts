/**
 * timeline_truss.ts
 * Maintains shard order in time and updates them per tick.
 */

import { BaseTruss } from "./truss";
import { Shard } from "../src/shards/shard";

interface TimeNode {
  shard: Shard;
  timestamp: number;
}

export class TimelineTruss extends BaseTruss {
  timeline: TimeNode[] = [];
  currentTime = 0;

  tick(delta: number): void {
    this.currentTime += delta;
    for (const node of this.timeline) {
      if (node.timestamp <= this.currentTime) {
        // future: trigger shard activation logic here
      }
    }
  }

  addShard(shard: Shard, timestamp = 0): void {
    super.addShard(shard);
    this.timeline.push({ shard, timestamp });
    this.timeline.sort((a, b) => a.timestamp - b.timestamp);
  }
}
