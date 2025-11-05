/**
 * shard_factory.ts
 * Builds Canon→Word→Glyph hierarchy using archetype refs.
 */

import { Shard, ShardLevel } from "./shard";
import { GlyphRegistry } from "./glyph_registry";

const glyphRegistry = GlyphRegistry.getInstance();

export function buildTextShard(text: string, parentId: string): Shard {
  const words = text.split(/\s+/);
  const wordShards = words.map((word, wIndex) => {
    const chars = Array.from(word).map((ch, cIndex) => {
      const archetype = glyphRegistry.register(ch);
      return {
        id: `${parentId}_c${wIndex}_${cIndex}`,
        type: "GlyphShard",
        level: ShardLevel.GLYPH,
        data: { ref: archetype.id },
        instanceOf: archetype.id,
        meta: {
          created: new Date().toISOString(),
          updated: new Date().toISOString(),
          lineage: [parentId],
          position: cIndex,
          glyphIndex: cIndex
        }
      };
    });
    return {
      id: `${parentId}_w${wIndex}`,
      type: "WordShard",
      level: ShardLevel.WORD,
      data: word,
      children: chars,
      meta: {
        created: new Date().toISOString(),
        updated: new Date().toISOString(),
        lineage: [parentId],
        position: wIndex,
        wordIndex: wIndex
      }
    };
  });

  return {
    id: parentId,
    type: "CanonShard",
    level: ShardLevel.PARAGRAPH,
    data: text,
    children: wordShards,
    meta: {
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      lineage: []
    }
  };
}
