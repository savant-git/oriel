/**
 * pane.ts
 * Base class for all console panes.
 */
import { eventBus } from "../src/core/event_bus";
export class Pane {
    constructor(cfg) {
        this.id = cfg.id;
        this.label = cfg.label;
        this.active = cfg.active ?? true;
    }
    attach(event) {
        eventBus.on(event, data => {
            if (this.active)
                this.render(data);
        });
    }
}
