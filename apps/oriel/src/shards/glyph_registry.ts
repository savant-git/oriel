/**
 * glyph_registry.ts
 * One-time archetype table for every unique glyph.
 */

export interface GlyphArchetype {
  id: string;
  char: string;
  meta: {
    created: string;
    codepoint: number;
    category: string;
  };
}

export class GlyphRegistry {
  private static instance: GlyphRegistry;
  private archetypes = new Map<string, GlyphArchetype>();

  private constructor() {}

  static getInstance(): GlyphRegistry {
    if (!GlyphRegistry.instance)
      GlyphRegistry.instance = new GlyphRegistry();
    return GlyphRegistry.instance;
  }

  register(char: string): GlyphArchetype {
    const key = `G_${char === " " ? "SPACE" : char}`;
    if (!this.archetypes.has(key)) {
      const archetype: GlyphArchetype = {
        id: key,
        char,
        meta: {
          created: new Date().toISOString(),
          codepoint: char.codePointAt(0) || 0,
          category: this.categorize(char)
        }
      };
      this.archetypes.set(key, archetype);
    }
    return this.archetypes.get(key)!;
  }

  get(char: string): GlyphArchetype | undefined {
    const key = `G_${char === " " ? "SPACE" : char}`;
    return this.archetypes.get(key);
  }

  size(): number {
    return this.archetypes.size;
  }

  private categorize(c: string): string {
    if (/\s/.test(c)) return "space";
    if (/[a-zA-Z]/.test(c)) return "letter";
    if (/[0-9]/.test(c)) return "digit";
    if (/[.,;:!?'"-]/.test(c)) return "punctuation";
    return "symbol";
  }
}
