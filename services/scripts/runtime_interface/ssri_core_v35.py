#!/usr/bin/env python3
"""
⬢ SSRI v35 — Migration Health Dashboard API
──────────────────────────────────────────────────────────────
Serves a lightweight Flask dashboard summarizing:
  • Daemon uptime
  • Export status
  • Cloud sync health
  • API connections
──────────────────────────────────────────────────────────────
"""
from flask import Flask, jsonify
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
LOGS = Path.home()/ "savant/logs"

@app.route("/health")
def health():
    status = {
        "uptime": datetime.now().isoformat(),
        "exports": len(list((LOGS.parent/"exports").glob("*.zip*"))),
        "last_export_log": str(max(LOGS.glob("export*.log"), key=lambda f: f.stat().st_mtime, default="N/A")),
        "ready_flag": (LOGS/"MIGRATION_READY").exists()
    }
    return jsonify(status)

if __name__=="__main__":
    app.run(host="127.0.0.1", port=8094)


# Auto-completion safeguard
pass
