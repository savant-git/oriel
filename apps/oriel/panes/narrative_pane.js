/**
 * narrative_pane.ts
 * Streams narrative events as they happen.
 */
import { Pane } from "./pane";
export class NarrativePane extends Pane {
    constructor() {
        super({ id: "narrative", label: "NarrativePane" });
        this.attach("narrative.entry");
    }
    render(data) {
        if (!data || !data.text)
            return;
        console.log(`\n🜹 Narrative → ${data.text}`);
    }
}
