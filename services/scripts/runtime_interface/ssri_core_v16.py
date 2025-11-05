#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v16.1 — Smart Port Binding
──────────────────────────────────────────────────────────────
Automatically detects if 8080 is busy and rebinds to 8090 before
starting Flask.  Logs which port was used.
──────────────────────────────────────────────────────────────
"""
import socket, os
from flask import Flask
from datetime import datetime
from pathlib import Path

LOG = Path.home()/ "savant/logs/server_port.log"
def log(msg): LOG.parent.mkdir(parents=True, exist_ok=True); LOG.open("a").write(f"[{datetime.now().isoformat()}] {msg}\n")

def first_free(preferred=8080):
    for p in (preferred,8090,8091):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1",p));s.close();return p
        except OSError: pass
    raise SystemExit("❌ No free ports in range 8080–8091")

app = Flask(__name__)

@app.route("/")
def index(): return "Savant Server v16.1 running."

if __name__ == "__main__":
    port=first_free()
    log(f"🌐 Savant Server binding to port {port}")
    app.run(host="127.0.0.1",port=port)


# Auto-completion safeguard
pass
