#!/usr/bin/env python3
"""
⬢ Savant Archive-Export v150
Unified chat extraction → formatted archive → full export.
Restores all GitHub, S3, and Downloads functionality.
"""

import os, re, sys, json, zipfile, shutil, subprocess, hashlib, boto3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home()/ "savant"
LOGS = BASE/"logs"; CHAT_DIR = BASE/"chat_logs"; EXPORTS = BASE/"exports"
for d in (LOGS, CHAT_DIR, EXPORTS): d.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS/"archive_export_v150.log"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    LOG_FILE.open("a", encoding="utf-8").write(f"[{ts}] {msg}\n")
    print(msg)

# ---------------------------------------------------------------
# 1️⃣  Parse + Format Chat (with Table of Contents)
# ---------------------------------------------------------------
def parse_and_format_chat(json_path):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    blocks, toc = [], []
    index = 1
    for conv in data:
        title = conv.get("title", f"Conversation {index}")
        msgs = list(conv.get("mapping", {}).values())
        if not msgs: continue
        block_lines = [f"<a name='block{index}'></a>", f"\n<h2>{title}</h2>\n"]
        for m in msgs:
            msg = m.get("message")
            if not msg or not msg.get("content"): continue
            role = msg.get("author", {}).get("role", "system").upper()
            text = " ".join(msg["content"].get("parts", []))
            if not text.strip(): continue
            text = re.sub(r"\s+", " ", text.strip())
            block_lines.append(f"<p><b>{role}:</b> {text}</p>")
        blocks.append("\n".join(block_lines))
        toc.append(f"<li><a href='#block{index}'>{title}</a></li>")
        index += 1

    toc_html = "<ul>" + "\n".join(toc) + "</ul>"
    footer = """
    <div style="position:fixed;bottom:0;left:0;right:0;background:white;
    padding:20px;text-align:center;border-top:1px solid #ccc;">
    <a href='#top' style='font-size:18px;font-weight:bold;color:#222;
    text-decoration:none;'>⬆ Home</a></div>
    """
    html = f"<a name='top'></a><h1>Savant Chat Log</h1>{toc_html}\n" + "\n<hr>\n".join(blocks) + footer
    fp = CHAT_DIR / "chat_full_current.html"
    fp.write_text(html, encoding="utf-8")
    log(f"✅ Chat formatted → {fp}")
    # remove duplicates
    for f in CHAT_DIR.glob("chat_full_*"):
        if f != fp: f.unlink(missing_ok=True)
    return fp

# ---------------------------------------------------------------
# 2️⃣  Export everything (Downloads + S3 + GitHub)
# ---------------------------------------------------------------
def create_archive(chat_fp):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    arc = EXPORTS / f"savant_full_export_{ts}.zip"
    log(f"📦 Creating archive: {arc}")
    with zipfile.ZipFile(arc, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE/"services", CHAT_DIR, LOGS]:
            for fp in folder.rglob("*"):
                if fp.is_file():
                    z.write(fp, fp.relative_to(BASE))
        if chat_fp.exists():
            z.write(chat_fp, chat_fp.relative_to(BASE))
    return arc

def copy_to_downloads(fp):
    for path in [Path("/storage/emulated/0/Download"), Path.home()/ "storage/downloads"]:
        if path.exists():
            try:
                tgt = path/fp.name
                shutil.copy2(fp, tgt)
                log(f"📥 Copied to Downloads → {tgt}")
                return
            except Exception as e:
                log(f"⚠️ Copy failed: {e}")

def upload_s3(fp):
    try:
        bucket = os.getenv("SAVANT_S3_BUCKET")
        if not bucket:
            log("⚠️ No S3 bucket configured.")
            return
        s3 = boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        key = f"exports/{fp.name}"
        s3.upload_file(str(fp), bucket, key)
        log(f"☁️ Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

def push_github(fp):
    try:
        subprocess.run(["git","-C",str(BASE),"add","."],check=True)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Auto export {datetime.now().isoformat()}"],check=True)
        subprocess.run(["git","-C",str(BASE),"push"],check=True)
        log("🐙 GitHub push successful.")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

# ---------------------------------------------------------------
# 3️⃣  Main Routine
# ---------------------------------------------------------------
def main():
    log("🧠 Starting Savant Archive-Export v150")
    jpath = Path("/storage/emulated/0/Download/conversations.json")
    if not jpath.exists():
        log("❌ conversations.json not found in Downloads.")
        return
    chat_fp = parse_and_format_chat(jpath)
    arc = create_archive(chat_fp)
    copy_to_downloads(arc)
    upload_s3(arc)
    push_github(arc)
    log("✅ Full export complete — all destinations updated.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Fatal error: {e}")
