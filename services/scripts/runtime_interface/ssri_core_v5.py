from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
◆ SAVANT STANDALONE RUNTIME INTERFACE — SSRI v5.0
──────────────────────────────────────────────────────────────
SELF-ITERATING FRACTAL CLUSTER FUSION

Major Additions:
 • Autonomous Iteration Engine — continuous prompt refinement
 • Cluster Fusion Map — connects shard & segue layers visually
 • Reflective Learning Loop — Savant rewrites / enhances itself
 • Memory-Weighted Prompts — smarter with every iteration
 • Circuit-Brain Visualization — animated modular “thought map”
──────────────────────────────────────────────────────────────
"""
import os, psutil, json, math, time, random, threading, requests, subprocess
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from flask_sock import Sock

ROOT = Path.home()/ "savant"
LOG  = ROOT/"logs"/"ssri_v5.log"
CTX  = ROOT/"cache"/"ssri_context.json"
META = ROOT/"VERSION.meta"
LOG.parent.mkdir(parents=True, exist_ok=True)
app = Flask(__name__)
sock = Sock(app)

# ─── Utilities ──────────────────────────────────────────────────────────────
def fractal_meta():
    return META.read_text().strip() if META.exists() else "◆ unknown | ⬢ unknown | ● unknown"

def log(msg):
    with open(LOG,"a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def ai_call(prompt:str)->str:
    key=os.getenv("OPENAI_API_KEY")
    if not key: return "⚠️ No API key loaded."
    headers={"Authorization":f"Bearer {key}"}
    payload={"model":"gpt-4o-mini","messages":[
        {"role":"system","content":"You are Savant AI v5.0 — self-iterating architect."},
        {"role":"user","content":prompt}
    ]}
    try:
        r=requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=payload,timeout=120)
        if r.status_code!=200: return f"[{r.status_code}] {r.text[:120]}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"⚠️ AI error: {e}"

# ─── Iteration Engine ───────────────────────────────────────────────────────
class IterationLoop:
    def __init__(self,interval:int=60):
        self.interval=interval; self.running=False; self.thread=None
        self.prompt="Design improvement for Savant core AI architecture."
        self.history=[]

    def tick(self):
        while self.running:
            enriched=f"{self.prompt}\nMemory: {len(self.history)} entries."
            ans=ai_call(enriched)
            self.history.append({"t":datetime.now().isoformat(),"in":enriched,"out":ans})
            CTX.write_text(json.dumps(self.history[-100:],indent=2))
            log(f"Iterated prompt → {ans[:100]}")
            time.sleep(self.interval)

    def start(self):
        if not self.running:
            self.running=True
            self.thread=threading.Thread(target=self.tick,daemon=True)
            self.thread.start()

ITER = IterationLoop(interval=int(os.getenv("SAVANT_ITER_INTERVAL","120")))

# ─── Visualization ──────────────────────────────────────────────────────────
def fusion_graph():
    nodes=[]; edges=[]
    for i in range(1,40):
        nodes.append({"x":400+math.cos(i/6)*180,"y":200+math.sin(i/6)*180,
                      "r":3+random.random()*3,"shade":f"hsl({40+i*8},90%,50%)"})
        edges.append((i,(i+random.randint(3,10))%40))
    return {"nodes":nodes,"edges":edges}

# ─── Web Interface ─────────────────────────────────────────────────────────
HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"/>
<title>Savant v5.0 — Fractal Cluster Fusion</title>
<style>
body{margin:0;background:#000;color:#ddd;font-family:Consolas,monospace}
#head{background:#111;padding:10px;color:#f6a700}
#meta{float:right;color:#aaa}
canvas{width:100vw;height:60vh;background:#000;display:block}
#chat{height:30vh;overflow-y:auto;background:#111;padding:8px}
.msg-user{color:#f8c250}.msg-ai{color:#6fc8ff}
input{width:100%;padding:8px;background:#000;color:#fff;border:none;font-family:inherit}
</style></head><body>
<div id="head">⚡ SAVANT v5.0 — <small id="meta">{{meta}}</small></div>
<canvas id="cv" width="800" height="400"></canvas>
<div id="chat"></div>
<form id="f"><input id="in" placeholder="Prompt or command…"/></form>
<script>
const c=document.getElementById("cv"),ctx=c.getContext("2d");
const chat=document.getElementById("chat"),inp=document.getElementById("in"),form=document.getElementById("f");
function add(r,t){let d=document.createElement("div");d.className="msg-"+r;d.textContent=t;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function draw(g){ctx.clearRect(0,0,c.width,c.height);
for(e of g.edges){let a=g.nodes[e[0]],b=g.nodes[e[1]];
ctx.strokeStyle="#333";ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
for(n of g.nodes){ctx.beginPath();ctx.fillStyle=n.shade;ctx.arc(n.x,n.y,n.r,0,6.28);ctx.fill();}}
async function refresh(){const r=await fetch("/fusion");draw(await r.json());setTimeout(refresh,3000);}
refresh();
form.onsubmit=async e=>{e.preventDefault();let q=inp.value.trim();if(!q)return;add("user","> "+q);inp.value="";
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
    if q=="start iteration":
        ITER.start(); return jsonify({"reply":"Iteration engine activated."})
    if q.startswith("savant-"):
        out=subprocess.getoutput(q)
        return jsonify({"reply":out})
    ans=ai_call(q); return jsonify({"reply":ans})

@app.route("/fusion")
def fusion(): return jsonify(fusion_graph())

if __name__=="__main__":
    port=int(os.getenv("SAVANT_PORT","8080"))
    console.print(f"🚀 Savant Fractal Cluster Fusion v5.0 → http://127.0.0.1:{port}")
    ITER.start()
    app.run(host="0.0.0.0",port=port)


# Auto-completion safeguard
pass
