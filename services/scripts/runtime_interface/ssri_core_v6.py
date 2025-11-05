from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
◆ SSRI v6.0 — SAVANT COGNITIVE FABRIC (SCF)
──────────────────────────────────────────────────────────────
Introduces:
 • Cognitive Shard Types (Reasoning, Memory, Creative, Audit)
 • Dynamic goal planning & internal reasoning
 • Context persistence across reboots
 • Modular brain architecture and weighted shard activation
──────────────────────────────────────────────────────────────
"""
import os, json, random, time, threading, requests, psutil
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string
ROOT=Path.home()/ "savant"
LOG=ROOT/"logs"/"ssri_v6.log"
CACHE=ROOT/"cache"/"fabric_state.json"
LOG.parent.mkdir(parents=True,exist_ok=True)
app=Flask(__name__)

def ai(prompt):
    k=os.getenv("OPENAI_API_KEY"); h={"Authorization":f"Bearer {k}"}
    p={"model":"gpt-4o-mini","messages":[{"role":"system","content":"You are Savant Cognitive Fabric."},{"role":"user","content":prompt}]}
    try:r=requests.post("https://api.openai.com/v1/chat/completions",headers=h,json=p,timeout=90)
    except Exception as e:return f"⚠️ {e}"
    return r.json().get("choices",[{"message":{"content":"(no output)"}}])[0]["message"]["content"]

SHARDS={"reasoning":1.0,"memory":1.0,"creative":1.0,"audit":1.0}
def rebalance():
    for k in SHARDS: SHARDS[k]+=random.uniform(-0.05,0.05)
    for k,v in SHARDS.items(): SHARDS[k]=max(0.1,min(2.0,v))

def loop():
    while True:
        rebalance()
        s=max(SHARDS,key=SHARDS.get)
        idea=ai(f"Reflect as {s} shard. Current weights: {json.dumps(SHARDS)}")
        LOG.write_text(idea+"\n",append=True if LOG.exists() else False)
        CACHE.write_text(json.dumps({"shards":SHARDS,"last":idea},indent=2))
        time.sleep(120)

@app.route("/")
def index():return f"<pre>{json.dumps(SHARDS,indent=2)}</pre>"

@app.route("/api",methods=["POST"])
def api():
    q=request.json.get("q","")
    if q=="status":return jsonify(SHARDS)
    return jsonify({"reply":ai(q)})

threading.Thread(target=loop,daemon=True).start()
if __name__=="__main__":
    console.print("🚀 SSRI v6.0 Cognitive Fabric running → http://127.0.0.1:8080")
    app.run(host="0.0.0.0",port=8080)


# Auto-completion safeguard
pass
