/**
 * memory_lattice.ts
 * Persistent associative memory store for the AI Daemon.
 * Forms a fractal graph of memories with weighted resonance links.
 */
import fs from "fs";
import path from "path";
export class MemoryLattice {
    constructor() {
        this.memories = new Map();
        this.file = "./logs/oriel_memory.json";
    }
    static getInstance() {
        if (!MemoryLattice.instance)
            MemoryLattice.instance = new MemoryLattice();
        return MemoryLattice.instance;
    }
    store(text, tags = []) {
        const id = `M_${Date.now().toString(36)}`;
        const node = {
            id,
            timestamp: Date.now(),
            data: text,
            weight: 1,
            tags,
            links: []
        };
        this.memories.set(id, node);
        this.save();
        return node;
    }
    link(a, b) {
        const A = this.memories.get(a);
        const B = this.memories.get(b);
        if (A && B && !A.links.includes(b)) {
            A.links.push(b);
            B.links.push(a);
            this.save();
        }
    }
    recallByTag(tag) {
        return Array.from(this.memories.values()).filter(m => m.tags.includes(tag));
    }
    summarize(count = 5) {
        const list = Array.from(this.memories.values())
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, count)
            .map(m => m.data);
        return list.join("\n");
    }
    save() {
        fs.mkdirSync(path.dirname(this.file), { recursive: true });
        fs.writeFileSync(this.file, JSON.stringify([...this.memories.values()], null, 2));
    }
}
export const memoryLattice = MemoryLattice.getInstance();
