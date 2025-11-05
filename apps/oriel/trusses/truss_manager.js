/**
 * truss_manager.ts
 * Handles creation, lookup, and ticking of Trusses.
 */
export class TrussManager {
    constructor() {
        this.trusses = new Map();
    }
    register(truss) {
        this.trusses.set(truss.id, truss);
    }
    get(id) {
        return this.trusses.get(id);
    }
    all() {
        return Array.from(this.trusses.values());
    }
    tickAll(delta) {
        for (const truss of this.trusses.values()) {
            if (truss.active)
                truss.tick(delta);
        }
    }
}
export const trussManager = new TrussManager();
