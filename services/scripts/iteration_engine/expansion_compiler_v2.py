from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Savant Expansion Compiler v2.0 (Dynamic)
───────────────────────────────────────────────────────────────────────────────
Auto-sizes each iteration layer based on *actual demand*:
- Knowledge shard density per layer
- Backlog/deficit signals
- Optional per-layer overrides
- Hard caps & floors to prevent thrash

Idempotent: re-runs will only add what's missing.
Never deletes existing modules.
"""

from __future__ import annotations
import os, json, re, math, random, pathlib
from datetime import datetime, timezone
from typing import Dict, List

HOME = pathlib.Path.home()
ROOT = HOME / "savant"
IE   = ROOT / "services" / "scripts" / "iteration_engine"
LOG  = ROOT / "logs" / "expansion_compiler_v2_runtime.log"
IDX  = IE / "upgrade_index.json"
REG  = IE / "layer_registry.json"           # canonical registry (grows over time)
OVR  = IE / "dynamic_overrides.json"        # optional, user-tunable
SHARDS_BASE = ROOT / "knowledge" / "shards" # per-layer folders optional

def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n", append=LOG.exists())
    console.print(msg)

# Python < 3.11 compatibility shim for Path.write_text append
from pathlib import Path
def _write_text_patch(self, data, append=False, **kwargs):
    self.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with self.open(mode, encoding=kwargs.get("encoding","utf-8")) as f:
        f.write(data)
Path.write_text = _write_text_patch  # type: ignore

# --------------------------- Layer taxonomy (themes) --------------------------
LAYER_FOCUS: Dict[str, List[str]] = {
    "L1_Cognition": [
        "Prompt Refinement Engine","Persona Fusion","Contextual Memory",
        "Meta-Reasoning Kernel","Autonomous Task Chaining","Thought Stream Parser"
    ],
    "L2_Creativity": [
        "Visual Generator","Style Harmonizer","Color Theory Matrix",
        "Concept Composer","Voice Design Architect","Narrative Mapper"
    ],
    "L3_Interface": [
        "UX Mapper","Dashboard Renderer","Timeline Sync",
        "Interactive Grid","Live Asset Bridge","Gesture Control Adapter"
    ],
    "L4_Optimization": [
        "Latency Auditor","Cache Harmonizer","Efficiency Compiler",
        "Redundancy Pruner","Task Batcher","I/O Governor"
    ],
    "L5_Knowledge": [
        "Web Harvester","Semantic Indexer","Document Vectorizer",
        "Corpus Synthesizer","Fact Validator","Temporal Context Linker"
    ],
    "L6_Integration": [
        "GitHub Bridge","S3 Link","API Orchestrator",
        "Autosave Daemon","Notification Relay","Dependency Graph Updater"
    ],
    "L7_Reasoning": [
        "Error Repair Agent","Hypothesis Modeler","Causal Inference Core",
        "Experiment Tracker","Heuristic Mapper","Evaluation Network"
    ],
    "L8_VisualIntelligence": [
        "3D Asset Generator","Motion Designer","Camera Path Solver",
        "Lighting Architect","Scene Composer","Animation Sampler"
    ],
    "L9_Autonomy": [
        "Scheduler Daemon","Task Orchestrator","Distributed Node Link",
        "Policy Balancer","Priority Weighting Engine","Cyclic Intelligence Loop"
    ],
    "L10_SentienceFramework": [
        "Goal Evaluator","Meta-Learning Kernel","Ethics Guardrail",
        "Self-Audit Engine","Motivational Lattice","Reflective Awareness Node"
    ],
}

# --------------------------- Heuristics controls -----------------------------
FLOOR_PER_LAYER   = 6      # never fewer than this many modules
SOFT_TARGET_BASE  = 12     # base demand even with few shards
SHARD_TO_MODULE_K = 0.12   # each N shards => +modules
BACKLOG_WEIGHT    = 0.35   # backlog bumps
HARD_CAP_PER_LYR  = 220    # safety ceiling

def load_json(p: Path, fallback):
    try:
        return json.loads(p.read_text())
    except Exception:
        return fallback

def nameify(base: str, idx: int) -> str:
    base = re.sub(r'\W+', '', base.title().replace(" ", ""))
    return f"{base}_{idx}"

def shard_count_for(layer: str) -> int:
    p = SHARDS_BASE / layer
    if not p.exists():
        return 0
    c = 0
    for fp in p.rglob("*"):
        if fp.is_file() and fp.suffix.lower() in (".json",".md",".txt",".yaml",".yml",".py",".html",".css",".js"):
            c += 1
    return c

def backlog_for(layer: str) -> int:
    # If present, read a simple backlog file: one item per line.
    f = IE / "backlog" / f"{layer}.list"
    if not f.exists():
        return 0
    try:
        lines = [ln for ln in f.read_text().splitlines() if ln.strip()]
        return len(lines)
    except Exception:
        return 0

def desired_modules(layer: str, existing: int, overrides: dict) -> int:
    # Override wins first.
    if (ov := overrides.get(layer, {}).get("desired")):
        return max(FLOOR_PER_LAYER, min(HARD_CAP_PER_LYR, int(ov)))

    shards = shard_count_for(layer)
    back   = backlog_for(layer)

    # Nonlinear shard influence (diminishing returns) + soft base + backlog bump
    shard_term = int(math.ceil(math.log2(max(1, shards+1)) * (1/SHARD_TO_MODULE_K)))
    # So if shards=0 → log2(1)=0 → term 0; shards=31 → log2(32)=5 → amplifies
    # Clamp shard_term sensibly
    shard_term = max(0, min(180, shard_term))

    backlog_term = int(math.ceil(back * BACKLOG_WEIGHT))

    target = SOFT_TARGET_BASE + shard_term + backlog_term

    # Never below floor; never insane
    target = max(FLOOR_PER_LAYER, min(HARD_CAP_PER_LYR, target))

    # If we already exceed target, keep current (no deletions)
    target = max(target, existing)

    return target

def ensure_registry() -> list:
    REG.parent.mkdir(parents=True, exist_ok=True)
    if not REG.exists():
        # If no registry, lay down an empty list.
        REG.write_text("[]")
    return load_json(REG, [])

def write_registry(entries: list):
    REG.write_text(json.dumps(entries, indent=2))

def next_id(entries: list) -> int:
    if not entries:
        return 1
    return max(e["id"] for e in entries) + 1

def compile_layer(entries: list, layer: str, overrides: dict):
    # Count existing
    cur = [e for e in entries if e["layer"] == layer]
    existing = len(cur)
    desired  = desired_modules(layer, existing, overrides)
    add_n    = desired - existing

    log(f"📊 {layer}: shards={shard_count_for(layer)} backlog={backlog_for(layer)} existing={existing} ⇒ desired={desired}")

    if add_n <= 0:
        log(f"✅ {layer}: already satisfied ({existing})")
        return entries

    # Create the additional modules
    focus = LAYER_FOCUS.get(layer, ["Expansion Node"])
    for _ in range(add_n):
        nid   = next_id(entries)
        title = random.choice(focus)
        name  = nameify(title, nid)
        rel   = f"services/scripts/iteration_engine/layers/{layer}/{name}.py"
        absf  = HOME / "savant" / rel
        absf.parent.mkdir(parents=True, exist_ok=True)
        code  = f'''#!/usr/bin/env python3
"""
{name}
Layer: {layer}
Role : {title}

