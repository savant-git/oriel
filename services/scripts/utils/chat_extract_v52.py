from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧩 Savant Chat Extractor v52 — Stream-Safe + Human-Readable
- Finds conversations.json automatically.
- Prompts for scope (current/project/all).
- Parses incrementally to avoid memory errors.
- Produces formatted text chat.
- Uploads .txt to S3, deletes JSON.
"""
import os, json, boto3, ijson
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
CHAT = BASE / "chat_logs"
CHAT.mkdir(parents=True, exist_ok=True)
LOG = BASE / "logs/chat_extract_v52.log"

def log(m):
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")
    console.print(m)

def find_json():
    for p in [
        Path.home()/ "storage/downloads/conversations.json",
        Path("/storage/emulated/0/Download/conversations.json"),
        Path("/data/data/com.termux/files/home/storage/downloads/conversations.json")
    ]:
        if p.exists(): return p
    return None

def choose_scope():
    console.print("\nSelect extraction mode:")
    console.print("1️⃣ Current chat only\n2️⃣ All Savant project chats\n3️⃣ All chats (entire export)")
    return input("Enter 1 / 2 / 3: ").strip() or "1"

def extract(json_fp, scope):
    readable = []
    with open(json_fp, "r", encoding="utf-8") as f:
        for conv in ijson.items(f, "item"):
            if scope == "3" or ("savant" in json.dumps(conv).lower()):
                for m in conv.get("mapping", {}).values():
                    msg = m.get("message", {})
                    role = msg.get("author", {}).get("role", "user").upper()
                    parts = msg.get("content", {}).get("parts", [""])
                    if parts and parts[0].strip():
                        readable.append(f"{role}:\n  {parts[0].strip()}\n")
    return "\n".join(readable)

def upload_s3(fp):
    try:
        s3 = boto3.client("s3")
        s3.upload_file(str(fp), "savant-ai-cluster", f"chat_exports/{fp.name}")
        log(f"☁️ Uploaded to s3://savant-ai-cluster/chat_exports/{fp.name}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

def main():
    json_fp = find_json()
    if not json_fp:
        log("❌ conversations.json not found.")
        return
    scope = choose_scope()
    label = {"1": "current", "2": "project", "3": "all"}[scope]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_fp = CHAT / f"chat_full_{label}_{ts}.txt"
    out_fp.write_text(extract(json_fp, scope), encoding="utf-8")
    log(f"✅ Saved chat to {out_fp}")
    upload_s3(out_fp)
    try:
        os.remove(json_fp)
        log(f"🧹 Deleted {json_fp}")
    except: pass

if __name__=="__main__": main()
