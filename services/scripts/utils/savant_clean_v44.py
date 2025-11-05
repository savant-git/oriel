from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧹 Savant Clean v44 — Safe Cleanup
"""
import os, shutil
from pathlib import Path

BASE = Path.home() / "savant"
SAFE_DIRS = {"exports", "backups", "logs", "chat_logs"}

def log(msg): console.print(msg)

def main():
    log("🧹 Cleaning temp & cache files safely...")
    for root, dirs, files in os.walk(BASE):
        for f in files:
            path = Path(root)/f
            if any(d in path.parts for d in SAFE_DIRS): continue
            if path.suffix in [".tmp",".bak",".cache"]: path.unlink(missing_ok=True)
    log("✅ Cleanup complete. No core libraries touched.")

if __name__ == "__main__":
    main()
