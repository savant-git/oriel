from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
◆ SAVANT STANDALONE RUNTIME INTERFACE — SSRI v4.0
──────────────────────────────────────────────────────────────
Adds the Fractal Intelligence Layer:
 • Real-time system metrics (CPU, memory, process load)
 • Animated fractal-curve visualization of Savant hierarchy
 • Shard & Segue topology display
 • Persistent AI context + version delta tracker
 • Live event stream via WebSocket
──────────────────────────────────────────────────────────────
"""
import os, psutil, json, threading, math, time, random, requests
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from flask_sock import Sock

ROOT = Path.home()/"savant"
LOG  = ROOT/"logs"/"ssri_v4.log"
CTX  = ROOT/"cache"/"ssri_context.json"
META = ROOT/"VERSION.meta"
LOG.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
sock = Sock(app)

# --- Helper utilities ------------------------------------------------------
def ai_call(prompt:str)->str:
    key=os.getenv("OPENAI_API_KEY")
    if not key: return "⚠️ No API key loaded."
    headers={"Authorization":f"Bearer {key}"}
    payload={"model":"gpt-4o-mini","messages":[{"role":"system","content":"You are Savant AI."},{"role":"user","content":prompt}]}
    try:
        r=requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=payload,timeout=60)
        if r.status_code!=200: return f"[{r.status_code}] {r.text[:100]}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"⚠️ AI error: {e}"

def fractal_meta():
    return META.read_text().strip() if META.exists() else "◆ unknown | ⬢ unknown | ● unknown"

def shard_graph():
    """Generate pseudo-fractal data (until real shard map connected)."""
    nodes=[{"x":math.cos(i/5)*80+100,"y":math.sin(i/5)*80+100} for i in range(60)]
    edges=[(i,(i+random.randint(3,10))%len(nodes)) for i in range(len(nodes)//2)]
    return {"nodes":nodes,"edges":edges}

# --- Flask routes ----------------------------------------------------------
HTML = """
<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<title>Savant Fractal Intelligence Layer v4.0</title>
<style>
body{margin:0;background:#0b0b0b;color:#ddd;font-family:Consolas,monospace}
#top{background:#111;padding:10px;color:#f6a700}
#stats{position:absolute;top:10px;right:10px;text-align:right;color:#999}
#canvas{background:#000;width:100vw;height:70vh;display:block}
#chat{height:20vh;overflow-y:auto;padding:8px;background:#151515}
.msg-user{color:#f8c250}.msg-ai{color:#6fc8ff}
input{width:100%;padding:8px;background:#000;color:#fff;border:none;font-family:inherit}
</style></head><body>
<div id="top">🧠 SAVANT v4.0 — <small>{{meta}}</small><div id="stats"></div></div>
<canvas id="canvas" width="800" height="400"></canvas>
<div id="chat"></div>
<form id="form"><input id="input" placeholder="Prompt or command…"/></form>
<script>
const ws=new WebSocket("ws://"+location.host+"/stream");
const c=document.getElementById("canvas"),ctx=c.getContext("2d");
let graph=null;function draw(g){if(!g)return;ctx.clearRect(0,0,c.width,c.height);
ctx.strokeStyle="#444";ctx.lineWidth=1;for(e of g.edges){let a=g.nodes[e[0]],b=g.nodes[e[1]];
ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
for(n of g.nodes){ctx.beginPath();ctx.fillStyle="#f6a700";ctx.arc(n.x,n.y,3,0,6.28);ctx.fill();}}
ws.onmessage=e=>{const d=JSON.parse(e.data);
document.getElementById("stats").textContent=d.stats;
graph=d.graph;draw(graph);}
const chat=document.getElementById("chat"),input=document.getElementById("input"),form=document.getElementById("form");
function add(role,txt){const div=document.createElement("div");div.className="msg-"+role;div.textContent=txt;chat.appendChild(div);chat.scrollTop=chat.scrollHeight;}
form.onsubmit=async e=>{e.preventDefault();let q=input.value.trim();if(!q)return;add("user","> "+q);input.value="";
let r=await fetch("/api",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({q})});
let j=await r.json();add("ai",j.reply);}
</script></body></html>
"""

@app.route("/")
def index(): return render_template_string(HTML,meta=fractal_meta())

@app.route("/api",methods=["POST"])
def api():
    q=request.json.get("q","")
    if not q: return jsonify({"reply":"(empty)"})
    if q.startswith("savant-"):
        try:
            res=os.popen(q).read()
        except Exception as e: res=f"Command error: {e}"
        return jsonify({"reply":res})
    ans=ai_call(q)
    ctxlog=json.loads(CTX.read_text()) if CTX.exists() else []
    ctxlog.append({"t":datetime.now().isoformat(),"user":q,"ai":ans})
    CTX.write_text(json.dumps(ctxlog[-200:],indent=2))
    return jsonify({"reply":ans})

@sock.route("/stream")
def stream(ws):
    while True:
        try:
            cpu=psutil.cpu_percent()
            mem=psutil.virtual_memory().percent
            graph=shard_graph()
            msg=json.dumps({"stats":f"CPU {cpu:.1f}% | MEM {mem:.1f}%","graph":graph})
            ws.send(msg)
            time.sleep(2)
        except Exception: break

if __name__=="__main__":
    port=int(os.getenv("SAVANT_PORT","8080"))
    console.print(f"🚀 Savant Fractal Layer v4.0 → http://127.0.0.1:{port}")
    app.run(host="0.0.0.0",port=port)


# Auto-completion safeguard
pass
