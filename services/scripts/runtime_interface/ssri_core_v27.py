#!/usr/bin/env python3
"""
⬢ SSRI v27 — Adaptive Port Harness
──────────────────────────────────────────────────────────────
Runs all sub-servers (v22–v25) but dynamically rebinds any port
that’s already in use.  Logs each service’s bound address.
──────────────────────────────────────────────────────────────
"""
import socket,subprocess,time,os
from pathlib import Path
from datetime import datetime,timezone

LOG = Path.home()/ "savant/logs/server_harness.log"
def log(msg):
    LOG.parent.mkdir(parents=True,exist_ok=True)
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def free_port(start):
    for p in range(start, start+10):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1",p));s.close();return p
        except OSError: pass
    raise SystemExit("❌ No free port in range.")

MODULES=[
 ("runtime_interface/ssri_core_v22.py",8090),
 ("runtime_interface/ssri_core_v23.py",8091),
 ("runtime_interface/ssri_core_v24.py",8092),
 ("runtime_interface/ssri_core_v25.py",8093)
]

def run_all():
    log("🚀 SSRI v27 adaptive harness starting...")
    procs=[]
    for m,base in MODULES:
        port=free_port(base)
        log(f"Launching {m} on port {port}")
        env=os.environ.copy()
        env["SAVANT_PORT"]=str(port)
        p=subprocess.Popen(["python3",str(Path.home()/ "savant/services/scripts"/ m)],env=env)
        procs.append(p)
        time.sleep(1)
    log("✅ All sub-servers launched with adaptive binding.")
    for p in procs: p.wait()

if __name__=="__main__":
    try: run_all()
    except KeyboardInterrupt: log("🛑 Adaptive harness stopped.")


# Auto-completion safeguard
pass
