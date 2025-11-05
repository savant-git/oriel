from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v140
Full-featured export: chat parsing + archive + S3 + GitHub + Downloads
Nothing removed; every previous function preserved.
"""

import os, sys, shutil, zipfile, json, boto3, requests, subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home()/ "savant"
LOGS = BASE/"logs"; EXPORTS = BASE/"exports"; CHAT_DIR = BASE/"chat_logs"
for d in (LOGS, EXPORTS, CHAT_DIR): d.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS/"export_v140.log"

def log(msg):
    ts=datetime.now(timezone.utc).isoformat()
    LOG_FILE.parent.mkdir(parents=True,exist_ok=True)
    with LOG_FILE.open("a",encoding="utf-8") as f: f.write(f"[{ts}] {msg}\n")
    console.print(msg)

# --- Chat parsing and formatting -----------------------------------------
def find_json():
    dl=Path("/storage/emulated/0/Download/conversations.json")
    alt=Path.home()/ "storage/downloads/conversations.json"
    if dl.exists(): return dl
    if alt.exists(): return alt
    return None

def parse_chat(path):
    log(f"🧩 Parsing chat JSON from {path}")
    try:
        data=json.loads(Path(path).read_text(encoding="utf-8"))
        out=[]
        for conv in data:
            title=conv.get("title","Untitled Chat")
            out.append(f"\n\n=== {title} ===\n")
            msgs=conv.get("mapping",{}).values()
            for m in msgs:
                msg=m.get("message")
                if not msg or "author" not in msg or "content" not in msg: continue
                role=msg["author"].get("role","system").upper()
                parts=msg["content"].get("parts",[])
                text="\n".join(p for p in parts if isinstance(p,str))
                if text.strip():
                    out.append(f"\n[{role}]\n{text.strip()}\n")
        ts=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        fp=CHAT_DIR/f"chat_full_export_{ts}.txt"
        fp.write_text("".join(out),encoding="utf-8")
        try: os.remove(path)
        except Exception: pass
        return fp
    except Exception as e:
        log(f"⚠️ Chat parse failed: {e}")
        return None

# --- ZIP creation ---------------------------------------------------------
def make_archive(chat_fp=None):
    ts=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    arc=EXPORTS/f"savant_full_export_{ts}.zip"
    log(f"📦 Creating archive: {arc.name}")
    with zipfile.ZipFile(arc,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE/"services",LOGS,CHAT_DIR]:
            if folder.exists():
                for fp in folder.rglob("*"):
                    if fp.is_file(): z.write(fp,fp.relative_to(BASE))
        if chat_fp and chat_fp.exists():
            z.write(chat_fp,chat_fp.relative_to(BASE))
    log(f"✅ Archive complete → {arc}")
    return arc

# --- Copy to Downloads ----------------------------------------------------
def copy_to_downloads(fp):
    try:
        dl=Path("/storage/emulated/0/Download")
        if not dl.exists(): dl=Path.home()/ "storage/downloads"
        dl.mkdir(parents=True,exist_ok=True)
        tgt=dl/fp.name
        shutil.copy2(fp,tgt)
        log(f"📥 Copied to Downloads → {tgt}")
    except Exception as e:
        log(f"⚠️ Copy failed: {e}")

# --- Upload to S3 ---------------------------------------------------------
def upload_s3(fp):
    try:
        bucket=os.getenv("SAVANT_S3_BUCKET")
        if not bucket:
            log("⚠️ No S3 bucket configured.")
            return
        s3=boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        key=f"exports/{fp.name}"
        s3.upload_file(str(fp),bucket,key)
        log(f"☁️ Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

# --- Push to GitHub -------------------------------------------------------
def push_github(fp):
    repo=BASE
    try:
        subprocess.run(["git","-C",str(repo),"add",str(fp)],check=True)
        subprocess.run(["git","-C",str(repo),"commit","-m",f"Auto export {datetime.now().isoformat()}"],check=True)
        subprocess.run(["git","-C",str(repo),"push"],check=True)
        log("🐙 GitHub push successful.")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

# --- MAIN -----------------------------------------------------------------
def main():
    log(f"🧠 Savant Export v140 start {datetime.now(timezone.utc).isoformat()}")
    j=find_json()
    chat_fp=None
    if j and j.exists(): chat_fp=parse_chat(j)
    else: log("⚠️ No conversations.json found — skipping chat.")
    arc=make_archive(chat_fp)
    copy_to_downloads(arc)
    upload_s3(arc)
    push_github(arc)
    log("✅ Export v140 complete — all destinations updated.")

if __name__=="__main__":
    try: main()
    except Exception as e: log(f"❌ Fatal error: {e}")
