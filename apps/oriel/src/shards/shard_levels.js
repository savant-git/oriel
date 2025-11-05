/**
 * shard_levels.ts
 * Enumerates every fractal layer from glyph (00) to savant (7).
 */
export var ShardLevel;
(function (ShardLevel) {
    ShardLevel[ShardLevel["GLYPH"] = 0] = "GLYPH";
    ShardLevel[ShardLevel["WORD"] = 1] = "WORD";
    ShardLevel[ShardLevel["PHRASE"] = 2] = "PHRASE";
    ShardLevel[ShardLevel["PARAGRAPH"] = 3] = "PARAGRAPH";
    ShardLevel[ShardLevel["PANE"] = 4] = "PANE";
    ShardLevel[ShardLevel["TRUSS"] = 5] = "TRUSS";
    ShardLevel[ShardLevel["ORIEL"] = 6] = "ORIEL";
    ShardLevel[ShardLevel["SAVANT"] = 7] = "SAVANT";
})(ShardLevel || (ShardLevel = {}));
