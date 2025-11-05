/**
 * console_dashboard_pane.ts
 * Unified terminal dashboard combining Status + Narrative updates.
 */
import { Pane } from "./pane";
import { store } from "../src/core/store";
export class ConsoleDashboardPane extends Pane {
    constructor() {
        super({ id: "dashboard", label: "ConsoleDashboard" });
        this.attach("simulation.tick");
        this.attach("narrative.entry");
    }
    render(data) {
        const s = store.getState();
        const run = s.running ? "RUNNING" : "PAUSED";
        const msg = typeof data?.text === "string"
            ? data.text
            : data
                ? JSON.stringify(data)
                : "";
        process.stdout.write(`\r🜹 ${run.padEnd(8)} | Payloads:${Object.keys(s.payloads).length
            .toString()
            .padStart(3)} | ${msg.slice(0, 60)} `);
    }
}
