from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
📦 Savant Export v191 — Stable + Clean Output
Packages Savant files and pushes to S3 and GitHub.
"""
import os, subprocess, zipfile, boto3
from datetime import datetime
from pathlib import Path

BASE = Path.home() / "savant"
EXPORTS = BASE / "exports"
EXPORTS.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ARCHIVE = EXPORTS / f"savant_full_export_{timestamp}.zip"

def log(msg): console.print(f"[{datetime.now():%H:%M:%S}] {msg}")

def create_zip():
    log("📦 Creating archive...")
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(BASE):
            for file in files:
                if "backups" not in root:
                    path = Path(root)/file
                    arc = path.relative_to(BASE)
                    zipf.write(path, arc)
    log(f"✅ Archive created: {ARCHIVE}")

def upload_s3():
    try:
        log("☁️ Uploading to S3...")
        s3 = boto3.client("s3")
        bucket = "savant-ai-cluster"
        s3.upload_file(str(ARCHIVE), bucket, f"exports/{ARCHIVE.name}")
        log("✅ Uploaded to S3 successfully.")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

def push_github():
    try:
        log("🔄 Syncing to GitHub...")
        subprocess.run(["git","-C",str(BASE),"add","exports"], check=True)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Export {ARCHIVE.name}"], check=False)
        subprocess.run(["git","-C",str(BASE),"pull","--rebase","origin","main"], check=False)
        subprocess.run(["git","-C",str(BASE),"push","origin","main"], check=True)
        log("✅ GitHub sync complete.")
    except Exception as e:
        log(f"⚠️ GitHub sync failed: {e}")

if __name__ == "__main__":
    create_zip()
    upload_s3()
    push_github()
    log("🏁 Export complete.")
