/**
 * shard.ts
 * Universal node schema; supports archetype references.
 */

import { ShardLevel } from "./shard_levels";

export type ShardType =
  | "CanonShard" | "LoreShard" | "CodeShard"
  | "VisualShard" | "MetaShard" | "ResoShard"
  | "AIShard" | "WordShard" | "GlyphShard";

export interface Shard {
  id: string;
  type: ShardType;
  level: ShardLevel;
  data: string | Record<string, any>;
  instanceOf?: string;        // archetype reference if applicable
  children?: Shard[];
  fibers?: string[];
  meta: {
    created: string;
    updated: string;
    lineage: string[];
    position?: number;
    glyphIndex?: number;
    wordIndex?: number;
  };
}
