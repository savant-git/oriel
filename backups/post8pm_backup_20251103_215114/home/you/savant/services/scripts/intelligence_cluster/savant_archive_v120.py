#!/usr/bin/env python3
"""
⬢ Savant Archive v120
Combines chat extraction, export creation, and S3/GitHub upload.
- Extracts current chat from conversations.json (asks scope).
- Converts to human-readable .txt.
- Deletes JSON afterward.
- Builds full ZIP export.
- Uploads to Downloads + S3 + GitHub.
"""
import os, json, zipfile, shutil, boto3, subprocess, time
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
EXPORTS = BASE / "exports"
CHAT_DIR = BASE / "chat_logs"
EXPORTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)
CHAT_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOGS / "savant_archive.log"

def log(msg):
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    print(msg)

# --- 1. CHAT EXTRACTION ---------------------------------------------------
def parse_chat(json_path: Path, mode="current"):
    """Extract chat(s) from conversations.json"""
    log(f"🧩 Parsing {json_path.name} ({mode})...")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"❌ Failed to parse JSON: {e}")
        return None

    chats = []
    if isinstance(data, dict) and "mapping" in data:  # single chat export
        chats.append(data)
    elif isinstance(data, list):  # multiple
        if mode == "current":
            chats.append(data[-1])
        elif mode == "project":
            chats.extend(data[-5:])
        else:
            chats.extend(data)

    txt_path = CHAT_DIR / f"chat_full_{mode}_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out = []
    for chat in chats:
        mapping = chat.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message", {})
            role = msg.get("author", {}).get("role")
            parts = msg.get("content", {}).get("parts", [])
            if not parts: continue
            out.append(f"\n[{role.upper()}]\n" + "\n".join(parts))
    if not out:
        log("⚠️  No chat content found.")
    else:
        txt_path.write_text("\n".join(out), encoding="utf-8")
        log(f"✅ Saved transcript → {txt_path}")
    json_path.unlink(missing_ok=True)
    log(f"🧹 Deleted JSON → {json_path}")
    return txt_path

# --- 2. ZIP CREATION ------------------------------------------------------
def create_zip(chat_fp: Path):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"savant_full_export_{ts}.zip"
    archive = EXPORTS / name
    log(f"📦 Creating archive: {archive}")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE / "services", LOGS, CHAT_DIR]:
            if folder.exists():
                for fp in folder.rglob("*"):
                    if fp.is_file():
                        z.write(fp, fp.relative_to(BASE))
        if chat_fp and chat_fp.exists():
            z.write(chat_fp, chat_fp.relative_to(BASE))
    log(f"✅ Archive complete → {archive}")
    return archive

# --- 3. S3 UPLOAD ---------------------------------------------------------
def upload_s3(fp):
    bucket = os.getenv("SAVANT_S3_BUCKET")
    if not bucket:
        log("⚠️  No S3 bucket configured.")
        return
    try:
        s3 = boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        key = f"exports/{fp.name}"
        s3.upload_file(str(fp), bucket, key)
        log(f"☁️  Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️  S3 upload failed: {e}")

# --- 4. GITHUB PUSH -------------------------------------------------------
def push_github(fp):
    try:
        subprocess.run(["git","-C",str(BASE),"add",str(fp)],check=True)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Auto export {datetime.now()}"],check=True)
        subprocess.run(["git","-C",str(BASE),"push"],check=True)
        log("🐙 GitHub push successful.")
    except Exception as e:
        log(f"⚠️  GitHub push failed: {e}")

# --- 5. MAIN --------------------------------------------------------------
def main():
    json_path = input("📄 Enter path to conversations.json: ").strip() or str(Path.home()/ "storage/downloads/conversations.json")
    jp = Path(json_path)
    if not jp.exists():
        log("❌ File not found.")
        return
    print("\nChoose extraction scope:\n1. Current chat only\n2. Project chats\n3. All chats")
    choice = input("→ Select (1-3): ").strip()
    mode = "current" if choice=="1" else "project" if choice=="2" else "all"
    chat_fp = parse_chat(jp, mode)
    if not chat_fp:
        log("❌ No chat extracted. Exiting.")
        return
    archive = create_zip(chat_fp)
    upload_s3(archive)
    push_github(archive)
    log("🏁 Export + Extract complete. Archive finalized.")

if __name__=="__main__":
    main()
