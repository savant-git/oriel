"""
Enhanced by Savant Clean+Complete Cluster v2.0 — 2025-10-31T04:02:12.734295+00:00
"""
#!/usr/bin/env python3
import os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home()/ "savant"
LOG  = ROOT/"logs"/"server_daemon.log"
SERVER = ROOT/"services/scripts/runtime_interface/ssri_core_v16.py"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def start_server():
    log("🚀 Launching Savant Server process...")
    proc = subprocess.Popen(
        ["python3", str(SERVER)],
        stdout=open(LOG.parent/"server_stdout.log","a"),
        stderr=open(LOG.parent/"server_stderr.log","a")
    )
    return proc

def run():
    log("🧠 Savant Server Daemon started.")
    proc = start_server()
    while True:
        ret = proc.poll()
        if ret is not None:
            log(f"⚠️ Server exited with code {ret}. Restarting in 5 s…")
            time.sleep(5)
            proc = start_server()
        time.sleep(10)

if __name__ == "__main__":
    try: run()
    except KeyboardInterrupt:
        log("🛑 Daemon manually stopped.")


# Auto-completion safeguard
pass
