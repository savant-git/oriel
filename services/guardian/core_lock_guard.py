#!/usr/bin/env python3
"""
⬢ Savant Core-Lock Guardian
Protects verified scripts and creates immutable snapshots before modification.
"""
import os, shutil, stat
from datetime import datetime
from pathlib import Path

BASE = Path.home() / "savant"
CORE = BASE / "core"
SERVICES = BASE / "services/scripts"

def lock_core():
    CORE.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = CORE / f"snapshot_{ts}"
    for script in SERVICES.rglob("*.py"):
        rel = script.relative_to(SERVICES)
        dest = snap / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(script, dest)
        os.chmod(dest, stat.S_IREAD)
    print(f"✅ Core snapshot created → {snap}")

if __name__ == "__main__":
    lock_core()
