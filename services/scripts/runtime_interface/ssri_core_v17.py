#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v17 — Guaranteed Startup & Heartbeat
──────────────────────────────────────────────────────────────
Ensures that savant/logs/server_daemon.log exists before any
write, logs heartbeat events every minute, and verifies that the
server port 8080 is listening.
──────────────────────────────────────────────────────────────
"""
import os, time, socket
from pathlib import Path
from datetime import datetime, timezone

LOG = Path.home()/ "savant/logs/server_daemon.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def port_check(port=8080):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1",port));s.close();return True
    except: return False

log("🧩 v17 Heartbeat initialized")
while True:
    ok=port_check()
    log(f"💓 Heartbeat OK" if ok else "⚠️ Port 8080 not responding — server may be down")
    time.sleep(60)


# Auto-completion safeguard
pass
