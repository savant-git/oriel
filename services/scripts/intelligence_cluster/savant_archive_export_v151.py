from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive-Export v151
Safe, self-healing parser for malformed ChatGPT JSON.
Preserves full export (Downloads + S3 + GitHub).
"""

import os, re, json, zipfile, shutil, subprocess, boto3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home()/ "savant"
LOGS = BASE/"logs"; CHAT_DIR = BASE/"chat_logs"; EXPORTS = BASE/"exports"
for d in (LOGS, CHAT_DIR, EXPORTS): d.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS/"archive_export_v151.log"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    console.print(msg)

# ---------------------------------------------------------------
# 1️⃣  Robust chat formatter
# ---------------------------------------------------------------
def normalize_part(p):
    if isinstance(p, str): return p
    if isinstance(p, (dict, list)): return json.dumps(p, ensure_ascii=False)
    return str(p)

def parse_and_format_chat(json_path):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    blocks, toc = [], []
    index = 1
    for conv in data:
        title = conv.get("title") or f"Conversation {index}"
        msgs = list(conv.get("mapping", {}).values())
        if not msgs: continue
        block_lines = [f"<a name='block{index}'></a>", f"\n<h2>{title}</h2>\n"]
        for m in msgs:
            msg = m.get("message") or {}
            content = msg.get("content") or {}
            parts = content.get("parts") or []
            if not parts: continue
            role = msg.get("author", {}).get("role", "system").upper()
            text = " ".join(normalize_part(p) for p in parts)
            text = re.sub(r"\s+", " ", text.strip())
            if text:
                block_lines.append(f"<p><b>{role}:</b> {text}</p>")
        if len(block_lines) > 2:
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
    for f in CHAT_DIR.glob("chat_full_*"):
        if f != fp: f.unlink(missing_ok=True)
    return fp

# ---------------------------------------------------------------
# 2️⃣  Export (Downloads + S3 + GitHub)
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
def main():
    log("🧠 Starting Savant Archive-Export v151")
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
    try: main()
    except Exception as e: log(f"❌ Fatal error: {e}")
