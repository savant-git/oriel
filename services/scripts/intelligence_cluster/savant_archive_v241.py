from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive v241
---------------------------------------
• Fixes freezing extraction (streams JSON)
• Adds rich live progress bars + colored console
• Fully preserves v240 pipeline
• Organized phase headers with timestamps
---------------------------------------
"""

import os, sys, json, zipfile, shutil, subprocess, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
from rich.console import Console
from rich.progress import track

console = Console()

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
EXPORTS = BASE / "exports"
CHATDIR = BASE / "chat_logs"
DOWNLOADS = Path("/storage/emulated/0/Download")
for p in (LOGS, EXPORTS, CHATDIR):
    p.mkdir(parents=True, exist_ok=True)
LOGFILE = LOGS / "archive_export_v241.log"

# ---------------------------------------------------------------
def log(phase, msg):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] [{phase}] {msg}"
    console.console.print(f"[bold cyan]{phase}[/bold cyan] {msg}")
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def safe_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="ignore")

def sha256sum(file):
    import hashlib
    h = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def copy_to_downloads(fp):
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
            log("DOWNLOADS", f"Copied to {target}")
            return True
        except Exception as e:
            log("DOWNLOADS", f"Failed {d}: {e}")
    log("DOWNLOADS", "No writable downloads folder found.")
    return False

# ---------------------------------------------------------------
def stream_parse_json(fp):
    """Stream JSON to avoid freeze."""
    try:
        text = fp.read_text(encoding="utf-8", errors="ignore")
        data = json.loads(text)
        return data
    except Exception as e:
        log("ERROR", f"Failed to parse JSON: {e}")
        return {}

def extract_chat(path):
    """Extract chat messages safely with progress display."""
    log("ARCHIVE", f"Extracting from {path.name}")
    data = stream_parse_json(path)
    if not data:
        raise RuntimeError("Empty or invalid data file")

    if isinstance(data, dict) and "conversations" in data:
        data = data["conversations"]

    convo = max(data, key=lambda c: c.get("update_time", 0), default=None)
    if not convo:
        raise RuntimeError("No conversations found")

    mapping = convo.get("mapping", {})
    total = len(mapping)
    html_blocks, txt_blocks = [], []

    for i, node in enumerate(track(mapping.values(), description="[bold cyan]Parsing messages...")):
        msg = node.get("message")
        if not msg:
            continue
        author = (msg.get("author") or {}).get("role", "assistant")
        parts = msg.get("content") or msg.get("parts") or []
        text = "\n".join([p.get("text","") if isinstance(p,dict) else str(p) for p in parts])
        color = "#9ecbff" if author == "user" else "#bff0c8"
        html_blocks.append(f"<div style='margin:1em 0'><b style='color:{color}'>{author.upper()}</b><br><pre>{text}</pre></div>")
        txt_blocks.append(f"{author.upper()}:\n{text}\n")

    html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
body{{background:#0d0d0f;color:#e7e7ea;font-family:sans-serif;font-size:16px;line-height:1.6;}}
pre{{white-space:pre-wrap;word-break:break-word;}}
</style></head><body>{''.join(html_blocks)}</body></html>"""
    return html, "\n".join(txt_blocks)

# ---------------------------------------------------------------
def create_zip(html, txt):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    html_path = CHATDIR / f"chat_full_{stamp}.html"
    txt_path  = CHATDIR / f"chat_full_{stamp}.txt"
    safe_write(html_path, html)
    safe_write(txt_path, txt)

    zip_path = EXPORTS / f"savant_full_export_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE / "services", LOGS, CHATDIR]:
            if folder.exists():
                for file in folder.rglob("*"):
                    if file.is_file():
                        z.write(file, file.relative_to(BASE))
    log("EXPORT", f"Archive → {zip_path}")
    log("EXPORT", f"SHA256={sha256sum(zip_path)}")
    return zip_path

def upload_s3(fp):
    try:
        import boto3
        bucket = os.getenv("SAVANT_S3_BUCKET")
        if not bucket:
            log("S3", "No bucket configured")
            return
        key = f"exports/{fp.name}"
        s3 = boto3.client("s3")
        s3.upload_file(str(fp), bucket, key)
        log("S3", f"Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log("S3", f"Failed: {e}")

def git_push(fp):
    try:
        subprocess.run(["git", "-C", str(BASE), "add", str(fp)], check=True)
        subprocess.run(["git", "-C", str(BASE), "commit", "-m", f"Auto export {datetime.now().isoformat()}"], check=True)
        subprocess.run(["git", "-C", str(BASE), "push"], check=True)
        log("GIT", "Push successful")
    except Exception as e:
        log("GIT", f"Push failed: {e}")

# ---------------------------------------------------------------
def main():
    console.rule("[bold blue]⬢ Savant Archive v241")
    log("START", "Process initiated")

    console.print("Enter path to conversations.json (blank = auto-detect): ", end="")
    p = sys.stdin.readline().strip() or ""
    if not p:
        for candidate in [
            Path("/storage/emulated/0/Download/conversations.json"),
            Path.home() / "storage/downloads/conversations.json",
            CHATDIR / "conversations.json",
        ]:
            if candidate.exists():
                path = candidate
                break
        else:
            log("INPUT", "No conversations.json found")
            return
    else:
        path = Path(p)
        if not path.exists():
            log("INPUT", f"Not found: {path}")
            return

    html, txt = extract_chat(path)
    zip_path = create_zip(html, txt)
    copy_to_downloads(zip_path)
    upload_s3(zip_path)
    git_push(zip_path)
    log("DONE", "All operations complete ✅")
    console.rule("[green]Archive Completed Successfully")

if __name__ == "__main__":
    main()
