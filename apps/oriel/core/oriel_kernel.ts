/**
 * oriel_kernel.ts
 * Phase 9 — Interactive UI + Visualization Control
 * Connects the Oriel engine, AI Daemon, Sensory layer, and Electron dashboard.
 */

import { simulationController } from "./simulation_controller";
import { resoEngine } from "./reso_engine";
import { eventHistory } from "./event_history";
import { trussManager } from "../trusses";
import { TimelineTruss } from "../trusses/timeline_truss";
import { ResonanceTruss } from "../trusses/resonance_truss";
import { PhysicsTruss } from "../trusses/physics_truss";
import {
  aiDaemon,
  dialogueGateway,
  cognitiveStack,
  memoryLattice,
} from "./ai";
import { sensoryManager } from "../panes/sensory_manager";
import { StatusPane } from "../panes/status_pane";
import { NarrativePane } from "../panes/narrative_pane";
import { ConsoleDashboardPane } from "../panes/console_dashboard_pane";

/**
 * The OrielKernel class orchestrates all subsystems.
 */
export class OrielKernel {
  private initialized = false;

  async boot(): Promise<void> {
    if (this.initialized) return;
    console.log("🜹 Oriel Kernel :: boot initiated (Phase 9)");

    // 1️⃣ Register base trusses
    const timeline = new TimelineTruss({ id: "timeline", label: "Timeline" });
    const resonance = new ResonanceTruss({ id: "resonance", label: "Resonance" });
    const physics = new PhysicsTruss({ id: "physics", label: "Physics" });
    trussManager.register(timeline);
    trussManager.register(resonance);
    trussManager.register(physics);
    console.log(
      "🜹 Trusses registered:",
      trussManager.all().map((t) => t.label).join(", ")
    );

    // 2️⃣ Start simulation subsystems
    eventHistory.attach();
    resoEngine.start();
    simulationController.start();

    // 3️⃣ Start AI layer
    aiDaemon.start();
    dialogueGateway.open();
    cognitiveStack.push("System boot complete", 3);
    memoryLattice.store("Oriel engine fully online", ["system"]);

    // 4️⃣ Initialize sensory layer (console panes)
    const statusPane = new StatusPane({ id: "status", label: "Status" });
    const narrativePane = new NarrativePane();
    const consolePane = new ConsoleDashboardPane();
    sensoryManager.register(statusPane);
    sensoryManager.register(narrativePane);
    sensoryManager.register(consolePane);

    console.log("🜹 Sensory Layer online – console panes active");

    this.initialized = true;
    console.log("🜹 Oriel Engine + AI + Visualization Control active");

    // 5️⃣ Listen for external (Electron) control commands via stdin
    this.setupCommandListener();
  }

  /**
   * Responds to JSON commands received via stdin.
   * Enables the Electron dashboard to control simulation state.
   */
  private setupCommandListener(): void {
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (buf) => {
      const raw = buf.toString().trim();
      if (!raw) return;

      try {
        const msg = JSON.parse(raw);
        if (!msg.cmd) return;

        switch (msg.cmd) {
          case "pause":
            simulationController.stop();
            console.log("🜹 Simulation paused by UI command");
            break;

          case "resume":
            simulationController.start();
            console.log("🜹 Simulation resumed by UI command");
            break;

          case "rate":
            if (typeof msg.arg === "number" && msg.arg > 0) {
              resoEngine.setRate(msg.arg);
              console.log(`🜹 Resonance rate set to ${msg.arg.toFixed(1)} Hz`);
            }
            break;

          default:
            console.log("⚠️ Unknown command:", msg);
            break;
        }
      } catch (err) {
        console.error("⚠️ Invalid command input:", err);
      }
    });
  }

  /** Graceful shutdown */
  shutdown(): void {
    simulationController.stop();
    resoEngine.stop();
    aiDaemon.stop();
    dialogueGateway.close();
    eventHistory.save();
    console.log("🜹 Oriel Kernel shutdown complete");
  }
}

/** --- CLI runner (stand-alone mode) --- */
if (require.main === module) {
  (async () => {
    const kernel = new OrielKernel();
    await kernel.boot();

    // Graceful termination
    process.on("SIGINT", () => {
      kernel.shutdown();
      process.exit(0);
    });
  })();
}
