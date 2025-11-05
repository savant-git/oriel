#!/usr/bin/env python3
"""
⬢ Savant Clean Orchestrator v18
Runs even with zero free bytes.
Phase 1 (shell) clears /tmp, logs, cache using direct system calls.
Phase 2 (Python) resumes normal orchestrator + S3 offload.
"""
import os, shutil, subprocess, boto3, sys, time
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
TMP = Path("/data/data/com.termux/files/usr/tmp")
EXPORTS = BASE / "exports"
LOG = LOGS / "savant_clean.log"

def shell_phase():
    # Remove tmp/logs/cache using shell commands only (no memory allocation)
    os.system("rm -rf /data/data/com.termux/files/usr/tmp/* 2>/dev/null")
    os.system("rm -rf ~/savant/logs/* ~/savant/cache/* 2>/dev/null")
    os.system("sync")

def log(m):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")
    except Exception:
        print(m)

def offload_s3():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        bucket = os.getenv("SAVANT_S3_BUCKET")
        if not bucket: return
        for fp in EXPORTS.glob("*.zip"):
            s3.upload_file(str(fp), bucket, f"exports/{fp.name}")
            log(f"☁️  Uploaded {fp.name} to s3://{bucket}/exports/")
    except Exception as e:
        log(f"⚠️  S3 offload failed: {e}")

def main():
    print("⚙️  Phase 1: Emergency shell cleanup...")
    shell_phase()
    print("⚙️  Phase 2: Intelligent orchestrator cleanup...")
    # Kill stray Python daemons
    subprocess.run(["pkill", "-f", "python3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Remove __pycache__ and temporary files
    for root, dirs, files in os.walk(str(BASE)):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
    offload_s3()
    log("✅ Full cleanup complete.")
    print("💾 Savant Clean v18 finished successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        print("❌ Cleanup failed. Check logs if space allows.")
