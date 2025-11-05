#!/usr/bin/env python3
"""
⬢ SSRI v46 — Gateway Launcher
Launches the new unified gateway core as a background service.
"""
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home()/ "savant/logs/gateway_unified.log"
def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

log("🚀 Launching unified gateway core (v45)...")
subprocess.Popen(["python3", str(Path.home()/ "savant/services/scripts/runtime_interface/ssri_core_v45.py")])
log("✅ Unified gateway core launched.")
