#!/usr/bin/env python3
"""
⬢ SSRI v29.2 — Daemon Supervisor (Resilient Edition)
Launches gateway (v27) and sentinel (v28.2) with auto-log creation,
crash recovery, and periodic verification.
"""
import subprocess, time
from pathlib import Path
from datetime import datetime, timezone

LOG = Path.home()/ "savant/logs/daemon_supervisor.log"
GATEWAY = Path.home()/ "savant/services/scripts/runtime_interface/ssri_core_v27.py"
SENTINEL = Path.home()/ "savant/services/scripts/runtime_interface/ssri_core_v28.py"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def launch():
    procs = []
    for path in (GATEWAY, SENTINEL):
        try:
            p = subprocess.Popen(["python3", str(path)])
            procs.append(p)
            log(f"✅ Launched {path.name} (PID {p.pid})")
        except Exception as e:
            log(f"❌ Launch failed for {path}: {e}")
    return procs

if __name__ == "__main__":
    log("🧩 Supervisor initiated.")
    procs = launch()
    try:
        while True:
            time.sleep(60)
            for p in procs:
                if p.poll() is not None:
                    log(f"⚠️ Process {p.pid} exited — restarting.")
                    procs.remove(p)
                    procs += launch()
    except KeyboardInterrupt:
        for p in procs:
            p.terminate()
        log("🛑 Supervisor stopped gracefully.")


# Auto-completion safeguard
pass

# --- [2025-10-31 Environment Reset Hook] ---
import subprocess
def preflight_reset():
    try:
        subprocess.run(["bash",str(Path.home()/ "savant/services/scripts/utils/env_reset.sh")],check=True)
        log("🧹 Preflight reset executed before launch.")
    except Exception as e:
        log(f"⚠️ Preflight reset failed: {e}")

preflight_reset()
# --- End Reset Hook ---

# --- [2025-10-31 Environment Reset Hook] ---
import subprocess
def preflight_reset():
    try:
        subprocess.run(["bash",str(Path.home()/ "savant/services/scripts/utils/env_reset.sh")],check=True)
        log("🧹 Preflight reset executed before launch.")
    except Exception as e:
        log(f"⚠️ Preflight reset failed: {e}")

preflight_reset()
# --- End Reset Hook ---


# Auto-completion safeguard
pass
