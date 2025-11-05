/**
 * event_bus.ts
 * Central pub/sub bus with cascade for shard depth.
 */

type Listener = (data?: any) => void;

class EventBus {
  private listeners = new Map<string, Set<Listener>>();

  on(event: string, fn: Listener): void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event)!.add(fn);
  }

  off(event: string, fn: Listener): void {
    this.listeners.get(event)?.delete(fn);
  }

  emit(event: string, data?: any): void {
    const set = this.listeners.get(event);
    if (!set) return;
    for (const fn of set) fn(data);
  }

  cascade(event: string, shardId: string, data?: any): void {
    this.emit(`${event}:${shardId}`, data);
  }
}

export const eventBus = new EventBus();
