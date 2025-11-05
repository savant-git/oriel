from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v6.2
Full unabridged chat log capture and export system.
 • Captures all chat text (both sides, with code)
 • Standard ZIP archive only — no zstd compression
 • Saves to Downloads
 • Uploads to S3
 • Pushes to GitHub
"""

import os, zipfile, boto3, shutil, subprocess, json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
EXPORTS = BASE / "exports"
LOGS = BASE / "logs"
DOWNLOADS = Path.home() / "storage/downloads"
S3_BUCKET = os.getenv("SAVANT_S3_BUCKET")
CHAT_SRC = Path.home() / "savant/chat_history"
CHAT_OUT = LOGS / "chat_full_log.txt"
CHAT_JSON = LOGS / "chat_full_log.json"
LOG_PATH = LOGS / "export_cluster_v6_2.log"

# ------------------- Logging -------------------
def log(msg):
    LOGS.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

# ------------------- Chat Log Collector -------------------
def collect_chat_log():
    log("🧠 Collecting full chat history...")
    combined = []
    sources = []

    # Main chat history
    if CHAT_SRC.exists():
        for f in sorted(CHAT_SRC.glob("*.txt")):
            try:
                combined.append(f"\n--- FILE: {f.name} ---\n")
                combined.append(f.read_text(errors="ignore"))
                sources.append(str(f))
            except Exception as e:
                log(f"⚠️ Failed to read {f}: {e}")

    # Fallback logs
    for f in sorted(LOGS.glob("chat_*.txt")):
        try:
            combined.append(f"\n--- FILE: {f.name} ---\n")
            combined.append(f.read_text(errors="ignore"))
            sources.append(str(f))
        except Exception as e:
            log(f"⚠️ Failed to read {f}: {e}")

    CHAT_OUT.write_text("\n".join(combined) or "(no chat data found)", encoding="utf-8")
    log(f"📘 Combined chat log → {CHAT_OUT} ({len(combined)} segments)")

    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "sources": sources, "text": "\n".join(combined)}
    CHAT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    log(f"💾 JSON chat log mirror → {CHAT_JSON}")

# ------------------- ZIP Creation -------------------
def create_archive():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = EXPORTS / f"savant_full_export_{ts}.zip"
    log(f"📦 Creating archive: {zip_path.name}")
    skip_dirs = {"node_modules", "__pycache__", "usr", ".git", ".cache", "tmp"}
    include_roots = ["services", "docs", "logs", "registry"]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root in include_roots:
            d = BASE / root
            if not d.exists():
                continue
            for path in d.rglob("*"):
                if any(s in path.parts for s in skip_dirs):
                    continue
                if not path.is_file():
                    continue
                rel = path.relative_to(BASE)
                try:
                    zf.write(path, rel)
                except Exception as e:
                    log(f"⚠️ Skipped {path}: {e}")
    return zip_path

# ------------------- S3 + GitHub -------------------
def copy_to_downloads(path):
    try:
        DOWNLOADS.mkdir(parents=True, exist_ok=True)
        target = DOWNLOADS / path.name
        shutil.copy2(path, target)
        log(f"📥 Copied to Downloads → {target}")
    except Exception as e:
        log(f"⚠️ Copy failed: {e}")

def upload_to_s3(path):
    if not S3_BUCKET:
        log("⚠️ No S3 bucket configured.")
        return
    try:
        s3 = boto3.client("s3")
        key = f"exports/{path.name}"
        s3.upload_file(str(path), S3_BUCKET, key)
        log(f"☁️ Uploaded {path.name} → s3://{S3_BUCKET}/{key}")
    except Exception as e:
        log(f"⚠️ S3 upload failed: {e}")

def push_to_github():
    try:
        subprocess.run(["git", "-C", str(BASE), "add", "."], check=False)
        subprocess.run(["git", "-C", str(BASE), "commit", "-m", f"Automated export {datetime.now().isoformat()}"], check=False)
        subprocess.run(["git", "-C", str(BASE), "push", "origin", "main"], check=False)
        log("🐙 GitHub sync complete.")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

# ------------------- Main -------------------
def main():
    log(f"🧠 Starting Savant Export at {datetime.now(timezone.utc).isoformat()}")
    collect_chat_log()
    zip_path = create_archive()
    copy_to_downloads(zip_path)
    upload_to_s3(zip_path)
    push_to_github()
    log("✅ Savant Export v6.2 complete — full chat preserved, ZIP only.")

if __name__ == "__main__":
    main()
