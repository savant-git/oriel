/**
 * cognitive_stack.ts
 * Real-time working memory and reasoning context for the AI Daemon.
 * Sits between DecisionBroker and NarrativeCore.
 */

import { memoryLattice } from "./memory_lattice";

interface Thought {
  id: string;
  content: string;
  weight: number;
  timestamp: number;
}

export class CognitiveStack {
  private static instance: CognitiveStack;
  private stack: Thought[] = [];

  static getInstance(): CognitiveStack {
    if (!CognitiveStack.instance)
      CognitiveStack.instance = new CognitiveStack();
    return CognitiveStack.instance;
  }

  push(content: string, weight = 1): Thought {
    const thought: Thought = {
      id: `T_${Date.now().toString(36)}`,
      content,
      weight,
      timestamp: Date.now()
    };
    this.stack.unshift(thought);
    if (this.stack.length > 50) this.stack.pop();
    memoryLattice.store(content, ["thought"]);
    return thought;
  }

  pop(): Thought | undefined {
    return this.stack.shift();
  }

  peek(): Thought | undefined {
    return this.stack[0];
  }

  contextSummary(depth = 5): string {
    return this.stack
      .slice(0, depth)
      .map(t => `• ${t.content}`)
      .join("\n");
  }
}

export const cognitiveStack = CognitiveStack.getInstance();
