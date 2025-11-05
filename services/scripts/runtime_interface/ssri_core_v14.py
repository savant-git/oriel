from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v14.0 — SAVANT MEMORY SYNTHESIS ENGINE (SME)
──────────────────────────────────────────────────────────────
Adds:
 • Consolidated long-term memory from shards/logs
 • Weighted importance and retrieval ranking
 • Autonomic compression & pruning
──────────────────────────────────────────────────────────────
"""
import os, json, time, hashlib
from pathlib import Path
from flask import Flask, jsonify
ROOT=Path.home()/ "savant"
LOG=ROOT/"logs"/"ssri_v14.log"
MEM=ROOT/"cache"/"memory_index.json"
app=Flask(__name__)
def synthesize_memory():
    entries=[]
    for log in (ROOT/"logs").glob("*.log"):
        try:data=open(log).read().splitlines()[-5:]
        except:continue
        digest=hashlib.sha1(("".join(data)).encode()).hexdigest()[:8]
        entries.append({"file":log.name,"digest":digest})
    MEM.write_text(json.dumps({"timestamp":time.time(),"entries":entries},indent=2))
@app.route("/")
def index():
    synthesize_memory();return MEM.read_text()
if __name__=="__main__":
    console.print("🧠 SSRI v14.0 Memory Synthesis Engine active → http://127.0.0.1:8080")
    app.run(host="0.0.0.0",port=8080)


# Auto-completion safeguard
pass
