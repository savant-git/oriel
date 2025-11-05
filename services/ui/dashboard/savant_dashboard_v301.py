#!/usr/bin/env python3
"""
⬢ Savant Dashboard v301
Full operational control center for the Savant AI system.
This version fixes display issues and adds live HTML output.
"""

from flask import Flask, render_template_string, request
import subprocess, datetime, os, pathlib

app = Flask(__name__)
ROOT = pathlib.Path.home() / "savant"
LOGS = ROOT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

# --- Dashboard HTML Template ---
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⬢ Savant Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; }
body { font-family:'Orbitron',sans-serif; background:#0b0b0b; color:#ddd; margin:0; }
header { background:#111; color:#f0b400; padding:20px; text-align:center; font-size:1.6em; letter-spacing:1px; box-shadow:0 3px 10px #000;}
.container { display:flex; flex-wrap:wrap; justify-content:center; gap:25px; padding:40px; }
.card { background:#181818; border:1px solid #333; border-radius:12px; padding:25px; width:280px; text-align:center; box-shadow:0 0 12px #000; transition:0.25s; }
.card:hover { transform:scale(1.03); box-shadow:0 0 20px #f0b400; }
button { background:#f0b400; border:none; color:#000; font-weight:bold; padding:12px 22px; border-radius:8px; cursor:pointer; transition:0.3s; }
button:hover { background:#ffcf40; }
pre { text-align:left; background:#111; padding:15px; border-radius:8px; overflow-x:auto; color:#9effa8; max-height:70vh; overflow-y:auto; }
footer { text-align:center; padding:20px; color:#666; font-size:0.9em; border-top:1px solid #222; margin-top:30px; }
</style>
</head>
<body>
<header>⬢ SAVANT AI CONTROL CENTER</header>

<div class="container">
  <div class="card"><h3>🧠 Extract & Export</h3><p>Run full archive pipeline</p><form action="/run/archive" method="post"><button>Run Archive</button></form></div>
  <div class="card"><h3>🧹 Clean</h3><p>Perform deep cleanup + S3 offload</p><form action="/run/clean" method="post"><button>Run Clean</button></form></div>
  <div class="card"><h3>☁️  S3 Check</h3><p>Validate cloud credentials</p><form action="/run/s3check" method="post"><button>Check S3</button></form></div>
  <div class="card"><h3>📜 Logs</h3><p>Show recent activity</p><form action="/run/logs" method="post"><button>View Logs</button></form></div>
  <div class="card"><h3>⚙️  System Info</h3><p>Check environment and version</p><form action="/run/sysinfo" method="post"><button>Show Info</button></form></div>
</div>

<footer>© Savant System {{year}} — All rights reserved</footer>
</body>
</html>
"""

# --- Flask routes ---
@app.route("/")
def home():
    return render_template_string(TEMPLATE, year=datetime.datetime.now().year)

@app.route("/run/<task>", methods=["POST"])
def run(task):
    cmd_map = {
        "archive": "savant-archive",
        "clean": "savant-clean",
        "s3check": "savant-s3check",
        "logs": f"tail -n 40 {LOGS}/archive_export_v*.log",
        "sysinfo": "df -h && free -h && uname -a"
    }
    cmd = cmd_map.get(task)
    if not cmd:
        return "❌ Unknown task", 400
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
        output = result.stdout or result.stderr
        html = f"""
        <html><head><title>{task} Results</title>
        <meta charset='UTF-8'><style>body{{background:#0a0a0a;color:#9effa8;font-family:monospace;padding:20px;}}</style></head>
        <body><h2>⬢ Task: {task}</h2><pre>{output}</pre><a href='/' style='color:#f0b400'>← Back to Dashboard</a></body></html>
        """
        return html
    except Exception as e:
        return f"<pre style='color:#f00;'>❌ Error: {e}</pre>"

if __name__ == "__main__":
    print("🚀 Starting Savant Dashboard v301 on port 8099…")
    print("🌐 Access it at: http://<your_VM_IP>:8099")
    app.run(host="0.0.0.0", port=8099)
