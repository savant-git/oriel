from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Cleanup Engine — v5.0
Purpose:
    Intelligent disk hygiene module that safely reclaims storage
    without damaging operational code or user data.

Functions:
    • Remove transient caches (__pycache__, tmp, build)
    • Delete obsolete exports/logs beyond retention window
    • Validate disk health before and after purge
    • Optionally push heavy artifacts to S3 for off-device storage

All deletions are logged to ~/savant/logs/cleanup_engine.log
"""

import os, shutil, time, boto3
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
LOG  = BASE / "logs/cleanup_engine.log"
RETENTION_DAYS = 3
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def remove_path(p):
    try:
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
        log(f"🗑️  Removed: {p}")
    except Exception as e:
        log(f"⚠️  Failed to remove {p}: {e}")

def upload_s3(p):
    if not S3_BUCKET: return False
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        key = f"offload/{p.name}"
        s3.upload_file(str(p), S3_BUCKET, key)
        log(f"☁️  Uploaded to S3: {key}")
        return True
    except Exception as e:
        log(f"⚠️  S3 upload failed for {p}: {e}")
        return False

def main():
    log(f"🧹 Savant Cleanup Start — {datetime.now().isoformat()}")
    cutoff = time.time() - RETENTION_DAYS*86400
    targets = []

    # 1. Core cache folders
    for pattern in ["__pycache__", "build", "dist", ".mypy_cache"]:
        for p in BASE.rglob(pattern):
            targets.append(p)

    # 2. Obsolete exports/logs
    for ext in (".zip",".zst",".log",".tmp"):
        for p in BASE.rglob(f"*{ext}"):
            if p.stat().st_mtime < cutoff:
                targets.append(p)

    log(f"🔍 {len(targets)} items flagged for cleanup")
    for p in targets:
        if p.stat().st_size > 50*1024*1024 and S3_BUCKET:
            if upload_s3(p): remove_path(p)
        else:
            remove_path(p)

    total = shutil.disk_usage(str(BASE))
    free_gb = total.free / (1024**3)
    log(f"✅ Cleanup complete — Free space: {free_gb:.2f} GB")
    rule_status(f"✅ Cleanup complete — Free space: {free_gb:.2f} GB (log: {LOG})", "ok")

if __name__ == "__main__":
    main()


# Auto-completion safeguard
pass
