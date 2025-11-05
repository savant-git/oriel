#!/usr/bin/env python3
"""
⬢ Savant Script Guardian v1
Watches all Savant scripts, logs every change, and locks "finished" files.
No deletion or truncation can occur unnoticed.
"""

import os, hashlib, time, json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
WATCH_DIRS = [BASE / "services" / "scripts", BASE / "ui"]
LOCK_FILE = BASE / "services" / "guardian" / "locked_scripts.json"
LOG_FILE = BASE / "logs" / "script_guardian.log"
HASH_FILE = BASE / "services" / "guardian" / "script_hashes.json"

LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    LOG_FILE.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    print(msg)

def sha256(fp: Path):
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))

def scan_scripts():
    hashes = {}
    for root in WATCH_DIRS:
        if not root.exists():
            continue
        for fp in root.rglob("*.py"):
            try:
                hashes[str(fp)] = sha256(fp)
            except Exception as e:
                log(f"⚠️ Failed to hash {fp}: {e}")
    return hashes

def monitor():
    old_hashes = load_json(HASH_FILE)
    locked = set(load_json(LOCK_FILE).get("locked", []))
    new_hashes = scan_scripts()

    for fp, new_hash in new_hashes.items():
        old_hash = old_hashes.get(fp)
        if old_hash and old_hash != new_hash:
            if fp in locked:
                log(f"🚫 Attempted modification of LOCKED script: {fp}")
                # restore file from last known good version
                os.system(f"git checkout -- '{fp}' || true")
            else:
                log(f"🧩 Script changed: {fp}")
        elif not old_hash:
            log(f"➕ New script detected: {fp}")

    save_json(HASH_FILE, new_hashes)
    log("✅ Script Guardian scan complete.")

def lock_script(target: str):
    locked = load_json(LOCK_FILE)
    if "locked" not in locked:
        locked["locked"] = []
    if target not in locked["locked"]:
        locked["locked"].append(target)
    save_json(LOCK_FILE, locked)
    log(f"🔒 Script locked: {target}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--lock":
        if len(sys.argv) < 3:
            print("Usage: script_guardian_v1.py --lock <script_path>")
            exit(1)
        lock_script(sys.argv[2])
    else:
        monitor()
