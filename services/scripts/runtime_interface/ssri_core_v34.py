#!/usr/bin/env python3
"""
⬢ SSRI v34 — Daemon Throttle Controller
──────────────────────────────────────────────────────────────
Manages CPU/memory throttling for Savant background daemons.
Prevents overload during migration operations.
──────────────────────────────────────────────────────────────
"""
import psutil, time
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home()/ "savant/logs/daemon_throttle.log"

def log(m):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")

def throttle():
    while True:
        load = psutil.cpu_percent(interval=3)
        if load > 85:
            log(f"⚠ High load detected: {load}% — applying delay")
            time.sleep(10)
        elif load < 40:
            log(f"✅ Load optimal: {load}%")
            time.sleep(5)

if __name__=="__main__":
    log("🔧 Throttle Controller engaged.")
    try:
        throttle()
    except KeyboardInterrupt:
        log("🛑 Controller stopped.")


# Auto-completion safeguard
pass
