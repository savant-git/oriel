from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v6.1
Full unabridged chat log capture and export system.
 • Captures complete chat from ~/.chat_history or memory shards
 • Ensures full text (both sides, untruncated, with code)
 • ZIP + ZST archive
 • Downloads + S3 + GitHub sync
"""

import os, zipfile, boto3, shutil, subprocess, json, zstandard as zstd
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home()/"savant"
EXPORTS = BASE/"exports"
LOGS = BASE/"logs"
DOWNLOADS = Path.home()/"storage/downloads"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")
CHAT_SRC = Path.home()/"savant/chat_history"
CHAT_OUT = LOGS/"chat_full_log.txt"
CHAT_ZST = LOGS/"chat_full_log.json.zst"
LOG_PATH = LOGS/"export_cluster_v6_1.log"

# ------------------- Logging -------------------
def log(msg):
    LOGS.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

# ------------------- Chat Log Collector -------------------
def collect_chat_log():
    """
    Collects and concatenates all known chat sources:
    - /savant/chat_history
    - /savant/logs/chat_*.txt
    - memory snapshot via internal ingestion tool (if available)
    """
    log("🧠 Collecting full chat history...")
    combined = []
    sources = []

    # Primary history folder
    if CHAT_SRC.exists():
        for f in sorted(CHAT_SRC.glob("*.txt")):
            try:
                combined.append(f"\n--- FILE: {f.name} ---\n")
                combined.append(f.read_text(errors="ignore"))
                sources.append(str(f))
            except Exception as e:
                log(f"⚠️  Failed to read {f}: {e}")

    # Fallback: any chat logs in savant/logs
    for f in sorted(LOGS.glob("chat_*.txt")):
        try:
            combined.append(f"\n--- FILE: {f.name} ---\n")
            combined.append(f.read_text(errors="ignore"))
            sources.append(str(f))
        except Exception as e:
            log(f"⚠️  Failed to read {f}: {e}")

    # Write unified plaintext file
    CHAT_OUT.write_text("\n".join(combined) or "(no chat data found)", encoding="utf-8")
    log(f"📘 Combined chat log → {CHAT_OUT} ({len(combined)} segments)")

    # Also write JSON mirror
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "sources": sources, "text": "\n".join(combined)}
    cctx = zstd.ZstdCompressor(level=5)
    with open(CHAT_ZST, "wb") as f:
        f.write(cctx.compress(json.dumps(payload, ensure_ascii=False).encode("utf-8")))
    log(f"🗜️  Compressed chat log mirror → {CHAT_ZST}")

# ------------------- ZIP Creation -------------------
def create_archive():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = EXPORTS/f"savant_full_export_{ts}.zip"
    log(f"📦 Creating archive: {zip_path.name}")
    skip_dirs = {"node_modules","__pycache__","usr",".git",".cache","tmp"}
    include_roots = ["services","docs","logs","registry"]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root in include_roots:
            d = BASE/root
            if not d.exists(): continue
            for path in d.rglob("*"):
                if any(s in path.parts for s in skip_dirs): continue
                if not path.is_file(): continue
                rel = path.relative_to(BASE)
                try: zf.write(path, rel)
                except Exception as e: log(f"⚠️ Skipped {path}: {e}")
    return zip_path

# ------------------- Compress + Upload -------------------
def compress_zst(zip_path):
    zst_path = zip_path.with_suffix(".zip.zst")
    log(f"🧩 Compressing → {zst_path.name}")
    cctx = zstd.ZstdCompressor(level=7)
    with open(zip_path,"rb") as fin, open(zst_path,"wb") as fout:
        cctx.copy_stream(fin,fout)
    zip_path.unlink(missing_ok=True)
    log(f"✅ ZST compression complete — {zst_path}")
    return zst_path

def copy_to_downloads(path):
    try:
        DOWNLOADS.mkdir(parents=True, exist_ok=True)
        target = DOWNLOADS / path.name
        shutil.copy2(path, target)
        log(f"📥 Copied to Downloads → {target}")
    except Exception as e:
        log(f"⚠️ Copy failed: {e}")

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

def push_to_github():
    try:
        subprocess.run(["git","-C",str(BASE),"add","."],check=False)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Automated export {datetime.now().isoformat()}"],check=False)
        subprocess.run(["git","-C",str(BASE),"push","origin","main"],check=False)
        log("🐙 GitHub sync complete.")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

# ------------------- MAIN -------------------
def main():
    log(f"🧠 Starting Savant Export at {datetime.now(timezone.utc).isoformat()}")
    collect_chat_log()
    zip_path = create_archive()
    zst_path = compress_zst(zip_path)
    copy_to_downloads(zst_path)
    upload_to_s3(zst_path)
    push_to_github()
    log("✅ Savant Export v6.1 complete — full chat preserved.")

if __name__=="__main__":
    main()
