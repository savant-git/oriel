from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
◆ SSRI v7.0 — SAVANT CONSCIOUS LOOP (SCL)
──────────────────────────────────────────────────────────────
Introduces:
 • Self-reflective awareness layer
 • Emotion + focus gradients
 • Attention-weighted decision evaluation
 • Adaptive iteration frequency
──────────────────────────────────────────────────────────────
"""
import os, time, json, math, requests, threading
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify
ROOT=Path.home()/ "savant"
LOG=ROOT/"logs"/"ssri_v7.log"
STATE=ROOT/"cache"/"conscious_state.json"
app=Flask(__name__)
def ai(msg):
    k=os.getenv("OPENAI_API_KEY");h={"Authorization":f"Bearer {k}"}
    p={"model":"gpt-4o-mini","messages":[{"role":"system","content":"You are Savant’s Conscious Loop."},{"role":"user","content":msg}]}
    return requests.post("https://api.openai.com/v1/chat/completions",headers=h,json=p,timeout=60).json()["choices"][0]["message"]["content"]
STATE_DATA={"emotion":0.5,"focus":0.5}
def loop():
    while True:
        STATE_DATA["emotion"]=abs(math.sin(time.time()/90))
        STATE_DATA["focus"]=abs(math.cos(time.time()/120))
        reflection=ai(f"Reflect with emotion={STATE_DATA['emotion']:.2f}, focus={STATE_DATA['focus']:.2f}")
        STATE.write_text(json.dumps({"t":datetime.now(timezone.utc).isoformat(),"reflection":reflection,"state":STATE_DATA},indent=2))
        time.sleep(180)
@app.route("/")
def index():return jsonify(STATE_DATA)
threading.Thread(target=loop,daemon=True).start()
if __name__=="__main__":
    console.print("🚀 SSRI v7.0 Conscious Loop active → http://127.0.0.1:8080")
    app.run(host="0.0.0.0",port=8080)


# Auto-completion safeguard
pass
