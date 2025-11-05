/**
 * status_pane.ts
 * Displays simulation timing and shard stats.
 */

import { Pane } from "./pane";
import { store } from "../src/core/store";

export class StatusPane extends Pane {
  private last = 0;

  render(): void {
    const now = Date.now();
    if (now - this.last < 1000) return; // throttle 1 Hz
    this.last = now;

    const s = store.getState();
    const run = s.running ? "RUNNING" : "PAUSED";
    const payloads = Object.keys(s.payloads).length;
    const shards = Object.keys(s.rootShards).length;

    process.stdout.write(
      `\r🜹 Status → ${run.padEnd(8)} | Payloads: ${payloads
        .toString()
        .padStart(3)} | Root shards: ${shards.toString().padStart(3)} `
    );
  }
}
