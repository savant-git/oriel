from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive-Export v152
Formatted HTML chat + instant mobile viewer.
"""

import os, re, json, zipfile, shutil, subprocess, boto3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home()/ "savant"
LOGS = BASE/"logs"; CHAT_DIR = BASE/"chat_logs"; EXPORTS = BASE/"exports"
for d in (LOGS, CHAT_DIR, EXPORTS): d.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS/"archive_export_v152.log"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f: f.write(f"[{ts}] {msg}\n")
    console.print(msg)

def normalize_part(p):
    if isinstance(p, str): return p
    if isinstance(p, (dict, list)): return json.dumps(p, ensure_ascii=False)
    return str(p)

# ---------------------------------------------------------------
# 1️⃣  Build rich HTML with mobile styling + TOC
# ---------------------------------------------------------------
def parse_and_format_chat(json_path):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    blocks, toc = [], []
    index = 1
    for conv in data:
        title = conv.get("title") or f"Conversation {index}"
        msgs = list(conv.get("mapping", {}).values())
        if not msgs: continue
        block_lines = [f"<a name='block{index}'></a>", f"<h2>{title}</h2>"]
        for m in msgs:
            msg = m.get("message") or {}
            content = msg.get("content") or {}
            parts = content.get("parts") or []
            if not parts: continue
            role = msg.get("author", {}).get("role", "system").capitalize()
            text = " ".join(normalize_part(p) for p in parts)
            text = re.sub(r"\s+", " ", text.strip())
            if text:
                block_lines.append(f"<div class='msg {role.lower()}'><b>{role}:</b> {text}</div>")
        if len(block_lines) > 2:
            blocks.append("\n".join(block_lines))
            toc.append(f"<li><a href='#block{index}'>{title}</a></li>")
        index += 1

    toc_html = "<ul>" + "\n".join(toc) + "</ul>"
    style = """
    <style>
    body{font-family:Arial,Helvetica,sans-serif;padding:20px;max-width:800px;margin:auto;line-height:1.5;background:#fafafa;color:#222;}
    h1,h2{color:#222;border-bottom:1px solid #ddd;padding-bottom:4px;}
    ul{list-style:none;padding:0;} ul li{margin:4px 0;}
    a{text-decoration:none;color:#0077cc;} a:hover{text-decoration:underline;}
    .msg.user{background:#e0f7fa;padding:10px;border-radius:8px;margin:8px 0;}
    .msg.assistant{background:#fff8e1;padding:10px;border-radius:8px;margin:8px 0;}
    .msg.system{background:#eeeeee;padding:10px;border-radius:8px;margin:8px 0;}
    #homebar{position:fixed;bottom:0;left:0;right:0;background:white;padding:20px;text-align:center;
    border-top:1px solid #ccc;}
    #homebar a{font-size:18px;font-weight:bold;color:#222;text-decoration:none;}
    </style>
    """
    footer = "<div id='homebar'><a href='#top'>⬆ Home</a></div>"
    html = f"<html><head><meta charset='utf-8'><title>Savant Chat Log</title>{style}</head><body><a name='top'></a><h1>Savant Chat Log</h1>{toc_html}<hr>" + "\n<hr>\n".join(blocks) + footer + "</body></html>"
    fp = CHAT_DIR / "chat_full_current.html"
    fp.write_text(html, encoding="utf-8")
    log(f"✅ Chat formatted → {fp}")
    for f in CHAT_DIR.glob("chat_full_*"):
        if f != fp: f.unlink(missing_ok=True)
    return fp

# ---------------------------------------------------------------
# 2️⃣  Export and open
# ---------------------------------------------------------------
def create_archive(chat_fp):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    arc = BASE/"exports"/f"savant_full_export_{ts}.zip"
    with zipfile.ZipFile(arc,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE/"services",BASE/"chat_logs",BASE/"logs"]:
            for fp in folder.rglob("*"):
                if fp.is_file(): z.write(fp,fp.relative_to(BASE))
    log(f"📦 Archive → {arc}")
    return arc

def copy_to_downloads(fp):
    dl = Path("/storage/emulated/0/Download")
    if not dl.exists(): dl = Path.home()/ "storage/downloads"
    dl.mkdir(parents=True, exist_ok=True)
    tgt = dl/fp.name
    shutil.copy2(fp, tgt)
    log(f"📥 Copied to Downloads → {tgt}")

def upload_s3(fp):
    try:
        bucket = os.getenv("SAVANT_S3_BUCKET")
        if not bucket: return log("⚠️ No S3 bucket configured.")
        s3 = boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        s3.upload_file(str(fp), bucket, f"exports/{fp.name}")
        log(f"☁️ Uploaded to s3://{bucket}/exports/{fp.name}")
    except Exception as e: log(f"⚠️ S3 upload failed: {e}")

def push_github(fp):
    try:
        subprocess.run(["git","-C",str(BASE),"add","."],check=True)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Auto export {datetime.now().isoformat()}"],check=True)
        subprocess.run(["git","-C",str(BASE),"push"],check=True)
        log("🐙 GitHub push successful.")
    except Exception as e: log(f"⚠️ GitHub push failed: {e}")

def open_html(chat_fp):
    try:
        subprocess.run(["am","start","-a","android.intent.action.VIEW","-d",f"file://{chat_fp}"],check=False)
        log("🌐 Opened in mobile browser.")
    except Exception as e: log(f"⚠️ Could not open automatically: {e}")

# ---------------------------------------------------------------
def main():
    log("🧠 Starting Savant Archive-Export v152")
    jpath = Path("/storage/emulated/0/Download/conversations.json")
    if not jpath.exists(): return log("❌ conversations.json not found in Downloads.")
    chat_fp = parse_and_format_chat(jpath)
    arc = create_archive(chat_fp)
    copy_to_downloads(arc)
    upload_s3(arc)
    push_github(arc)
    open_html(chat_fp)
    log("✅ Full export + HTML viewer ready.")

if __name__=="__main__":
    try: main()
    except Exception as e: log(f"❌ Fatal error: {e}")
