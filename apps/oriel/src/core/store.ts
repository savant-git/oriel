/**
 * store.ts
 * Global reactive state for Oriel.
 */

import type { Shard } from "../shards/shard";

type OrielState = {
  running: boolean;
  payloads: Record<string, any>;
  rootShards: Record<string, Shard>;
  initialize: (payloads: Record<string, any>) => void;
  setRunning: (v: boolean) => void;
};

export const store = (() => {
  let state: OrielState = {
    running: false,
    payloads: {},
    rootShards: {},
    initialize(payloads) {
      state.payloads = payloads;
      console.log("🜹 Store initialized with payloads:", Object.keys(payloads));
    },
    setRunning(v) {
      state.running = v;
      console.log(`🜹 Simulation ${v ? "running" : "paused"}`);
    }
  };
  return {
    getState: () => state,
    setState: (partial: Partial<OrielState>) => Object.assign(state, partial)
  };
})();
