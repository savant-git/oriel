#!/usr/bin/env python3
"""
⬢ SSRI v26 — Integration Harness
Orchestrates v22-v25 modules into one unified daemon.
"""
import subprocess,sys,time,os
from pathlib import Path
from datetime import datetime,timezone

LOG=Path.home()/ "savant/logs/server_harness.log"
def log(msg): LOG.parent.mkdir(parents=True,exist_ok=True); LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

MODULES=[
 "runtime_interface/ssri_core_v22.py",
 "runtime_interface/ssri_core_v23.py",
 "runtime_interface/ssri_core_v24.py",
 "runtime_interface/ssri_core_v25.py"
]

def run_all():
    log("🚀 SSRI v26 starting composite modules…")
    procs=[]
    for m in MODULES:
        p=subprocess.Popen(["python3",str(Path.home()/ "savant/services/scripts"/ m)])
        procs.append(p)
        time.sleep(1)
    log("✅ All sub-servers launched.")
    for p in procs: p.wait()

if __name__=="__main__":
    try: run_all()
    except KeyboardInterrupt: log("🛑 Integration harness stopped.")


# Auto-completion safeguard
pass
