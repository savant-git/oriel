/**
 * narrative_core.ts
 * Handles narrative generation and contextual responses
 * to insights or simulation events.
 */

import fs from "fs";
import path from "path";
import { eventBus } from "../../src/core/event_bus";

export class NarrativeCore {
  private static instance: NarrativeCore;
  private logFile = "./logs/narrative_log.txt";

  static getInstance(): NarrativeCore {
    if (!NarrativeCore.instance)
      NarrativeCore.instance = new NarrativeCore();
    return NarrativeCore.instance;
  }

  generate(prompt: string): void {
    // Placeholder: in production this could call GPT-5 via internal API
    const text = `[${new Date().toISOString()}] ${prompt}`;
    fs.mkdirSync(path.dirname(this.logFile), { recursive: true });
    fs.appendFileSync(this.logFile, text + "\n");
    console.log("🜹 Narrative Core →", prompt);
    eventBus.emit("narrative.entry", { text });
  }

  summarize(): string {
    if (!fs.existsSync(this.logFile)) return "";
    const lines = fs.readFileSync(this.logFile, "utf-8").trim().split("\n");
    return lines.slice(-5).join("\n");
  }
}

export const narrativeCore = NarrativeCore.getInstance();
