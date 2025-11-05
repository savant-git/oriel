#!/usr/bin/env python3
"""
⬢ Savant v5.0 — Library Mirror
Compresses and mirrors site-packages to S3 to reclaim storage.
"""
import os, tarfile, boto3
from pathlib import Path
from datetime import datetime, timezone
import zstandard as zstd

LIB_PATH = Path("/data/data/com.termux/files/usr/lib/python3.12/site-packages")
ARCHIVE = Path.home()/f"savant/lib_mirror_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.zst"
LOG = Path.home()/ "savant/logs/lib_mirror.log"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def compress_libs():
    log(f"Compressing {LIB_PATH} → {ARCHIVE}")
    cctx = zstd.ZstdCompressor(level=10)
    with tarfile.open(fileobj=cctx.stream_writer(open(ARCHIVE,"wb")), mode="w|") as tar:
        tar.add(str(LIB_PATH), arcname="site-packages")
    log("✅ Compression complete")

def upload_to_s3():
    if not S3_BUCKET:
        log("⚠️ No S3 bucket configured.")
        return
    s3=boto3.client("s3")
    key=f"libraries/{ARCHIVE.name}"
    s3.upload_file(str(ARCHIVE),S3_BUCKET,key)
    log(f"☁️ Uploaded {ARCHIVE.name} → s3://{S3_BUCKET}/{key}")

def main():
    if LIB_PATH.exists():
        compress_libs()
        upload_to_s3()
        log("✅ Library mirror complete.")
    else:
        log("❌ Library path not found.")

if __name__=="__main__":
    main()
