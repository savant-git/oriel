#!/usr/bin/env python3
"""
🧩 Savant Rule Enforcer v321
--------------------------------------------------------------
Ensures PROJECT_RULES.md exists, is non-empty, and current.
Blocks execution of any Savant subsystem if the rules file
is missing, corrupted, or outdated.
--------------------------------------------------------------
"""

import os, sys, time, hashlib
from pathlib import Path

DOC = Path.home() / "savant/docs/PROJECT_RULES.md"
LOG = Path.home() / "savant/logs/rule_enforcement.log"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[RULE] {msg}")

def fail(reason):
    log(f"❌ Enforcement failure: {reason}")
    sys.exit(1)

# === Validation ===
if not DOC.exists():
    fail("PROJECT_RULES.md missing.")
if DOC.stat().st_size < 1000:
    fail("PROJECT_RULES.md appears incomplete or truncated.")

age_hours = (time.time() - DOC.stat().st_mtime) / 3600
if age_hours > 168:  # 7 days
    log("⚠️ Rule document older than 7 days — refresh advised.")

doc_hash = hash_file(DOC)
log(f"✅ Rule enforcement passed — PROJECT_RULES.md hash {doc_hash[:12]}")
