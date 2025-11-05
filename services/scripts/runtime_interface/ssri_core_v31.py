from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ SSRI v31 — Handshake Verifier
Tests OpenAI, GitHub, and S3 connectivity and logs the result for
migration readiness.
"""
import boto3,requests,os,json
from datetime import datetime,timezone
from pathlib import Path
LOG=Path.home()/ "savant/logs/handshake_verifier.log"
def log(m): LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")

def test_openai():
    try:
        r=requests.get("https://api.openai.com/v1/models",
          headers={"Authorization":f"Bearer {os.getenv('OPENAI_API_KEY')}"},timeout=5)
        return r.status_code==200
    except Exception: return False

def test_github():
    try:
        r=requests.get("https://api.github.com/user",
          headers={"Authorization":f"Bearer {os.getenv('GITHUB_TOKEN')}"},timeout=5)
        return r.status_code==200
    except Exception: return False

def test_s3():
    try:
        s=boto3.client("s3",
          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
          aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        s.list_buckets()
        return True
    except Exception: return False

if __name__=="__main__":
    r={"openai":test_openai(),"github":test_github(),"s3":test_s3()}
    log(json.dumps(r))
    console.print(json.dumps(r,indent=2))


# Auto-completion safeguard
pass
