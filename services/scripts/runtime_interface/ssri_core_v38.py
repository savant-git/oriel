#!/usr/bin/env python3
"""
⬢ SSRI v38 — Gateway Auto-Reviver
Continuously ensures the Savant Gateway Flask service is running.
If port 8092 is unavailable, relaunches the gateway automatically.
"""
import time,subprocess,requests
from datetime import datetime,timezone
from pathlib import Path
LOG=Path.home()/ "savant/logs/gateway_reviver.log"

def log(m):
    LOG.parent.mkdir(parents=True,exist_ok=True)
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")

def alive():
    try:
        r=requests.get("http://127.0.0.1:8092",timeout=1)
        return r.status_code==200
    except Exception: return False

def restart():
    log("⚙️ Restarting Gateway on port 8092…")
    subprocess.Popen(["python3",str(Path.home()/ "savant/services/scripts/runtime_interface/ssri_core_v24.py")])

if __name__=="__main__":
    log("🧠 Gateway Auto-Reviver started.")
    while True:
        if not alive():
            log("❌ Gateway offline; restarting.")
            restart()
            time.sleep(10)
        else:
            log("✅ Gateway healthy.")
            time.sleep(60)


# Auto-completion safeguard
pass
