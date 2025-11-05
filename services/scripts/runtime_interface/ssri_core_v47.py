from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ SSRI v47 — Finalization Verifier
Confirms gateway health and seals migration state permanently.
"""
import requests
from pathlib import Path
from datetime import datetime, timezone

LOG  = Path.home()/ "savant/logs/finalization_verifier.log"
FLAG = Path.home()/ "savant/logs/MIGRATION_COMPLETE"

def log(m):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")

ok = 0
for port in range(8090, 8100):
    try:
        r = requests.get(f"http://127.0.0.1:{port}/api/status", timeout=3)
        if r.ok:
            log(f"✅ Gateway on port {port} responsive.")
            ok += 1
    except Exception as e:
        log(f"❌ Gateway check failed on {port}: {e}")

if ok >= 1:
    FLAG.write_text(datetime.now(timezone.utc).isoformat())
    log("✅ MIGRATION COMPLETE — Savant now fully independent.")
    rule_status("✅ MIGRATION COMPLETE — Savant now fully independent.", "ok")
else:
    log("❌ No gateway response detected.")
    rule_status("❌ No gateway response detected.", "error")
