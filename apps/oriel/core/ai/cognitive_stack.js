/**
 * cognitive_stack.ts
 * Real-time working memory and reasoning context for the AI Daemon.
 * Sits between DecisionBroker and NarrativeCore.
 */
import { memoryLattice } from "./memory_lattice";
export class CognitiveStack {
    constructor() {
        this.stack = [];
    }
    static getInstance() {
        if (!CognitiveStack.instance)
            CognitiveStack.instance = new CognitiveStack();
        return CognitiveStack.instance;
    }
    push(content, weight = 1) {
        const thought = {
            id: `T_${Date.now().toString(36)}`,
            content,
            weight,
            timestamp: Date.now()
        };
        this.stack.unshift(thought);
        if (this.stack.length > 50)
            this.stack.pop();
        memoryLattice.store(content, ["thought"]);
        return thought;
    }
    pop() {
        return this.stack.shift();
    }
    peek() {
        return this.stack[0];
    }
    contextSummary(depth = 5) {
        return this.stack
            .slice(0, depth)
            .map(t => `• ${t.content}`)
            .join("\n");
    }
}
export const cognitiveStack = CognitiveStack.getInstance();
