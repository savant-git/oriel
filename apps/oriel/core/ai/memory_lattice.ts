/**
 * memory_lattice.ts
 * Persistent associative memory store for the AI Daemon.
 * Forms a fractal graph of memories with weighted resonance links.
 */

import fs from "fs";
import path from "path";

export interface MemoryNode {
  id: string;
  timestamp: number;
  data: string;
  weight: number;
  tags: string[];
  links: string[];
}

export class MemoryLattice {
  private static instance: MemoryLattice;
  private memories = new Map<string, MemoryNode>();
  private file = "./logs/oriel_memory.json";

  static getInstance(): MemoryLattice {
    if (!MemoryLattice.instance)
      MemoryLattice.instance = new MemoryLattice();
    return MemoryLattice.instance;
  }

  store(text: string, tags: string[] = []): MemoryNode {
    const id = `M_${Date.now().toString(36)}`;
    const node: MemoryNode = {
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

  link(a: string, b: string): void {
    const A = this.memories.get(a);
    const B = this.memories.get(b);
    if (A && B && !A.links.includes(b)) {
      A.links.push(b);
      B.links.push(a);
      this.save();
    }
  }

  recallByTag(tag: string): MemoryNode[] {
    return Array.from(this.memories.values()).filter(m => m.tags.includes(tag));
  }

  summarize(count = 5): string {
    const list = Array.from(this.memories.values())
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, count)
      .map(m => m.data);
    return list.join("\n");
  }

  private save(): void {
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    fs.writeFileSync(this.file, JSON.stringify([...this.memories.values()], null, 2));
  }
}

export const memoryLattice = MemoryLattice.getInstance();
