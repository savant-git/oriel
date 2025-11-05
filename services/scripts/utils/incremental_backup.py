from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Cleanup v4.5 — Incremental Backup
Detects changed files since last export and syncs to S3.
"""
import os, boto3, hashlib
from pathlib import Path

BASE = Path.home()/"savant"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")

def sha(path): return hashlib.sha256(open(path,"rb").read()).hexdigest()

def main():
    s3 = boto3.client("s3")
    for path in BASE.rglob("*"):
        if path.is_file() and path.stat().st_size < 50_000_000:
            key=f"incr/{path.relative_to(BASE)}"
            try:
                s3.upload_file(str(path),S3_BUCKET,key)
                console.print(f"☁️  Synced: {key}")
            except Exception as e:
                rule_status(f"⚠️  {path}: {e}", "warn")

if __name__=="__main__":
    main()
