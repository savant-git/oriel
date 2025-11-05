from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive v230
----------------------------------------
• Extracts the current or recent chats
• Formats and builds a beautiful HTML log
• Creates an optimized export ZIP
• Saves to Downloads, S3, and GitHub
• Adds clear headers for each stage
----------------------------------------
"""

import os, sys, json, zipfile, shutil, subprocess, time, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE     = Path.home() / "savant"
LOGS     = BASE / "logs"
EXPORTS  = BASE / "exports"
CHATDIR  = BASE / "chat_logs"
DOWNLOADS = Path("/storage/emulated/0/Download")
for p in (LOGS, EXPORTS, CHATDIR):
    p.mkdir(parents=True, exist_ok=True)

LOGFILE  = LOGS / "archive_export_v230.log"

# --------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------
def log(section, message):
    line = f"[{datetime.now(timezone.utc).isoformat()}] [{section}] {message}"
    console.print(line)
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def safe_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="ignore")

def sha256sum(file):
    h = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def copy_to_downloads(fp):
    """Copy ZIP to multiple download locations safely."""
    candidates = [
        Path.home() / "storage/downloads",
        Path("/storage/emulated/0/Download"),
        Path("/sdcard/Download"),
        DOWNLOADS,
    ]
    for d in candidates:
        try:
            d.mkdir(parents=True, exist_ok=True)
            target = d / fp.name
            shutil.copy2(fp, target)
            log("DOWNLOADS", f"Copied export to {target}")
            return True
        except Exception as e:
            log("DOWNLOADS", f"Failed {d}: {e}")
    log("DOWNLOADS", "No writable downloads folder found.")
    return False

# --------------------------------------------------------------
# 1️⃣ Extract & format chat (simplified for current chat)
# --------------------------------------------------------------
def extract_current_chat(conversations_path):
    try:
        data = json.loads(Path(conversations_path).read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Cannot parse {conversations_path}: {e}")

    if isinstance(data, dict) and "conversations" in data:
        data = data["conversations"]

    # Pick the newest conversation
    data = sorted(data, key=lambda c: c.get("update_time", 0), reverse=True)
    convo = data[0] if data else {}
    mapping = convo.get("mapping", {})

    blocks = []
    for k, v in mapping.items():
        msg = v.get("message")
        if not msg: continue
        author = (msg.get("author") or {}).get("role", "assistant")
        parts = msg.get("content") or msg.get("parts") or []
        text = "\n".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in parts])
        blocks.append((author, text.strip()))
    if not blocks:
        raise RuntimeError("No messages found in current chat.")

    # Simple formatted HTML
    html_blocks = []
    for author, text in blocks:
        color = "#9ecbff" if author == "user" else "#bff0c8"
        html_blocks.append(f"<div style='margin:1em 0'><b style='color:{color}'>{author.upper()}</b><br><pre>{text}</pre></div>")
    html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8">
    <style>body{{background:#0d0d0f;color:#e7e7ea;font-family:sans-serif;font-size:16px;line-height:1.6;}}</style>
    </head><body>{''.join(html_blocks)}</body></html>
    """
    return html, "\n\n".join([f"{a.upper()}: {t}" for a,t in blocks])

# --------------------------------------------------------------
# 2️⃣ Create ZIP export
# --------------------------------------------------------------
def create_zip(chat_html, chat_txt):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    html_path = CHATDIR / f"chat_full_{timestamp}.html"
    txt_path  = CHATDIR / f"chat_full_{timestamp}.txt"
    safe_write(html_path, chat_html)
    safe_write(txt_path, chat_txt)

    zip_path = EXPORTS / f"savant_full_export_{timestamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE / "services", LOGS, CHATDIR]:
            if folder.exists():
                for file in folder.rglob("*"):
                    if file.is_file():
                        z.write(file, file.relative_to(BASE))
    log("EXPORT", f"Created archive {zip_path}")
    return zip_path

# --------------------------------------------------------------
# 3️⃣ Upload to S3
# --------------------------------------------------------------
def upload_s3(fp):
    import boto3
    bucket = os.getenv("SAVANT_S3_BUCKET")
    if not bucket:
        log("S3", "No S3 bucket configured.")
        return False
    s3 = boto3.client("s3")
    key = f"exports/{fp.name}"
    s3.upload_file(str(fp), bucket, key)
    log("S3", f"Uploaded to s3://{bucket}/{key}")
    return True

# --------------------------------------------------------------
# 4️⃣ Push to GitHub
# --------------------------------------------------------------
def git_push(fp):
    try:
        subprocess.run(["git", "-C", str(BASE), "add", str(fp)], check=True)
        subprocess.run(["git", "-C", str(BASE), "commit", "-m", f"Auto export {datetime.now().isoformat()}"], check=True)
        subprocess.run(["git", "-C", str(BASE), "push"], check=True)
        log("GIT", "Push successful.")
    except Exception as e:
        log("GIT", f"Push failed: {e}")

# --------------------------------------------------------------
# Main
# --------------------------------------------------------------
def main():
    log("START", "Savant Archive v230 start")

    # Step 1 - find conversations.json
    console.print("Enter path to conversations.json (leave blank to auto-detect): ", end="")
    p = (sys.stdin.readline().strip() or "")
    if not p:
        candidates = [
            Path("/storage/emulated/0/Download/conversations.json"),
            Path.home() / "storage/downloads/conversations.json",
            CHATDIR / "conversations.json",
        ]
        found = [x for x in candidates if x.exists()]
        if not found:
            log("INPUT", "No conversations.json found. Abort.")
            return
        path = found[0]
    else:
        path = Path(p)
        if not path.exists():
            log("INPUT", f"File not found: {path}")
            return

    # Step 2 - extract & format
    log("ARCHIVE", f"Extracting current chat from {path}")
    html, txt = extract_current_chat(path)

    # Step 3 - zip
    log("EXPORT", "Creating export ZIP")
    zip_path = create_zip(html, txt)
    log("EXPORT", f"SHA256: {sha256sum(zip_path)}")

    # Step 4 - copy to Downloads
    log("DOWNLOADS", "Saving to device Downloads")
    copy_to_downloads(zip_path)

    # Step 5 - S3 upload
    log("S3", "Uploading to S3 (if configured)")
    try:
        upload_s3(zip_path)
    except Exception as e:
        log("S3", f"Upload failed: {e}")

    # Step 6 - GitHub push
    log("GIT", "Pushing to GitHub (if repo exists)")
    git_push(zip_path)

    log("DONE", "Archive complete")
    console.print("\n✅ Archive complete\n")

if __name__ == "__main__":
    main()
