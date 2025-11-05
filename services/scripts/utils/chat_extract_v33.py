from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Chat Extract v33
---------------------------------------------------------------
Fully self-healing version that:
  - Auto-installs boto3 if missing
  - Lets user pick scope (current / project / all)
  - Saves chat logs locally and to S3
  - Adds extracted chat to the newest export zip
"""

import os, json, pathlib, sys, subprocess, zipfile
from datetime import datetime, timezone

# --- 0. Optional boto3 bootstrap ---
try:
    import boto3
except ImportError:
    subprocess.run(["pip", "install", "--break-system-packages", "boto3"], stdout=subprocess.DEVNULL)
    import boto3

BASE = pathlib.Path.home() / "savant"
LOGS = BASE / "logs"
OUT = BASE / "chat_logs"
EXPORTS = BASE / "exports"
LOGS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
LOG = LOGS / "chat_extract_v33.log"

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
    if choice not in {"1","2","3"}: choice="1"
    return choice

def load_json(fp):
    try:
        return json.load(open(fp, "r", encoding="utf-8"))
    except Exception as e:
        log(f"❌ JSON load error: {e}")
        sys.exit(1)

def filter_conversations(data, mode):
    if not isinstance(data, list):
        return [data]
    selected = []
    for conv in data:
        blob = json.dumps(conv)
        if mode == "1" and "savant" in blob.lower() and "non-negotiable" in blob.lower():
            return [conv]
        elif mode == "2" and "savant" in blob.lower():
            selected.append(conv)
        elif mode == "3":
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

def add_to_latest_export(txt):
    EXPORTS.mkdir(exist_ok=True)
    zips = list(EXPORTS.glob("savant_full_export_*.zip"))
    if not zips:
        log("⚠️ No existing export zip found; skipping update.")
        return
    latest = max(zips, key=lambda z: z.stat().st_mtime)
    with zipfile.ZipFile(latest, "a", compression=zipfile.ZIP_DEFLATED) as z:
        rel = txt.relative_to(BASE)
        z.write(txt, rel)
    log(f"📦 Added chat log → {latest}")

def main():
    log("🧠 Savant Chat Extract v33 — Scoped + Export sync")
    fp = auto_find_json()
    mode = choose_scope()
    data = load_json(fp)
    convs = filter_conversations(data, mode)
    label = {"1":"current","2":"project","3":"all"}[mode]
    raw, txt = save_outputs(convs, label)
    upload_s3(raw)
    upload_s3(txt)
    add_to_latest_export(txt)
    log("🏁 Extraction complete + integrated into latest export.")

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Interrupted by user.")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
