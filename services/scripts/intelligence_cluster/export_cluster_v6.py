from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v6.0
Full intelligent export with:
 • Chat log capture
 • ZIP + Zstandard compression
 • Save to Downloads
 • Upload to S3
 • GitHub sync (commit + push)
Optimized to skip large dirs and broken symlinks.
"""
import os, sys, zipfile, boto3, shutil, subprocess, time, json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home()/ "savant"
EXPORTS = BASE/"exports"
LOGS = BASE/"logs"
DOWNLOADS = Path.home()/ "storage/downloads"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")
GITHUB_URL = "https://github.com/flypaper-creative/savant.git"
CHAT_LOG = BASE/"logs/chat_full_log.txt"
LOG_PATH = LOGS/"export_cluster_v6.log"

# ------------------- Logging -------------------
def log(msg):
    LOGS.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

# ------------------- Chat Log -------------------
def capture_chat_log():
    try:
        src = BASE/"services"/"scripts"/"intelligence_cluster"/"chat_log_ingestor.py"
        if src.exists():
            subprocess.run(["python3", str(src)], check=False)
        if CHAT_LOG.exists():
            log("🗒  Chat log found and included.")
        else:
            CHAT_LOG.write_text("(no chat log found)")
            log("⚠️  Chat log placeholder created.")
    except Exception as e:
        log(f"⚠️  Chat log capture failed: {e}")

# ------------------- ZIP Creation -------------------
def create_archive():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = EXPORTS/f"savant_full_export_{ts}.zip"
    log(f"📦 Creating archive: {zip_path.name}")
    safe_roots = ["services", "docs", "logs", "registry"]
    skip_dirs = {"node_modules","__pycache__","usr",".git",".cache","tmp"}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root in safe_roots:
            d = BASE/root
            if not d.exists(): continue
            for path in d.rglob("*"):
                if any(s in path.parts for s in skip_dirs): continue
                if not path.is_file(): continue
                rel = path.relative_to(BASE)
                try:
                    zf.write(path, rel)
                except Exception as e:
                    log(f"⚠️  Skipped {path}: {e}")
    return zip_path

# ------------------- ZST Compression -------------------
def compress_zst(zip_path):
    import zstandard as zstd
    zst_path = zip_path.with_suffix(".zip.zst")
    log(f"🧩 Compressing → {zst_path.name}")
    try:
        cctx = zstd.ZstdCompressor(level=7)
        with open(zip_path, "rb") as f_in, open(zst_path, "wb") as f_out:
            cctx.copy_stream(f_in, f_out)
        log(f"✅ ZST compression complete → {zst_path}")
        zip_path.unlink(missing_ok=True)
        return zst_path
    except Exception as e:
        log(f"⚠️ Compression failed: {e}")
        return zip_path

# ------------------- Copy to Downloads -------------------
def copy_to_downloads(path):
    try:
        DOWNLOADS.mkdir(parents=True, exist_ok=True)
        target = DOWNLOADS / path.name
        shutil.copy2(path, target)
        log(f"📥 Copied to Downloads → {target}")
    except Exception as e:
        log(f"⚠️ Copy failed: {e}")

# ------------------- Upload to S3 -------------------
def upload_to_s3(path):
    if not S3_BUCKET: 
        log("⚠️ No S3 bucket configured.")
        return
    try:
        s3 = boto3.client("s3")
        key = f"exports/{path.name}"
        s3.upload_file(str(path), S3_BUCKET, key)
        log(f"☁️ Uploaded {path.name} → s3://{S3_BUCKET}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

# ------------------- Push to GitHub -------------------
def push_to_github():
    try:
        subprocess.run(["git", "-C", str(BASE), "add", "."], check=False)
        subprocess.run(["git", "-C", str(BASE), "commit", "-m", f"Automated export {datetime.now().isoformat()}"], check=False)
        subprocess.run(["git", "-C", str(BASE), "push", "origin", "main"], check=False)
        log("🐙 GitHub sync complete.")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

# ------------------- Main -------------------
def main():
    log(f"🧠 Starting Savant Export at {datetime.now(timezone.utc).isoformat()}")
    capture_chat_log()
    zip_path = create_archive()
    zst_path = compress_zst(zip_path)
    copy_to_downloads(zst_path)
    upload_to_s3(zst_path)
    push_to_github()
    log("✅ Savant Export v6.0 complete.")

if __name__ == "__main__":
    main()
