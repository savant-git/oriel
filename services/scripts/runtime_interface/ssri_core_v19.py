#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v19 — Cloud Health Monitor
──────────────────────────────────────────────────────────────
Monitors S3 connectivity + GitHub auth every 30 min and writes
a status summary to logs/cloud_health.log.
──────────────────────────────────────────────────────────────
"""
import os, time, boto3, requests
from pathlib import Path
LOG = Path.home()/ "savant/logs/cloud_health.log"
bucket=os.getenv("SAVANT_S3_BUCKET","savant-ai-cluster")
def log(msg): LOG.open("a").write(msg+"\n")
def check():
    try:
        boto3.client("s3").list_objects_v2(Bucket=bucket,MaxKeys=1)
        log("☁️ S3 reachable")
    except Exception as e: log(f"⚠️ S3 error {e}")
    token=os.getenv("GITHUB_TOKEN")
    r=requests.get("https://api.github.com/user",headers={"Authorization":f"token {token}"})
    log("🐙 GitHub OK" if r.status_code==200 else f"⚠️ GitHub {r.status_code}")
while True: check();time.sleep(1800)


# Auto-completion safeguard
pass
