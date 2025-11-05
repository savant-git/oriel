from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
◆ Savant Export Cluster v5 — Unified Cloud + GitHub + Chat Export
──────────────────────────────────────────────────────────────────────
• Retains prior export logic (v3, v4) in commented sections (dated).
• Adds GitHub auto-commit and remote push.
• Includes chat log ingestion, S3 upload, and Downloads copy.
──────────────────────────────────────────────────────────────────────
"""

import os, json, zipfile, shutil, zstandard, subprocess, boto3
from pathlib import Path
from datetime import datetime, timezone

# ================================================================
# Core Paths
# ================================================================
BASE   = Path.home()/ "savant"
EXPORTS= BASE/"exports"
LOGS   = BASE/"logs"
CHATLOG= LOGS/"chat_full.txt"
ENV    = BASE/".env"
ARCHIVE_NAME=f"savant_full_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BUCKET=os.getenv("SAVANT_S3_BUCKET","savant-ai-cluster")

def log(msg): console.print(msg)

# ================================================================
# [2025-10-31T02:00:00Z] — v4 legacy preserved
# (basic archive without GitHub integration)
# ================================================================
# def create_zip_legacy():
#     ...
#     return zip_path
# Reason replaced: lacked GitHub + chat ingestion

# ================================================================
# v5: Active logic
# ================================================================
def collect_chat_log():
    """Locate or create full chat transcript."""
    LOGS.mkdir(parents=True, exist_ok=True)
    src=LOGS/"session_log.txt"
    if src.exists():
        shutil.copy(src, CHATLOG)
        log("🗒  Chat log found and included.")
    else:
        CHATLOG.write_text("⚠ Chat log placeholder — full transcript pending import.\n")
        log("⚠ No chat log found; placeholder created.")

def create_zip():
    EXPORTS.mkdir(parents=True, exist_ok=True)
    zip_path=EXPORTS/f"{ARCHIVE_NAME}.zip"
    log(f"📦 Creating archive: {zip_path.name}")
    exclude=["__pycache__","node_modules",".git",".zst"]
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for path in BASE.rglob("*"):
            if any(x in str(path) for x in exclude): continue
            if path.is_file(): zf.write(path, path.relative_to(BASE))
    log("✅ ZIP archive complete.")
    return zip_path

def compress_zst(zip_path:Path):
    zst_path=zip_path.with_suffix(".zip.zst")
    log(f"🧩 Compressing → {zst_path.name}")
    cctx=zstandard.ZstdCompressor(level=10)
    with open(zip_path,"rb") as f_in, open(zst_path,"wb") as f_out:
        shutil.copyfileobj(cctx.stream_reader(f_in), f_out)
    log(f"✨ ZST compression complete — {(zst_path.stat().st_size/1e6):.2f} MB")
    return zst_path

def copy_to_downloads(file:Path):
    target=Path.home()/ "storage/downloads"/file.name
    try:
        shutil.copy2(file,target)
        log(f"📥 Copied to Downloads → {target}")
    except Exception as e:
        log(f"⚠ Could not copy to Downloads: {e}")

def upload_to_s3(file:Path):
    try:
        s3=boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        key=f"exports/{file.name}"
        s3.upload_file(str(file),BUCKET,key)
        log(f"☁️ Uploaded to s3://{BUCKET}/{key}")
    except Exception as e:
        log(f"⚠ S3 upload failed: {e}")

def push_to_github(file:Path):
    """Auto-commit and push latest export to GitHub."""
    try:
        repo=BASE
        log("🐙 Committing export to GitHub...")
        subprocess.run(["git","-C",str(repo),"add","-A"],check=True)
        subprocess.run(["git","-C",str(repo),"commit","-m",
            f"Automated export {datetime.now(timezone.utc).isoformat()}"],check=False)
        subprocess.run(["git","-C",str(repo),"push","origin","main","--force"],check=False)
        log("✅ GitHub push complete.")
    except Exception as e:
        log(f"⚠ GitHub push failed: {e}")

def main():
    console.print(f"\n🧠 Starting Savant Export at {datetime.now(timezone.utc).isoformat()}")
    collect_chat_log()
    zip_path=create_zip()
    zst_path=compress_zst(zip_path)
    copy_to_downloads(zst_path)
    upload_to_s3(zst_path)
    push_to_github(zst_path)
    console.print(f"\n✅ Export complete — {zst_path.name}")

if __name__=="__main__":
    main()


# Auto-completion safeguard
pass
