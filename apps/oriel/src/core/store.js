/**
 * store.ts
 * Global reactive state for Oriel.
 */
export const store = (() => {
    let state = {
        running: false,
        payloads: {},
        rootShards: {},
        initialize(payloads) {
            state.payloads = payloads;
            console.log("🜹 Store initialized with payloads:", Object.keys(payloads));
        },
        setRunning(v) {
            state.running = v;
            console.log(`🜹 Simulation ${v ? "running" : "paused"}`);
        }
    };
    return {
        getState: () => state,
        setState: (partial) => Object.assign(state, partial)
    };
})();
