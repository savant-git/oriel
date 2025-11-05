/**
 * sensory_manager.ts
 * Registers panes and updates them automatically.
 */

import { Pane } from "./pane";

export class SensoryManager {
  private static instance: SensoryManager;
  private panes = new Map<string, Pane>();

  static getInstance(): SensoryManager {
    if (!SensoryManager.instance)
      SensoryManager.instance = new SensoryManager();
    return SensoryManager.instance;
  }

  register(pane: Pane): void {
    this.panes.set(pane.id, pane);
  }

  all(): Pane[] {
    return Array.from(this.panes.values());
  }
}

export const sensoryManager = SensoryManager.getInstance();
