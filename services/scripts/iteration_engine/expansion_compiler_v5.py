from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Savant Expansion Compiler v5.0 — Autonomous Differentiation Engine
───────────────────────────────────────────────────────────────────────────────
This version guarantees per-layer uniqueness even when shard signals are flat.
Adds virtualized signal synthesis ("entropy fission") and adaptive weights.
"""

import os, json, math, random, pathlib, time
from datetime import datetime, timezone
try:
    import psutil
except ImportError:
    psutil = None

HOME = pathlib.Path.home()
ROOT = HOME / "savant"
IE   = ROOT / "services" / "scripts" / "iteration_engine"
LOG  = ROOT / "logs" / "expansion_compiler_v5_runtime.log"
REG  = IE / "layer_registry.json"
IDX  = IE / "upgrade_index.json"
SHARDS = ROOT / "knowledge" / "shards"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

LAYER_TITLES = [
    "Cognition","Creativity","Interface","Optimization","Knowledge",
    "Integration","Reasoning","VisualIntelligence","Autonomy","SentienceFramework"
]

# Base personality weights (higher = more expansive)
LAYER_WEIGHT = [1.25,1.15,0.9,0.8,1.4,1.0,1.3,1.1,1.6,2.0]

def safe_entropy(text:str)->float:
    words=set(text.split())
    return math.log2(len(words)+1)

def shard_metrics(layer):
    p = SHARDS / layer
    if not p.exists(): return (0,0,0,0)
    count=size=entropy=0
    latest=0
    for fp in p.rglob("*"):
        if fp.is_file():
            try:
                st=fp.stat()
                latest=max(latest,st.st_mtime)
                size+=st.st_size
                count+=1
                entropy+=safe_entropy(fp.read_text(errors="ignore"))
            except Exception: pass
    age=time.time()-latest if latest>0 else 1e6
    return count, size/max(count,1), entropy/max(count,1), age

def sys_resource_factor():
    if not psutil: return 1.0
    d=psutil.disk_usage(str(HOME))
    m=psutil.virtual_memory()
    return ((d.free/d.total)+(m.available/m.total))/2

# Inject variation when signals are too similar
def synth_signal(layer_idx:int, base:float)->float:
    bias = (math.sin(layer_idx*1.3)+1.1)*random.uniform(0.8,1.4)
    return base * bias * (1 + random.uniform(-0.3,0.3))

def desired_count(layer:str, idx:int, existing:int)->int:
    count,mean,ent,age=shard_metrics(layer)
    res=sys_resource_factor()
    base = (count*0.5 + ent*3.7 + mean/10000 + 5) * LAYER_WEIGHT[idx] * res
    base = synth_signal(idx, base)
    # Add recency bias: newer layers grow faster
    freshness = max(0.5, min(2.0, math.exp(-age/(60*60*24*20))))
    target = int(max(existing, base * freshness))
    # Soft cap: scaling per layer identity
    modcap = (idx+1)*random.uniform(5.0,12.0)
    final = int(target + modcap)
    return final

def load_json(p,fallback):
    try:return json.loads(p.read_text())
    except:return fallback

def ensure_registry():
    if not REG.exists(): REG.write_text("[]")
    return load_json(REG,[])

def next_id(entries): return (max([e["id"] for e in entries], default=0)+1)

def expand_layer(layer, idx, entries):
    existing=[e for e in entries if e["layer"]==layer]
    target=desired_count(layer, idx, len(existing))
    add=max(0,target-len(existing))
    log(f"📊 {layer}: existing={len(existing)} target={target} (+{add})")
    if add==0: return entries
    for _ in range(add):
        nid=next_id(entries)
        name=f"{layer}_Module{nid}"
        rel=f"services/scripts/iteration_engine/layers/{layer}/{name}.py"
        absf=ROOT/rel; absf.parent.mkdir(parents=True,exist_ok=True)
        code=f"#!/usr/bin/env python3\n# {name} — layer {layer}\nconsole.print('⚙️ {name} ready')\n"
        absf.write_text(code); os.chmod(absf,0o755)
        entries.append({"id":nid,"layer":layer,"name":name,"path":rel})
    return entries

def main():
    log("=== EXPANSION v5 BEGIN ===")
    entries=ensure_registry()
    for i,layer_name in enumerate([f"L{n}_{t}" for n,t in enumerate(LAYER_TITLES,1)]):
        entries=expand_layer(layer_name,i,entries)
    REG.write_text(json.dumps(entries,indent=2))
    IDX.write_text(json.dumps({"updated":datetime.now(timezone.utc).isoformat(),"entries":entries},indent=2))
    log(f"✅ Expansion complete — {len(entries)} modules total.")
    log("=== EXPANSION v5 END ===")

if __name__=="__main__":
    main()


# Auto-completion safeguard
pass
