/**
 * sensory_manager.ts
 * Registers panes and updates them automatically.
 */
export class SensoryManager {
    constructor() {
        this.panes = new Map();
    }
    static getInstance() {
        if (!SensoryManager.instance)
            SensoryManager.instance = new SensoryManager();
        return SensoryManager.instance;
    }
    register(pane) {
        this.panes.set(pane.id, pane);
    }
    all() {
        return Array.from(this.panes.values());
    }
}
export const sensoryManager = SensoryManager.getInstance();
