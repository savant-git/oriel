/**
 * dialogue_gateway.ts
 * Provides I/O channel between Oriel's AI and the outer system (console/UI).
 * All AI text output and inbound commands pass through here.
 */

import readline from "readline";
import { eventBus } from "../../src/core/event_bus";
import { narrativeCore } from "./narrative_core";
import { cognitiveStack } from "./cognitive_stack";

export class DialogueGateway {
  private static instance: DialogueGateway;
  private rl?: readline.Interface;
  private active = false;

  static getInstance(): DialogueGateway {
    if (!DialogueGateway.instance)
      DialogueGateway.instance = new DialogueGateway();
    return DialogueGateway.instance;
  }

  open(): void {
    if (this.active) return;
    this.active = true;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    console.log("🜹 Dialogue Gateway online — type messages to interact with Oriel");

    this.rl.on("line", line => {
      if (line.trim().toLowerCase() === "exit") {
        this.close();
        return;
      }
      cognitiveStack.push(`User: ${line}`, 2);
      narrativeCore.generate(`User said: ${line}`);
      eventBus.emit("dialogue.input", { text: line });
    });
  }

  speak(text: string): void {
    console.log(`Oriel: ${text}`);
  }

  close(): void {
    if (!this.rl) return;
    this.rl.close();
    this.active = false;
    console.log("🜹 Dialogue Gateway closed");
  }
}

export const dialogueGateway = DialogueGateway.getInstance();
