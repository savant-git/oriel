from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Savant Expansion Compiler v4.0 — Organic Growth Engine
───────────────────────────────────────────────────────────────
Truly self-differentiating layer sizing.  Each layer decides its
own growth using:
  • Entropy + file count + mean file size
  • Time-since-last-update curve
  • Conceptual weight per layer
  • Random organic drift
"""

import os, json, math, random, pathlib, time
from datetime import datetime, timezone

try: import psutil
except: psutil=None

HOME = pathlib.Path.home()
ROOT = HOME / "savant"
IE   = ROOT / "services" / "scripts" / "iteration_engine"
LOG  = ROOT / "logs" / "expansion_compiler_v4_runtime.log"
REG  = IE / "layer_registry.json"
IDX  = IE / "upgrade_index.json"
SHARDS = ROOT / "knowledge" / "shards"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG,"a") as f: f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

# ---------------- Layer weights (importance) ---------------- #
LAYER_WEIGHT = {
    "L1_Cognition":1.25, "L2_Creativity":1.15, "L3_Interface":0.9,
    "L4_Optimization":0.8, "L5_Knowledge":1.4, "L6_Integration":1.0,
    "L7_Reasoning":1.3, "L8_VisualIntelligence":1.1, "L9_Autonomy":1.6,
    "L10_SentienceFramework":2.0
}

# ---------------- Metrics ---------------- #
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
                text=fp.read_text(errors="ignore")
                words=set(text.split())
                entropy+=math.log2(len(words)+1)
            except: pass
    age = time.time()-latest if latest>0 else 1e6
    mean_size = size/max(count,1)
    ent = entropy/max(count,1) if count>0 else 0
    return count,mean_size,ent,age

def sys_resource_factor():
    if not psutil: return 1.0
    d=psutil.disk_usage(str(HOME))
    m=psutil.virtual_memory()
    free_ratio=(d.free/d.total + m.available/m.total)/2
    return max(0.2,min(1.0,free_ratio*1.5))

# ---------------- Growth Formula ---------------- #
def desired_count(layer, existing):
    count,mean,ent,age=shard_metrics(layer)
    weight=LAYER_WEIGHT.get(layer,1.0)
    res=sys_resource_factor()
    drift=random.uniform(0.85,1.15)

    # Layers with many shards + high entropy + recent change get more modules
    freshness = max(0.1, min(2.0, math.exp(-age/(60*60*24*30))))  # months
    score = ( (count*0.8) + (ent*4.2) + (mean/15000) ) * weight * freshness * res * drift
    target = max(existing, int(score)+5)
    return target

# ---------------- Registry helpers ---------------- #
def load_json(p,fallback): 
    try:return json.loads(p.read_text())
    except:return fallback

def ensure_registry():
    if not REG.exists(): REG.write_text("[]")
    return load_json(REG,[])

def next_id(entries): return (max([e["id"] for e in entries]) if entries else 0)+1

# ---------------- Main ---------------- #
def expand_layer(layer, entries):
    existing=[e for e in entries if e["layer"]==layer]
    target=desired_count(layer,len(existing))
    add=max(0,target-len(existing))
    log(f"📊 {layer}: existing={len(existing)} target={target} (+{add})")
    if add==0: return entries
    for _ in range(add):
        nid=next_id(entries)
        name=f"{layer}_Module{nid}"
        rel=f"services/scripts/iteration_engine/layers/{layer}/{name}.py"
        absf=ROOT/rel; absf.parent.mkdir(parents=True,exist_ok=True)
        code=f"#!/usr/bin/env python3\n# {name} — layer {layer} auto-generated\nconsole.print('⚙️ {name} ready')\n"
        absf.write_text(code); os.chmod(absf,0o755)
        entries.append({"id":nid,"layer":layer,"name":name,"path":rel})
    return entries

def main():
    log("=== EXPANSION v4 BEGIN ===")
    layers=[f"L{i}_{n}" for i,n in enumerate([
        "Cognition","Creativity","Interface","Optimization","Knowledge",
        "Integration","Reasoning","VisualIntelligence","Autonomy","SentienceFramework"],1)]
    entries=ensure_registry()
    for layer in layers: entries=expand_layer(layer,entries)
    REG.write_text(json.dumps(entries,indent=2))
    IDX.write_text(json.dumps({"updated":datetime.now(timezone.utc).isoformat(),"entries":entries},indent=2))
    log(f"✅ Expansion complete — {len(entries)} modules total.")
    log("=== EXPANSION v4 END ===")

if __name__=="__main__": main()


# Auto-completion safeguard
pass
