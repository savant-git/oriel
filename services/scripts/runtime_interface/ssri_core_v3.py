from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
◆ SAVANT STANDALONE RUNTIME INTERFACE — SSRI v3.0
──────────────────────────────────────────────────────────────
Web dashboard + persistent context engine.
Provides:
 • Live chat panel + system console
 • Fractal version meta-display (◆ ⬢ ●)
 • Persistent history (chat + commands)
 • Cloud + GitHub status indicators
 • REST endpoints for remote control
──────────────────────────────────────────────────────────────
"""
import os, threading, json, subprocess, requests
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

ROOT = Path.home()/ "savant"
LOG  = ROOT/"logs"/"ssri_web.log"
CTX  = ROOT/"cache"/"ssri_context.json"
META = ROOT/"VERSION.meta"
LOG.parent.mkdir(parents=True, exist_ok=True)
app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html><html><head>
<title>Savant Dashboard v3.0</title>
<style>
body{background:#0c0c0c;color:#e0e0e0;font-family:Consolas,monospace;margin:0}
#top{background:#111;padding:10px;color:#f6a700}
#meta{float:right;color:#f8c250}
#chat{height:70vh;overflow-y:auto;background:#181818;padding:10px;margin:0}
#input{width:100%;padding:10px;background:#000;border:none;color:#fff;font-family:inherit}
.msg-user{color:#f8c250;margin:4px 0}
.msg-ai{color:#b4e2ff;margin:4px 0}
</style></head><body>
<div id="top">🧠 SAVANT v3.0 <small id="meta">{{meta}}</small></div>
<div id="chat"></div>
<form id="form"><input id="input" placeholder="Type a prompt or savant-command…"/></form>
<script>
const chat=document.getElementById("chat"),input=document.getElementById("input"),form=document.getElementById("form");
function add(role,txt){const div=document.createElement("div");div.className="msg-"+role;div.textContent=txt;chat.appendChild(div);chat.scrollTop=chat.scrollHeight;}
form.onsubmit=async e=>{
 e.preventDefault();const txt=input.value.trim();if(!txt)return;add("user","> "+txt);input.value="";
 const r=await fetch("/api", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({q:txt})});
 const j=await r.json();add("ai",j.reply);
}
</script></body></html>
"""

def log(msg:str):
    LOG.write_text(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n",append=LOG.exists())

def ai_call(prompt:str)->str:
    key=os.getenv("OPENAI_API_KEY"); proj=os.getenv("OPENAI_PROJECT")
    if not key: return "⚠️ No API key loaded."
    headers={"Authorization":f"Bearer {key}"}
    if proj: headers["OpenAI-Project"]=proj
    payload={"model":"gpt-4o-mini","messages":[{"role":"system","content":"You are Savant AI."},{"role":"user","content":prompt}]}
    try:
        r=requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=payload,timeout=60)
        if r.status_code!=200: return f"[{r.status_code}] {r.text[:120]}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"⚠️ Error: {e}"

def save_context(entry):
    data=json.loads(CTX.read_text()) if CTX.exists() else []
    data.append(entry)
    CTX.write_text(json.dumps(data[-200:],indent=2))

def fractal_meta():
    return META.read_text().strip() if META.exists() else "◆ unknown | ⬢ unknown | ● unknown"

@app.route("/")
def index(): return render_template_string(TEMPLATE,meta=fractal_meta())

@app.route("/api",methods=["POST"])
def api():
    q=request.json.get("q","")
    if not q: return jsonify({"reply":"(empty)"})
    if q.startswith("savant-"):
        try:
            res=subprocess.run(q,shell=True,capture_output=True,text=True)
            out=res.stdout or res.stderr
        except Exception as e: out=f"Command error: {e}"
        save_context({"t":datetime.now().isoformat(),"user":q,"ai":out})
        return jsonify({"reply":out})
    ans=ai_call(q)
    save_context({"t":datetime.now().isoformat(),"user":q,"ai":ans})
    return jsonify({"reply":ans})

def run():
    port=int(os.getenv("SAVANT_PORT","8080"))
    console.print(f"🚀 Savant Dashboard v3.0 → http://127.0.0.1:{port}")
    app.run(host="0.0.0.0",port=port,debug=False)

if __name__=="__main__":
    run()


# Auto-completion safeguard
pass
