#!/usr/bin/env python3
"""
⬢ SSRI v43 — System Reinforcer
Watches all background daemons and relaunches any that stop unexpectedly.
"""
import subprocess, time, os
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home()/ "savant/logs/system_reinforcer.log"
DAEMONS = {
    "savant-supervisor": "Supervisor",
    "savant-sentinel": "Sentinel",
    "savant-health": "Health Monitor",
}

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def running(cmd):
    return any(cmd in l for l in os.popen("ps -ef").read().splitlines())

while True:
    for cmd, label in DAEMONS.items():
        if not running(cmd):
            log(f"⚠️ {label} offline — restarting.")
            subprocess.Popen(["bash", "-lc", cmd])
        else:
            log(f"✅ {label} active.")
    time.sleep(300)


# Auto-completion safeguard
pass
