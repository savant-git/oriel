from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
◆ Savant Export Cluster v4 — Chat Log + System Snapshot
────────────────────────────────────────────────────────
Creates a full archival package including chat logs,
source scripts, and environment state, with S3 upload.
────────────────────────────────────────────────────────
"""
import os, json, zipfile, zstandard, shutil, boto3
from pathlib import Path
from datetime import datetime, timezone

BASE   = Path.home()/ "savant"
EXPORTS= BASE/"exports"
LOGS   = BASE/"logs"
CHATLOG= LOGS/"chat_full.txt"
ENV    = BASE/".env"
ARCHIVE_NAME=f"savant_full_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def log(msg): console.print(msg)

def collect_chat_log():
    """
    Collect chat log from this entire conversation (from OpenAI)
    For now: use local `~/savant/logs/session_log.txt` if present
    or placeholder if none.
    """
    LOGS.mkdir(parents=True,exist_ok=True)
    src=LOGS/"session_log.txt"
    if src.exists():
        shutil.copy(src, CHATLOG)
        log(f"🗒  Chat log found and included.")
    else:
        CHATLOG.write_text("Chat log placeholder — full transcript pending import.\n")
        log(f"⚠️ No chat log file found; placeholder added.")

def create_zip():
    EXPORTS.mkdir(parents=True,exist_ok=True)
    zip_path=EXPORTS/f"{ARCHIVE_NAME}.zip"
    log(f"📦 Creating archive: {zip_path.name}")
    exclude=["__pycache__","node_modules",".git"]
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for path in BASE.rglob("*"):
            if any(x in str(path) for x in exclude): continue
            if path.is_file():
                rel=path.relative_to(BASE)
                zf.write(path,rel)
    log(f"✅ ZIP archive complete.")
    return zip_path

def compress_zst(zip_path:Path):
    zst_path=zip_path.with_suffix(".zip.zst")
    log(f"🧩 Compressing → {zst_path.name}")
    cctx=zstandard.ZstdCompressor(level=10)
    with open(zip_path,"rb") as f_in, open(zst_path,"wb") as f_out:
        f_out.write(cctx.compress(f_in.read()))
    log(f"✨ ZST compression complete — {zst_path.stat().st_size/1e6:.2f} MB")
    return zst_path

def copy_to_downloads(file:Path):
    target=Path.home()/ "storage/downloads"/file.name
    try:
        shutil.copy2(file,target)
        log(f"📥 Copied to Downloads → {target}")
    except Exception as e:
        log(f"⚠️ Could not copy to Downloads: {e}")

def upload_to_s3(file:Path):
    try:
        s3=boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        bucket=os.getenv("SAVANT_S3_BUCKET","savant-ai-cluster")
        key=f"exports/{file.name}"
        s3.upload_file(str(file),bucket,key)
        log(f"☁️ Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

def main():
    console.print(f"\n🧠 Starting Savant Export at {datetime.now(timezone.utc).isoformat()}")
    collect_chat_log()
    zip_path=create_zip()
    zst_path=compress_zst(zip_path)
    copy_to_downloads(zst_path)
    upload_to_s3(zst_path)
    console.print(f"\n✅ Export complete — {zst_path.name}")

if __name__=="__main__": main()


# Auto-completion safeguard
pass
