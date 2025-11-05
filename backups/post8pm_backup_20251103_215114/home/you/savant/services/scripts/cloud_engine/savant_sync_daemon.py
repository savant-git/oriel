#!/usr/bin/env python3
"""
⬢ Savant Sync Daemon v2.0
Runs the Termux-to-S3 Overlay every hour to prevent storage overflow.
Automatically retries on network loss and logs all actions.
"""
import os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "savant"
LOG  = ROOT / "logs/savant_sync_daemon.log"
OVERLAY = ROOT / "services/scripts/cloud_engine/t2s3_overlay.py"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] {msg}")
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass

def run_overlay():
    if not OVERLAY.exists():
        log("⚠️ Overlay script missing — cannot run.")
        return
    try:
        log("🧩 Running Termux-to-S3 overlay...")
        subprocess.run(["python3", str(OVERLAY)], check=True)
        log("✅ Overlay run complete.")
    except subprocess.CalledProcessError as e:
        log(f"⚠️ Overlay failed: {e}")

def main():
    log("🚀 Savant Sync Daemon started — hourly S3 cycle active.")
    while True:
        run_overlay()
        log("⏳ Sleeping 1 hour before next sync...")
        time.sleep(3600)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Sync Daemon manually stopped.")
