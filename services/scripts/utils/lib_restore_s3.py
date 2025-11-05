from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Cleanup v4.1 — Library Restore from S3
Restores mirrored site-packages from the S3 archive when needed.
"""
import os, boto3, tarfile, zstandard as zstd
from pathlib import Path

LIB_PATH = Path("/data/data/com.termux/files/usr/lib/python3.12/site-packages")
RESTORE_DIR = LIB_PATH.parent/"restored"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")

def restore_latest():
    s3 = boto3.client("s3")
    objs = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="libraries/").get("Contents", [])
    if not objs:
        rule_status("⚠️  No backups found.", "warn")
        return
    latest = sorted(objs, key=lambda x: x["LastModified"], reverse=True)[0]["Key"]
    file = Path("/tmp")/Path(latest).name
    s3.download_file(S3_BUCKET, latest, str(file))
    console.print(f"⬇️ Downloaded {latest}")
    dctx = zstd.ZstdDecompressor()
    with tarfile.open(fileobj=dctx.stream_reader(open(file, "rb")), mode="r|") as tar:
        tar.extractall(str(RESTORE_DIR))
    rule_status(f"✅ Restored to {RESTORE_DIR}", "ok")

if __name__ == "__main__":
    restore_latest()
