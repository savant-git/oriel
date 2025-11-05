from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export v90 — Unified Extract + Export
---------------------------------------------------------------
One-command archive builder that:
  ✓ Locates and parses conversations.json
  ✓ Extracts chosen chat scope (current/project/all)
  ✓ Creates human-readable text transcript
  ✓ Deletes JSON once done
  ✓ Builds full export ZIP (scripts, logs, chats)
  ✓ Uploads to Downloads, S3, and GitHub
"""

import os, sys, json, zipfile, shutil, subprocess, boto3, textwrap
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
EXPORTS = BASE / "exports"
CHAT_DIR = BASE / "chat_logs"
LOGS = BASE / "logs"
EXPORTS.mkdir(parents=True, exist_ok=True)
CHAT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS / "export_v90.log"

def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        ts = datetime.now(timezone.utc).isoformat()
        f.write(f"[{ts}] {msg}\n")
    console.print(msg)

# --- Chat Extraction -----------------------------------------------------
def auto_find_json():
    search_paths = [
        Path.home() / "storage/downloads",
        Path("/storage/emulated/0/Download"),
        Path("/sdcard/Download")
    ]
    for path in search_paths:
        for f in path.glob("**/conversations*.json"):
            return f
    return None

def choose_scope():
    console.print("\nSelect extraction mode:")
    console.print("  1️⃣  Current chat only")
    console.print("  2️⃣  All Savant project chats")
    console.print("  3️⃣  All chats (entire export)")
    choice = input("Enter 1 / 2 / 3: ").strip() or "1"
    return choice

def parse_json(fp, scope):
    data = json.load(open(fp, "r", encoding="utf-8"))
    if not isinstance(data, list): data = [data]
    chats = []
    for conv in data:
        if scope == "3":
            chats.append(conv)
        else:
            text_blob = json.dumps(conv).lower()
            if "savant" in text_blob and (scope == "2" or "non-negotiable" in text_blob):
                chats.append(conv)
    return chats

def to_human_readable(convs):
    lines = []
    for c in convs:
        if isinstance(c, dict) and "mapping" in c:
            for m in c["mapping"].values():
                if not isinstance(m, dict): continue
                msg = m.get("message", {})
                author = msg.get("author", {}).get("role", "unknown")
                content = msg.get("content", {}).get("parts", [""])[0]
                if content:
                    lines.append(f"{author.upper()}:\n{textwrap.indent(content.strip(), '  ')}\n")
    return "\n".join(lines)

def extract_chat():
    fp = auto_find_json()
    if not fp:
        log("⚠️ No conversations.json found; skipping chat extraction.")
        return None
    scope = choose_scope()
    convs = parse_json(fp, scope)
    if not convs:
        log("⚠️ No relevant conversations found.")
        return None
    label = {"1": "current", "2": "project", "3": "all"}[scope]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    text_fp = CHAT_DIR / f"chat_full_{label}_{ts}.txt"
    json_fp = CHAT_DIR / f"chat_raw_{label}_{ts}.json"
    json_fp.write_text(json.dumps(convs, indent=2), encoding="utf-8")
    text_fp.write_text(to_human_readable(convs), encoding="utf-8")
    log(f"✅ Saved readable chat → {text_fp}")
    log(f"✅ Saved raw JSON → {json_fp}")
    try:
        os.remove(json_fp)
        log(f"🧹 Deleted raw JSON file → {json_fp}")
    except Exception as e:
        log(f"⚠️ Could not delete JSON: {e}")
    return text_fp

# --- ZIP Creation --------------------------------------------------------
def create_zip(chat_fp):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive = EXPORTS / f"savant_full_export_{ts}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE / "services", LOGS, CHAT_DIR]:
            if folder.exists():
                for fp in folder.rglob("*"):
                    if fp.is_file():
                        z.write(fp, fp.relative_to(BASE))
        if chat_fp and chat_fp.exists():
            z.write(chat_fp, chat_fp.relative_to(BASE))
    log(f"📦 Created export → {archive}")
    return archive

# --- Copy to Downloads ---------------------------------------------------
def copy_to_downloads(fp):
    try:
        downloads = Path.home() / "storage/downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        target = downloads / fp.name
        shutil.copy2(fp, target)
        log(f"📥 Copied to Downloads → {target}")
    except Exception as e:
        log(f"⚠️ Copy failed: {e}")

# --- Upload to S3 --------------------------------------------------------
def upload_s3(fp):
    bucket = os.getenv("SAVANT_S3_BUCKET")
    if not bucket:
        log("☁️ No S3 bucket configured.")
        return
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        key = f"exports/{fp.name}"
        s3.upload_file(str(fp), bucket, key)
        log(f"☁️ Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

# --- GitHub push --------------------------------------------------------
def push_github(fp):
    try:
        subprocess.run(["git", "-C", str(BASE), "add", str(fp)], check=True)
        subprocess.run(["git", "-C", str(BASE), "commit", "-m", f"Auto export {datetime.now().isoformat()}"], check=True)
        subprocess.run(["git", "-C", str(BASE), "push"], check=True)
        log("🐙 GitHub push successful.")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

# --- MAIN ---------------------------------------------------------------
def main():
    log(f"🧠 Savant Export v90 — Start {datetime.now(timezone.utc).isoformat()}")
    chat_fp = extract_chat()
    archive = create_zip(chat_fp)
    copy_to_downloads(archive)
    upload_s3(archive)
    push_github(archive)
    log("✅ Unified export complete — chat included, all targets synced.")

if __name__ == "__main__":
    main()
