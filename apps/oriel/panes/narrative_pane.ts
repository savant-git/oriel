/**
 * narrative_pane.ts
 * Streams narrative events as they happen.
 */

import { Pane } from "./pane";
import { eventBus } from "../src/core/event_bus";

export class NarrativePane extends Pane {
  constructor() {
    super({ id: "narrative", label: "NarrativePane" });
    this.attach("narrative.entry");
  }

  render(data?: any): void {
    if (!data || !data.text) return;
    console.log(`\n🜹 Narrative → ${data.text}`);
  }
}
