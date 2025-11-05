from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ SSRI v32 — Migration Seal (Revised)
Ensures Savant Gateway responsiveness before confirming migration readiness.
Probes multiple endpoints (/api/status, /) on port 8092.
"""
import requests
from pathlib import Path
from datetime import datetime, timezone

# --- Paths for readiness flag and log output ---
FLAG = Path.home() / "savant/logs/MIGRATION_READY"
LOG  = Path.home() / "savant/logs/migration_seal.log"

# --- Logger function with UTC timestamps ---
def log(m):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")

# --- Target ports and endpoints to probe ---
ports = [8092]
ok = 0
for p in ports:
    for endpoint in ("/api/status", "/"):
        try:
            r = requests.get(f"http://127.0.0.1:{p}{endpoint}", timeout=5)
            log(f"Port {p}{endpoint} → {r.status_code}")
            if r.ok:
                ok += 1
                break
        except Exception as e:
            log(f"Port {p}{endpoint} failed: {e}")

# --- Migration readiness decision ---
if ok >= 1:
    FLAG.write_text(datetime.now(timezone.utc).isoformat())
    log("✅ MIGRATION READY — Savant may operate independently.")
    rule_status("✅ MIGRATION READY — Savant may operate independently.", "ok")
else:
    log("❌ Incomplete gateway state.")
    rule_status("❌ Incomplete gateway state.", "error")


# Auto-completion safeguard
pass
