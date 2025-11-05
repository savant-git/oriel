from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v15.0 — SAVANT DEVELOPER CONTROL INTERFACE (SDC)
──────────────────────────────────────────────────────────────
Adds:
 • REST endpoints for dev commands (/api/restart, /api/status)
 • Local control bridge for connected IDEs
 • Command authentication with tokens
──────────────────────────────────────────────────────────────
"""
import os, json, subprocess
from flask import Flask, jsonify, request
ROOT=os.path.expanduser("~/savant")
app=Flask(__name__)
TOKEN=os.getenv("SAVANT_DEV_TOKEN","dev")
@app.route("/api/status")
def status():return jsonify({"status":"online","cwd":os.getcwd()})
@app.route("/api/restart",methods=["POST"])
def restart():
    if request.args.get("token")!=TOKEN:return jsonify({"error":"unauthorized"}),403
    subprocess.Popen(["nohup","bash","~/savant/services/scripts/intelligence_cluster/autonomous_runtime.sh"])
    return jsonify({"message":"restarted"})
if __name__=="__main__":
    console.print("🧩 SSRI v15.0 Developer Control Interface → http://127.0.0.1:8080/api/status")
    app.run(host="0.0.0.0",port=8080)


# Auto-completion safeguard
pass
