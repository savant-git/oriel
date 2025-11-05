#!/usr/bin/env python3
"""
🧠 Savant Clean Complete (Legacy Integration)
Timestamp: 2025-10-31T00:00Z
Preserved from v3.5; orchestrates export cleanup and cloud sync.
"""
import os, boto3
from pathlib import Path
from datetime import datetime, timedelta, timezone

BASE = Path.home()/"savant"
EXPORTS = BASE/"exports"
LOG = BASE/"logs/clean_complete.log"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def remove_old_exports(days=10):
    if not EXPORTS.exists(): return
    cutoff = datetime.now() - timedelta(days=days)
    for f in EXPORTS.glob("*"):
        if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            log(f"🗑️ Removing old export: {f}")
            try: f.unlink()
            except Exception as e: log(f"⚠️ Could not delete {f}: {e}")

def sync_to_s3():
    if not S3_BUCKET: return
    s3 = boto3.client("s3")
    for f in EXPORTS.glob("*.zip*"):
        try:
            key = f"exports/{f.name}"
            s3.upload_file(str(f), S3_BUCKET, key)
            log(f"☁️ Uploaded {f} → s3://{S3_BUCKET}/{key}")
        except Exception as e:
            log(f"⚠️ Upload failed for {f}: {e}")

def main():
    log("🧠 Starting legacy export cleanup")
    remove_old_exports()
    sync_to_s3()
    log("✅ Legacy cleanup complete.")

if __name__ == "__main__":
    main()
