from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
S3 Validator v112 — Verifies AWS credentials and bucket.
"""
import boto3, os, sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home()/ "savant/logs/s3_validator_v112.log"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

def main():
    try:
        access=os.getenv("AWS_ACCESS_KEY_ID")
        secret=os.getenv("AWS_SECRET_ACCESS_KEY")
        bucket=os.getenv("SAVANT_S3_BUCKET","savant-ai-cluster")
        if not access or not secret:
            log("❌ Missing AWS credentials in environment.")
            sys.exit(1)
        s3=boto3.client("s3",
            aws_access_key_id=access,
            aws_secret_access_key=secret,
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        res=s3.list_buckets()
        names=[b["Name"] for b in res["Buckets"]]
        if bucket in names:
            log(f"✅ Connected. Bucket '{bucket}' accessible.")
        else:
            log(f"⚠️ Bucket '{bucket}' not found. Existing buckets: {names}")
    except Exception as e:
        log(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__=="__main__": main()
