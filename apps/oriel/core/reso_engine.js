/**
 * reso_engine.ts
 * Generates global time pulses (“resonance ticks”).
 */
import { eventBus } from "../src/core/event_bus";
export class ResoEngine {
    constructor() {
        this.rate = 1000 / 30; // default 30 Hz
    }
    static getInstance() {
        if (!ResoEngine.instance)
            ResoEngine.instance = new ResoEngine();
        return ResoEngine.instance;
    }
    start() {
        if (this.interval)
            return;
        let last = Date.now();
        this.interval = setInterval(() => {
            const now = Date.now();
            const delta = now - last;
            last = now;
            eventBus.emit("reso.tick", { now, delta });
        }, this.rate);
        console.log(`🜹 ResoEngine started @${(1000 / this.rate).toFixed(1)} Hz`);
    }
    stop() {
        if (!this.interval)
            return;
        clearInterval(this.interval);
        this.interval = undefined;
        console.log("🜹 ResoEngine stopped");
    }
    setRate(hz) {
        this.rate = 1000 / hz;
        if (this.interval) {
            this.stop();
            this.start();
        }
    }
}
export const resoEngine = ResoEngine.getInstance();
