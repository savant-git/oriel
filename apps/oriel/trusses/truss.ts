/**
 * truss.ts
 * Defines the Truss interface and base class.
 * A Truss organizes and manages groups of shards.
 */

import type { Shard } from "../src/shards/shard";

export interface TrussConfig {
  id: string;
  label: string;
  description?: string;
  strength?: number; // weight or importance in the simulation
}

export interface Truss {
  id: string;
  label: string;
  active: boolean;
  shards: Map<string, Shard>;
  strength: number;
  tick(delta: number): void;
  addShard(shard: Shard): void;
  removeShard(id: string): void;
  getShard(id: string): Shard | undefined;
}

export abstract class BaseTruss implements Truss {
  id: string;
  label: string;
  active = true;
  shards = new Map<string, Shard>();
  strength: number;

  constructor(cfg: TrussConfig) {
    this.id = cfg.id;
    this.label = cfg.label;
    this.strength = cfg.strength ?? 1;
  }

  abstract tick(delta: number): void;

  addShard(shard: Shard): void {
    this.shards.set(shard.id, shard);
  }

  removeShard(id: string): void {
    this.shards.delete(id);
  }

  getShard(id: string): Shard | undefined {
    return this.shards.get(id);
  }
}
