/**
 * savant_kernel.ts
 * Root orchestrator for the Savant system.
 * Loads savant_manifest.json, enforces directives,
 * configures archive policy, and boots sub-apps (e.g., Oriel).
 */

import fs from "fs";
import path from "path";

// ---------- utility imports ----------
import { eventBus } from "./event_bus";
import { enforceRules } from "./directive_enforcer";
import { archiveManager } from "./archive_manager";

// ---------- manifest types ----------
interface AppRecord {
  path: string;
  entry: string;
  version: string;
  auto_load: boolean;
  description?: string;
}

interface SavantManifest {
  savant: { version: string; last_updated: string };
  apps: Record<string, AppRecord>;
  archive_policy: {
    pattern: string;
    destination: string;
    retain_versions: number;
  };
}

// ---------- main kernel ----------
export class SavantKernel {
  private static instance: SavantKernel | null = null;
  private manifest!: SavantManifest;
  private initialized = false;

  constructor() {
    if (SavantKernel.instance) return SavantKernel.instance;
    SavantKernel.instance = this;
  }

  // ----- boot sequence -----
  async boot(): Promise<void> {
    if (this.initialized) return;
    console.log("🜹 Savant Kernel :: boot initiated");

    this.loadManifest();
    enforceRules(this.manifest);
    archiveManager.configure(this.manifest.archive_policy);
    await this.bootApps();

    this.initialized = true;
    eventBus.emit("savant.ready", { timestamp: Date.now() });
    console.log("🜹 Savant Kernel ready");
  }

  // ----- manifest -----
  private loadManifest(): void {
    const manifestPath = path.resolve("savant_manifest.json");
    if (!fs.existsSync(manifestPath)) {
      throw new Error("Missing savant_manifest.json in project root.");
    }
    const data = fs.readFileSync(manifestPath, "utf-8");
    this.manifest = JSON.parse(data);
    console.log(
      `🜹 Manifest loaded :: version ${this.manifest.savant.version} (${Object.keys(
        this.manifest.apps
      ).length} apps)`
    );
  }

  // ----- app bootstrap -----
  private async bootApps(): Promise<void> {
    const apps = this.manifest.apps;
    for (const [name, app] of Object.entries(apps)) {
      if (!app.auto_load) continue;

      console.log(`↳ Booting ${name}@${app.version}`);
      const entryPath = path.resolve(app.entry);

      if (!fs.existsSync(entryPath)) {
        console.warn(`⚠ Missing entry for ${name}: ${entryPath}`);
        continue;
      }

      try {
        const mod = await import(entryPath);
        const kernelClass =
          mod.default ||
          mod[`${capitalize(name)}Kernel`] ||
          Object.values(mod)[0];

        if (!kernelClass) {
          console.warn(`⚠ No kernel class found in ${entryPath}`);
          continue;
        }

        const kernel = new (kernelClass as any)();
        if (typeof kernel.boot === "function") {
          await kernel.boot();
          console.log(`✔ ${name} booted successfully`);
        } else {
          console.warn(`⚠ ${name} has no boot() method`);
        }
      } catch (err) {
        console.error(`❌ Failed to boot ${name}:`, err);
      }
    }
  }

  // ----- shutdown -----
  shutdown(): void {
    eventBus.emit("savant.shutdown");
    SavantKernel.instance = null;
  }
}

// ---------- helper ----------
function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ---------- CLI entry ----------
if (require.main === module) {
  (async () => {
    try {
      const kernel = new SavantKernel();
      await kernel.boot();
    } catch (err) {
      console.error("❌ Fatal error during Savant boot:", err);
      process.exit(1);
    }
  })();
}
