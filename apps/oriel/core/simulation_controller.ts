/**
 * simulation_controller.ts
 * Runs Oriel’s live simulation loop.
 */

import { store } from "../src/core/store";
import { eventBus } from "../src/core/event_bus";
import { trussManager } from "../trusses";

export class SimulationController {
  private static instance: SimulationController;
  private lastTick = Date.now();
  private running = false;

  private constructor() {}

  static getInstance(): SimulationController {
    if (!SimulationController.instance)
      SimulationController.instance = new SimulationController();
    return SimulationController.instance;
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    store.getState().setRunning(true);
    this.lastTick = Date.now();
    console.log("🜹 Simulation started");
    this.loop();
  }

  stop(): void {
    this.running = false;
    store.getState().setRunning(false);
    console.log("🜹 Simulation stopped");
  }

  private loop(): void {
    if (!this.running) return;
    const now = Date.now();
    const delta = now - this.lastTick;
    this.lastTick = now;

    // update every active truss
    trussManager.tickAll(delta);
    eventBus.emit("simulation.tick", { delta, now });

    setTimeout(() => this.loop(), 33); // ~30 FPS
  }

  step(delta = 16): void {
    trussManager.tickAll(delta);
    eventBus.emit("simulation.step", { delta });
  }
}

export const simulationController = SimulationController.getInstance();
