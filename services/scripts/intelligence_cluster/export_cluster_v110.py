from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v110 — Final Integration
---------------------------------------------------------------
Unified chat extraction + export. Automatically includes latest chat log.
"""
import os, sys, zipfile, boto3, shutil, subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home()/"savant"
CHAT = BASE/"chat_logs"
EXPORTS = BASE/"exports"
LOGS = BASE/"logs"
EXPORTS.mkdir(parents=True,exist_ok=True)
LOGS.mkdir(parents=True,exist_ok=True)
LOG = LOGS/"export_v110.log"

def log(m):
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")
    console.print(m)

def get_latest_chat():
    try:
        chats=sorted(CHAT.glob("chat_full_*.txt"), key=os.path.getmtime, reverse=True)
        return chats[0] if chats else None
    except Exception as e:
        log(f"⚠️ No chat logs found: {e}")
        return None

def create_zip(chat):
    ts=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive=EXPORTS/f"savant_full_export_{ts}.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for d in [BASE/"services", LOGS, CHAT]:
            if d.exists():
                for f in d.rglob("*"):
                    if f.is_file(): z.write(f, f.relative_to(BASE))
        if chat: z.write(chat, chat.relative_to(BASE))
    log(f"📦 Created archive: {archive}")
    return archive

def upload_s3(fp):
    try:
        s3=boto3.client("s3")
        s3.upload_file(str(fp),"savant-ai-cluster",f"exports/{fp.name}")
        log(f"☁️ Uploaded to s3://savant-ai-cluster/exports/{fp.name}")
    except Exception as e: log(f"⚠️ S3 upload failed: {e}")

def copy_to_downloads(fp):
    try:
        d=Path("/storage/emulated/0/Download")
        d.mkdir(parents=True,exist_ok=True)
        shutil.copy2(fp,d/fp.name)
        log(f"📥 Copied to Downloads → {d/fp.name}")
    except Exception as e: log(f"⚠️ Copy failed: {e}")

def main():
    log(f"🧠 Export started {datetime.now(timezone.utc).isoformat()}")
    chat = get_latest_chat()
    archive=create_zip(chat)
    copy_to_downloads(archive)
    upload_s3(archive)
    log("✅ Export v110 complete — chat integrated.")

if __name__=="__main__": main()
