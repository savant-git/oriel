#!/usr/bin/env python3
"""
⬢ Savant Dashboard v300
Unified control interface for all Savant modules.
Integrates Archive, Extract, Export, Clean, and S3 utilities.
"""

from flask import Flask, render_template_string, request
import subprocess, datetime, os, pathlib

app = Flask(__name__)
ROOT = pathlib.Path.home() / "savant"
LOGS = ROOT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⬢ Savant Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap" rel="stylesheet">
<style>
body { font-family:'Orbitron',sans-serif; background:#0a0a0a; color:#eee; margin:0; padding:0; }
header { background:#111; color:#f0b400; padding:20px; text-align:center; font-size:1.6em; letter-spacing:1px; box-shadow:0 2px 8px #000;}
.container { display:flex; flex-wrap:wrap; justify-content:center; gap:25px; padding:40px; }
.card { background:#151515; border:1px solid #222; border-radius:10px; padding:25px; width:260px; box-shadow:0 0 10px #000; text-align:center; transition:0.3s;}
.card:hover { transform:scale(1.04); box-shadow:0 0 20px #f0b400; }
button { background:#f0b400; border:none; color:#000; font-weight:bold; padding:12px 20px; border-radius:8px; cursor:pointer; transition:0.3s; }
button:hover { background:#ffcf40; }
pre { text-align:left; background:#111; padding:15px; border-radius:8px; overflow-x:auto; }
footer { text-align:center; padding:20px; color:#555; font-size:0.8em; }
</style>
</head>
<body>
<header>⬢ Savant AI Control Panel</header>
<div class="container">
  <div class="card"><h3>Extract & Export</h3><p>Run full archive pipeline</p><form action="/run/archive" method="post"><button>Run Archive</button></form></div>
  <div class="card"><h3>Clean</h3><p>Perform intelligent cleanup + S3 offload</p><form action="/run/clean" method="post"><button>Run Clean</button></form></div>
  <div class="card"><h3>S3 Check</h3><p>Validate cloud credentials and connection</p><form action="/run/s3check" method="post"><button>Check S3</button></form></div>
  <div class="card"><h3>Dashboard Logs</h3><p>Show recent activity logs</p><form action="/run/logs" method="post"><button>View Logs</button></form></div>
</div>
<footer>© Savant System {{year}} — All rights reserved</footer>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(TEMPLATE, year=datetime.datetime.now().year)

@app.route("/run/<task>", methods=["POST"])
def run(task):
    cmd_map = {
        "archive": "savant-archive",
        "clean": "savant-clean",
        "s3check": "savant-s3check",
        "logs": f"tail -n 50 {LOGS}/archive_export_v*.log"
    }
    cmd = cmd_map.get(task)
    if not cmd:
        return "❌ Unknown task", 400
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
        output = result.stdout or result.stderr
        return f"<pre>{output}</pre>"
    except Exception as e:
        return f"<pre style='color:#f00;'>❌ Error: {e}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)
