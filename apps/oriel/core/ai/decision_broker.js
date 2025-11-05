/**
 * decision_broker.ts
 * Receives signals from AIDaemon and converts them into actions
 * for the NarrativeCore or system subsystems.
 */
import { eventBus } from "../../src/core/event_bus";
import { narrativeCore } from "./narrative_core";
export class DecisionBroker {
    evaluate(data) {
        // Minimal placeholder heuristic
        if (data.delta && data.delta > 40) {
            return { type: "lag_spike", payload: { delta: data.delta } };
        }
        return null;
    }
    dispatch(insight) {
        switch (insight.type) {
            case "lag_spike":
                console.log("⚠ AI Daemon detected lag spike:", insight.payload.delta);
                narrativeCore.generate("system anomaly detected");
                break;
            case "heartbeat_variation":
                narrativeCore.generate("resonance fluctuation");
                break;
            default:
                eventBus.emit("ai.insight", insight);
                break;
        }
    }
}
