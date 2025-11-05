#!/usr/bin/env python3
import os, boto3, time
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
BUCKET = "savant-ai-cluster"
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
DEST_PREFIX = f"backups/{timestamp}/"

s3 = boto3.client("s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))

for fp in BASE.rglob("*"):
    if fp.is_file():
        key = DEST_PREFIX + str(fp.relative_to(BASE))
        try:
            s3.upload_file(str(fp), BUCKET, key)
            print(f"☁️ Uploaded {fp} → s3://{BUCKET}/{key}")
        except Exception as e:
            print(f"⚠️ Upload failed for {fp}: {e}")

print(f"✅ Backup complete — {BUCKET}/{DEST_PREFIX}")
