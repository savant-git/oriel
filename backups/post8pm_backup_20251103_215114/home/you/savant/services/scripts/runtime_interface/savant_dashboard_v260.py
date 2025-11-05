#!/usr/bin/env python3
"""
⬢ Savant Dashboard v260
Unified Control Panel for Archive, Export, Clean, S3, and Logs
Modular, shard-ready, and styled with Savant branding.
"""

import os, subprocess, threading, queue, time
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------
# Config
# ---------------------------------------------------------------
BASE = Path.home() / "savant"
LOGS = BASE / "logs"
PORT = int(os.getenv("SAVANT_DASHBOARD_PORT", "8094"))
app = Flask(__name__)

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def run_command(cmd):
    """Run a shell command and stream live output"""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(process.stdout.readline, ''):
        yield line.strip()
    process.stdout.close()
    process.wait()

def read_recent_logs():
    """Fetch last 200 lines of latest log"""
    log_files = sorted(LOGS.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return ["No logs yet."]
    with log_files[0].open(errors="ignore") as f:
        lines = f.readlines()[-200:]
    return [l.strip() for l in lines]

# ---------------------------------------------------------------
# Routes
# ---------------------------------------------------------------
@app.route("/")
def home():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(DASHBOARD_HTML, now=now)

@app.route("/run", methods=["POST"])
def run_task():
    task = request.json.get("task")
    mapping = {
        "archive": "savant-archive",
        "export": "savant-export",
        "clean": "savant-clean",
        "s3check": "savant-s3check",
    }
    if task not in mapping:
        return jsonify({"error": "Unknown task"}), 400
    cmd = f"bash -lc 'source ~/.bashrc && {mapping[task]}'"
    output = []
    for line in run_command(cmd):
        output.append(line)
    return jsonify({"output": output})

@app.route("/logs")
def get_logs():
    return jsonify({"lines": read_recent_logs()})

# ---------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------
DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⬢ Savant Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<style>
:root {
  --bg: #0d0d0f; --fg: #e7e7ea; --accent: #00bcd4; --muted: #888;
  --btn-bg: #1b1b1e; --btn-hover: #2b2b30;
}
* { box-sizing: border-box; font-family: "Inter", "Segoe UI", sans-serif; }
body { margin:0; background:var(--bg); color:var(--fg); overflow-x:hidden; }
header {
  text-align:center; padding:24px;
  font-size:28px; font-weight:700; letter-spacing:1px;
  color:var(--accent); background:#111; box-shadow:0 2px 10px rgba(0,0,0,0.5);
}
main { display:flex; flex-direction:column; align-items:center; padding:40px 20px; }
button {
  background:var(--btn-bg); border:none; border-radius:10px;
  color:var(--fg); font-size:18px; padding:12px 30px; margin:10px;
  transition:background 0.3s ease;
}
button:hover { background:var(--btn-hover); color:var(--accent); cursor:pointer; }
#logbox {
  width:90%; max-width:900px; height:400px; overflow:auto;
  background:#111; color:#9f9; border-radius:12px; padding:10px;
  font-family:monospace; font-size:14px;
  border:1px solid #222; margin-top:40px;
}
footer {
  margin-top:60px; color:var(--muted); font-size:14px;
  text-align:center; padding-bottom:20px;
}
</style>
</head>
<body>
<header>⬢ Savant Dashboard</header>
<main>
  <div>
    <button onclick="runTask('archive')">🧠 Archive + Export</button>
    <button onclick="runTask('export')">📦 Export</button>
    <button onclick="runTask('clean')">🧹 Clean</button>
    <button onclick="runTask('s3check')">☁️ S3 Check</button>
  </div>
  <div id="logbox">[Logs will appear here]</div>
</main>
<footer>Generated {{now}} • Savant v260 • GSAP Flex UI</footer>
<script>
async function runTask(task) {
  const logbox = document.getElementById('logbox');
  logbox.textContent = `[${new Date().toLocaleTimeString()}] Starting ${task}...\n`;
  const res = await fetch('/run', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({task})});
  const data = await res.json();
  if (data.output) {
    data.output.forEach(line => logbox.textContent += line + '\\n');
  } else logbox.textContent += (data.error || "Unknown error") + '\\n';
  logbox.scrollTop = logbox.scrollHeight;
}
setInterval(async()=>{
  const res = await fetch('/logs');
  const data = await res.json();
  if(data.lines){
    document.getElementById('logbox').textContent = data.lines.join('\\n');
  }
}, 5000);
gsap.from("button", {opacity:0, y:20, stagger:0.1, duration:0.8, ease:"power3.out"});
</script>
</body>
</html>
"""

# ---------------------------------------------------------------
# Run Server
# ---------------------------------------------------------------
if __name__ == "__main__":
    print(f"⬢ Savant Dashboard v260 running on http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
