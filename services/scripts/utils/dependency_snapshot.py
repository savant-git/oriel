from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Cleanup v5.0 — Dependency Snapshot
Generates pip freeze and uploads to S3 for later recovery.
"""
import os, subprocess, boto3
from datetime import datetime
from pathlib import Path
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")
OUT = Path.home()/f"savant/dependency_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(OUT,"w") as f: subprocess.run(["pip","freeze"],stdout=f)
if S3_BUCKET:
    boto3.client("s3").upload_file(str(OUT),S3_BUCKET,f"manifests/{OUT.name}")
rule_status(f"✅ Dependency snapshot uploaded → {OUT.name}", "ok")
