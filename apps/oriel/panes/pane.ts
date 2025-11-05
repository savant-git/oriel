/**
 * pane.ts
 * Base class for all console panes.
 */

import { eventBus } from "../src/core/event_bus";

export interface PaneConfig {
  id: string;
  label: string;
  active?: boolean;
}

export abstract class Pane {
  id: string;
  label: string;
  active: boolean;

  constructor(cfg: PaneConfig) {
    this.id = cfg.id;
    this.label = cfg.label;
    this.active = cfg.active ?? true;
  }

  abstract render(data?: any): void;

  attach(event: string): void {
    eventBus.on(event, data => {
      if (this.active) this.render(data);
    });
  }
}
