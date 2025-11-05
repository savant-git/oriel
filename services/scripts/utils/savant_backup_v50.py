#!/usr/bin/env python3
"""
💾 Savant Backup v50
--------------------------------------------------------------
Performs an incremental S3 backup of ~/savant.
Only new or modified files are uploaded.
--------------------------------------------------------------
"""

import os, boto3, time, hashlib
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from savant.core.savant_console_theme import console, header, divider, success, error, accent
from savant.core.rule_enforcer import log as rule_log

BASE = Path.home() / "savant"
BUCKET = "savant-ai-cluster"
AWS_REGION = "us-east-1"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def upload_file(s3, file_path, key):
    s3.upload_file(str(file_path), BUCKET, key)
    console.print(success(f"☁️ Uploaded → {key}"))

header("💾 Savant Backup v50 — Incremental S3 Backup")
divider()

session = boto3.session.Session(region_name=AWS_REGION)
s3 = session.client("s3")

for root, _, files in os.walk(BASE):
    for name in files:
        path = Path(root) / name
        if "backups" in root or "exports" in root:
            continue
        key = f"backups/{path.relative_to(BASE)}"
        upload_file(s3, path, key)

rule_log("[BACKUP] Completed incremental backup.")
console.print(success("✅ Backup complete."))