This module was generated by Savant Expansion Compiler v2.0 (Dynamic).
It exists because layer demand exceeded current capacity based on:
- shard density
- backlog signals
- soft targets & floors
- optional overrides
"""
import sys, json, os
if __name__ == "__main__":
    console.print("⚙️ {name} ready — layer {layer}")
'''
        absf.write_text(code)
        os.chmod(absf, 0o755)
        entries.append({
            "id": nid,
            "layer": layer,
            "name": name,
            "title": title,
            "path": rel,
            "created": datetime.now(timezone.utc).isoformat()
        })
        log(f"➕ {layer}: created {name}")
    return entries

def main():
    log("=== EXPANSION v2 BEGIN ===")
    entries   = ensure_registry()
    overrides = load_json(OVR, {})
    # Ensure base layer directories and seed if missing
    for layer in LAYER_FOCUS.keys():
        entries = compile_layer(entries, layer, overrides)
    write_registry(entries)

    # Write index for quick lookup
    index = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
        "totals": {
            "layers": len(LAYER_FOCUS),
            "modules": len(entries)
        }
    }
    IDX.write_text(json.dumps(index, indent=2))
    log(f"✅ Expansion complete — {len(entries)} total modules across {len(LAYER_FOCUS)} layers.")
    log("=== EXPANSION v2 END ===")

if __name__ == "__main__":
    main()


# Auto-completion safeguard
pass
