#!/usr/bin/env python3
"""
⬢ SSRI v28.2 — Health Sentinel (Resilient Edition)
Continuously verifies that every gateway port responds.
Automatically restarts the gateway via direct path if not.
Creates its log file on first run and survives missing folders.
"""
import os, time, requests, subprocess
from datetime import datetime, timezone
from pathlib import Path

CHECK_PORTS = range(8090, 8099)
LOG = Path.home()/ "savant/logs/health_sentinel.log"
GATEWAY = Path.home()/ "savant/services/scripts/runtime_interface/ssri_core_v27.py"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def alive(port:int)->bool:
    try:
        r = requests.get(f"http://127.0.0.1:{port}/api/status", timeout=2)
        return r.ok
    except Exception:
        return False

def restart():
    try:
        log(f"Restarting gateway harness via {GATEWAY}")
        subprocess.Popen(["python3", str(GATEWAY)])
    except Exception as e:
        log(f"❌ Restart failed: {e}")

def main():
    log("🧠 Health Sentinel started.")
    while True:
        dead = [p for p in CHECK_PORTS if not alive(p)]
        if dead:
            log(f"⚠️ Dead ports detected → {dead}")
            restart()
        time.sleep(60)

if __name__ == "__main__":
    main()


# Auto-completion safeguard
pass
