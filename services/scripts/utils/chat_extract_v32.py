from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Chat Extract v32
---------------------------------------------------------------
Smart-scoped extractor for ChatGPT `conversations.json`.

Modes:
  1️⃣  Current chat only (matches by "savant" + keywords)
  2️⃣  All chats in Savant project
  3️⃣  All chats in export

Outputs:
  • chat_full_<timestamp>.txt
  • chat_raw_<timestamp>.json
  • uploads to S3 automatically if configured
"""

import os, json, boto3, pathlib, sys
from datetime import datetime, timezone

BASE = pathlib.Path.home() / "savant"
LOGS = BASE / "logs"
OUT = BASE / "chat_logs"
LOGS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
LOG = LOGS / "chat_extract_v32.log"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    LOG.open("a", encoding="utf-8").write(f"[{ts}] {msg}\n")
    console.print(msg)

def auto_find_json():
    search_roots = [
        pathlib.Path.home() / "storage/downloads",
        pathlib.Path("/storage/emulated/0/Download"),
        pathlib.Path("/sdcard/Download")
    ]
    candidates = []
    for r in search_roots:
        if r.exists():
            for f in r.glob("**/conversations*.json"):
                candidates.append(f)
    if not candidates:
        log("❌ No conversations.json found in known paths.")
        sys.exit(1)
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    log(f"📂 Found export: {latest}")
    return latest

def choose_scope():
    console.print("\nSelect extraction mode:")
    console.print("  1️⃣  Current chat only")
    console.print("  2️⃣  All Savant project chats")
    console.print("  3️⃣  All chats (entire export)")
    choice = input("Enter 1 / 2 / 3: ").strip() or "1"
    if choice not in {"1","2","3"}:
        choice="1"
    return choice

def load_json(fp):
    try:
        return json.load(open(fp, "r", encoding="utf-8"))
    except Exception as e:
        log(f"❌ JSON load error: {e}")
        sys.exit(1)

def filter_conversations(data, mode):
    if not isinstance(data, list):
        log("⚠️ Unexpected format; exporting raw content.")
        return [data]
    selected = []
    for conv in data:
        blob = json.dumps(conv)
        if mode=="1":
            # Current chat only
            if "savant" in blob.lower() and "non-negotiable" in blob.lower():
                return [conv]
        elif mode=="2":
            if "savant" in blob.lower():
                selected.append(conv)
        elif mode=="3":
            selected.append(conv)
    return selected

def save_outputs(convs, label):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw = OUT / f"chat_raw_{label}_{ts}.json"
    txt = OUT / f"chat_full_{label}_{ts}.txt"
    json.dump(convs, open(raw,"w",encoding="utf-8"), indent=2)
    txt.write_text(json.dumps(convs, indent=2), encoding="utf-8")
    log(f"✅ Saved transcript → {txt}")
    log(f"✅ Saved raw JSON → {raw}")
    return raw, txt

def upload_s3(file_path):
    try:
        bucket = os.getenv("SAVANT_S3_BUCKET")
        if not bucket:
            log("☁️  No S3 bucket configured; skipping upload.")
            return
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1")
        )
        key = f"chat_exports/{file_path.name}"
        s3.upload_file(str(file_path), bucket, key)
        log(f"☁️  Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

def main():
    log("🧠 Savant Chat Extract v32 — Scoped mode active")
    fp = auto_find_json()
    mode = choose_scope()
    data = load_json(fp)
    convs = filter_conversations(data, mode)
    label = {"1":"current","2":"project","3":"all"}[mode]
    raw, txt = save_outputs(convs, label)
    upload_s3(raw)
    upload_s3(txt)
    log("🏁 Extraction complete and mirrored to cloud.")

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Interrupted by user.")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
