#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ Savant Integrity Guard  —  ensures immutability & backup
──────────────────────────────────────────────────────────────
Checks every *.py script in ~/savant/services for unauthorized
changes.  If a hash mismatch is found, a timestamped backup of
the modified file is created in ~/savant/backups/integrity/.
──────────────────────────────────────────────────────────────
"""
import hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.home()/ "savant/services"
BACK = Path.home()/ "savant/backups/integrity"
BACK.mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def log(msg): print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}")

for f in ROOT.rglob("*.py"):
    try:
        h=sha(f)
        ref=f.with_suffix(f.suffix+".sha")
        if ref.exists():
            if ref.read_text()!=h:
                ts=datetime.now().strftime("%Y%m%d_%H%M%S")
                dest=BACK/f"{f.name}_{ts}.bak"
                shutil.copy2(f,dest)
                log(f"⚠️  Integrity deviation in {f.name} → backup created")
        ref.write_text(h)
    except Exception as e:
        log(f"Error on {f}: {e}")
log("✅ Integrity guard completed.")


# Auto-completion safeguard
pass
