/**
 * event_bus.ts
 * Central pub/sub bus with cascade for shard depth.
 */
class EventBus {
    constructor() {
        this.listeners = new Map();
    }
    on(event, fn) {
        if (!this.listeners.has(event))
            this.listeners.set(event, new Set());
        this.listeners.get(event).add(fn);
    }
    off(event, fn) {
        this.listeners.get(event)?.delete(fn);
    }
    emit(event, data) {
        const set = this.listeners.get(event);
        if (!set)
            return;
        for (const fn of set)
            fn(data);
    }
    cascade(event, shardId, data) {
        this.emit(`${event}:${shardId}`, data);
    }
}
export const eventBus = new EventBus();
