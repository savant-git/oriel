/**
 * shard_levels.ts
 * Enumerates every fractal layer from glyph (00) to savant (7).
 */

export enum ShardLevel {
  GLYPH = 0,       // character
  WORD = 1,        // word/token
  PHRASE = 2,      // sentence
  PARAGRAPH = 3,   // canonical shard
  PANE = 4,
  TRUSS = 5,
  ORIEL = 6,
  SAVANT = 7
}
