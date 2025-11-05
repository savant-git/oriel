from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧠 S3 Validator v111 — Ensures AWS credentials & bucket are valid.
"""
import boto3, os, sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home() / "savant/logs/s3_validator.log"
def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

def main():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1")
        )
        result = s3.list_buckets()
        names = [b["Name"] for b in result["Buckets"]]
        log(f"✅ Connected to S3 — Buckets: {names}")
        bucket = os.getenv("SAVANT_S3_BUCKET")
        if bucket and bucket in names:
            log(f"✅ Bucket {bucket} is accessible and ready.")
        else:
            log(f"⚠️  Bucket {bucket} not found; please verify your .env.")
    except Exception as e:
        log(f"❌ S3 validation failed: {e}")
        sys.exit(1)

if __name__=="__main__":
    main()
