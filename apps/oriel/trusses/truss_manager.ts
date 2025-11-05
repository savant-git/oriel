/**
 * truss_manager.ts
 * Handles creation, lookup, and ticking of Trusses.
 */

import { BaseTruss } from "./truss";

export class TrussManager {
  private trusses = new Map<string, BaseTruss>();

  register(truss: BaseTruss): void {
    this.trusses.set(truss.id, truss);
  }

  get(id: string): BaseTruss | undefined {
    return this.trusses.get(id);
  }

  all(): BaseTruss[] {
    return Array.from(this.trusses.values());
  }

  tickAll(delta: number): void {
    for (const truss of this.trusses.values()) {
      if (truss.active) truss.tick(delta);
    }
  }
}

export const trussManager = new TrussManager();
