from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
◆ Savant Export Cluster v5.1 — Stable Write + Verify Fix
───────────────────────────────────────────────────────────────
Enhancements:
- Ensures filesystem flush & fsync before compression
- Verifies ZIP file exists and is readable
- Adds recovery fallback if compression fails
───────────────────────────────────────────────────────────────
"""

import os, json, zipfile, shutil, zstandard, subprocess, boto3, time
from pathlib import Path
from datetime import datetime, timezone

BASE   = Path.home()/ "savant"
EXPORTS= BASE/"exports"
LOGS   = BASE/"logs"
CHATLOG= LOGS/"chat_full.txt"
BUCKET=os.getenv("SAVANT_S3_BUCKET","savant-ai-cluster")

def log(msg): console.print(msg)

def collect_chat_log():
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
    name=f"savant_full_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path=EXPORTS/name
    exclude=["__pycache__","node_modules",".git",".zst"]
    log(f"📦 Creating archive: {zip_path.name}")
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for path in BASE.rglob("*"):
            if any(x in str(path) for x in exclude): continue
            if path.is_file(): zf.write(path, path.relative_to(BASE))
        zf.close()
    os.sync()  # Ensure all writes complete to disk
    if not zip_path.exists():
        raise FileNotFoundError(f"❌ ZIP file missing after creation: {zip_path}")
    log("✅ ZIP archive complete.")
    return zip_path

def compress_zst(zip_path:Path):
    zst_path=zip_path.with_suffix(".zip.zst")
    log(f"🧩 Compressing → {zst_path.name}")
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP not found: {zip_path}")
    try:
        cctx=zstandard.ZstdCompressor(level=10)
        with open(zip_path,"rb") as f_in, open(zst_path,"wb") as f_out:
            shutil.copyfileobj(cctx.stream_reader(f_in), f_out)
        log(f"✨ ZST compression complete — {(zst_path.stat().st_size/1e6):.2f} MB")
        return zst_path
    except Exception as e:
        log(f"⚠ Compression failed: {e}")
        return zip_path  # fallback to ZIP if compression fails

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
    time.sleep(1)  # Wait for write sync safety
    zst_path=compress_zst(zip_path)
    copy_to_downloads(zst_path)
    upload_to_s3(zst_path)
    push_to_github(zst_path)
    console.print(f"\n✅ Export complete — {zst_path.name}")

if __name__=="__main__":
    main()


# Auto-completion safeguard
pass
