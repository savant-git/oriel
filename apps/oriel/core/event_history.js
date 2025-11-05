/**
 * event_history.ts
 * Keeps a log of simulation ticks and key events.
 */
import fs from "fs";
import path from "path";
import { eventBus } from "../src/core/event_bus";
export class EventHistory {
    constructor() {
        this.log = [];
    }
    static getInstance() {
        if (!EventHistory.instance)
            EventHistory.instance = new EventHistory();
        return EventHistory.instance;
    }
    attach() {
        eventBus.on("simulation.tick", e => this.record("tick", e));
        eventBus.on("simulation.step", e => this.record("step", e));
        eventBus.on("reso.tick", e => this.record("reso", e));
        console.log("🜹 EventHistory listening");
    }
    record(type, payload) {
        this.log.push({ type, timestamp: Date.now(), payload });
        if (this.log.length > 10000)
            this.log.shift();
    }
    save(file = "./logs/simulation_history.json") {
        fs.mkdirSync(path.dirname(file), { recursive: true });
        fs.writeFileSync(file, JSON.stringify(this.log, null, 2));
        console.log(`🜹 Event history saved → ${file}`);
    }
}
export const eventHistory = EventHistory.getInstance();
