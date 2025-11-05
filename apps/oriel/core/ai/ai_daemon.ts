/**
 * ai_daemon.ts
 * Background cognitive agent that observes the simulation loop,
 * interprets states, and requests narrative or system responses.
 */

import { eventBus } from "../../src/core/event_bus";
import { DecisionBroker } from "./decision_broker";

export class AIDaemon {
  private static instance: AIDaemon;
  private active = false;
  private broker: DecisionBroker;

  private constructor() {
    this.broker = new DecisionBroker();
  }

  static getInstance(): AIDaemon {
    if (!AIDaemon.instance) AIDaemon.instance = new AIDaemon();
    return AIDaemon.instance;
  }

  start(): void {
    if (this.active) return;
    this.active = true;
    console.log("🜹 AI Daemon online — listening for events");
    eventBus.on("simulation.tick", e => this.onTick(e));
    eventBus.on("reso.tick", e => this.onReso(e));
  }

  stop(): void {
    this.active = false;
    console.log("🜹 AI Daemon offline");
  }

  private onTick(data: any): void {
    if (!this.active) return;
    const insight = this.broker.evaluate(data);
    if (insight) this.broker.dispatch(insight);
  }

  private onReso(data: any): void {
    if (!this.active) return;
    // sample: monitor rhythm stability
    if (Math.random() < 0.005) {
      this.broker.dispatch({
        type: "heartbeat_variation",
        payload: { delta: data.delta }
      });
    }
  }
}

export const aiDaemon = AIDaemon.getInstance();
