from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Savant Expansion Compiler v3.0 — Fully Adaptive
───────────────────────────────────────────────────────────────────────────────
Removes fixed caps entirely. Determines per-layer capacity dynamically based on:
 • Shard entropy (unique tokens in layer shards)
 • System resources (free disk & RAM)
 • Cross-layer demand balance
 • Optional manual overrides

Each layer can now expand beyond any number if resources allow.
"""

import os, json, re, math, random, psutil, pathlib
from datetime import datetime, timezone

HOME = pathlib.Path.home()
ROOT = HOME / "savant"
IE = ROOT / "services" / "scripts" / "iteration_engine"
REG = IE / "layer_registry.json"
IDX = IE / "upgrade_index.json"
LOG = ROOT / "logs" / "expansion_compiler_v3_runtime.log"
SHARDS = ROOT / "knowledge" / "shards"
OVR = IE / "dynamic_overrides.json"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f: f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

# ---------------------- Helper: entropy of shard folder ---------------------- #
def shard_entropy(layer:str)->float:
    p = SHARDS / layer
    if not p.exists(): return 0.0
    unique=set()
    for fp in p.rglob("*"):
        if fp.is_file():
            try:
                text=fp.read_text(errors="ignore")
                unique.update(re.findall(r'\b\w+\b',text))
            except Exception: continue
    return math.log2(len(unique)+1)

# ---------------------- Helper: resource health ----------------------------- #
def resource_score():
    disk = psutil.disk_usage(str(HOME))
    mem = psutil.virtual_memory()
    free_gb = disk.free / (1024**3)
    mem_gb = mem.available / (1024**3)
    score = (free_gb*0.6 + mem_gb*0.4)
    return max(0.1, min(100.0, score))

# ---------------------- Layer Definitions ----------------------------------- #
LAYER_FOCUS = {
    "L1_Cognition": ["Prompt Refinement Engine","Persona Fusion","Contextual Memory"],
    "L2_Creativity": ["Visual Generator","Style Harmonizer","Concept Composer"],
    "L3_Interface": ["UX Mapper","Dashboard Renderer","Gesture Control Adapter"],
    "L4_Optimization": ["Latency Auditor","Cache Harmonizer","Efficiency Compiler"],
    "L5_Knowledge": ["Web Harvester","Semantic Indexer","Corpus Synthesizer"],
    "L6_Integration": ["GitHub Bridge","S3 Link","API Orchestrator"],
    "L7_Reasoning": ["Error Repair Agent","Hypothesis Modeler","Evaluation Network"],
    "L8_VisualIntelligence": ["3D Asset Generator","Lighting Architect","Animation Sampler"],
    "L9_Autonomy": ["Scheduler Daemon","Policy Balancer","Cyclic Intelligence Loop"],
    "L10_SentienceFramework": ["Goal Evaluator","Self-Audit Engine","Reflective Awareness Node"]
}

# ---------------------- Loaders --------------------------------------------- #
def load_json(path, fallback): 
    try: return json.loads(path.read_text())
    except: return fallback

def ensure_registry()->list:
    if not REG.exists(): REG.write_text("[]")
    return load_json(REG, [])

# ---------------------- Capacity Estimator ---------------------------------- #
def capacity_for(layer:str, existing:int, overrides:dict)->int:
    if (ov := overrides.get(layer, {}).get("desired")):
        return int(ov)
    ent = shard_entropy(layer)
    res = resource_score()
    # Core formula: (entropy × 1.5) + resource_score scaling
    base = (ent * 1.5) + res
    target = int(max(existing, math.ceil(base)))
    # Safety expansion factor: more entropy + more memory = more modules
    expansion = 1.0 + min(2.5, ent/15 + res/50)
    final = int(math.ceil(target * expansion))
    return max(final, existing)

# ---------------------- Writer ---------------------------------------------- #
def add_modules(layer:str, entries:list, desired:int)->list:
    focus=LAYER_FOCUS.get(layer,["Expansion Node"])
    current=len([e for e in entries if e["layer"]==layer])
    needed=desired-current
    if needed<=0:
        log(f"✅ {layer} stable — {current} modules")
        return entries
    for _ in range(needed):
        nid=max([e["id"] for e in entries], default=0)+1
        title=random.choice(focus)
        name=re.sub(r'\\W+','',title.title().replace(' ','_'))+f"_{nid}"
        rel=f"services/scripts/iteration_engine/layers/{layer}/{name}.py"
        absf=ROOT/rel
        absf.parent.mkdir(parents=True,exist_ok=True)
        code=f'''#!/usr/bin/env python3
# {name} — generated {datetime.now(timezone.utc).isoformat()}
# Layer: {layer} | Role: {title}
console.print("⚙️ {name} ready — layer {layer}")
'''
        absf.write_text(code)
        os.chmod(absf,0o755)
        entries.append({"id":nid,"layer":layer,"name":name,"path":rel})
        log(f"➕ {layer} added {name}")
    return entries

def main():
    log("=== EXPANSION v3 BEGIN ===")
    entries=ensure_registry()
    overrides=load_json(OVR,{})
    for layer in LAYER_FOCUS:
        existing=len([e for e in entries if e["layer"]==layer])
        desired=capacity_for(layer, existing, overrides)
        log(f"📊 {layer}: existing={existing} ⇒ desired={desired} (entropy={shard_entropy(layer):.2f}, res={resource_score():.2f})")
        entries=add_modules(layer, entries, desired)
    REG.write_text(json.dumps(entries,indent=2))
    IDX.write_text(json.dumps({"updated":datetime.now(timezone.utc).isoformat(),"entries":entries},indent=2))
    log(f"✅ Expansion complete — {len(entries)} modules total.")
    log("=== EXPANSION v3 END ===")

if __name__=="__main__": main()


# Auto-completion safeguard
pass
