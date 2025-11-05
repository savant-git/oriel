from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive-Export v201 — Indestructible Diagnostic Edition
Always prints progress, errors, and system diagnostics even on low-space or import failure.
"""

import sys, os, traceback
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS / "archive_export_v201.log"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    out = f"[{ts}] {msg}"
    console.print(out, flush=True)
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(out + "\n")
    except Exception:
        pass  # even if disk full, don’t die

log("🧠 Starting Savant Archive-Export v201 diagnostics...")

try:
    import re, json, zipfile, shutil, subprocess, html
    try:
        import boto3
    except Exception as e:
        log(f"⚠️ boto3 missing: {e}")
    from datetime import timedelta
    log("✅ Imports loaded successfully.")
except Exception as e:
    log(f"❌ Import failure: {e}")
    traceback.print_exc()
    sys.exit(1)

SRC = Path("/storage/emulated/0/Download/conversations.json")
if not SRC.exists():
    log(f"❌ conversations.json not found at {SRC}")
    sys.exit(1)

try:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    log(f"✅ Parsed conversations.json ({len(data)} conversations)")
except Exception as e:
    log(f"❌ Failed to read/parse conversations.json: {e}")
    traceback.print_exc()
    sys.exit(1)

# Simple confirmation output
CHAT_DIR = BASE / "chat_logs"
CHAT_DIR.mkdir(parents=True, exist_ok=True)
out = CHAT_DIR / "chat_diagnostic_test.html"
out.write_text("<html><body><h1>Savant Export Diagnostic OK</h1></body></html>", encoding="utf-8")
log(f"✅ Diagnostic HTML written → {out}")

log("🏁 Savant Archive-Export v201 finished successfully.")
