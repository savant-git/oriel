from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Chat Extract v31
---------------------------------------------------------------
Automatically locates the latest ChatGPT `conversations.json`
export (no user input required). Extracts this chat fully and
verbatim to:
  • ~/savant/chat_logs/chat_full_<timestamp>.txt
  • ~/savant/chat_logs/chat_raw_<timestamp>.json
"""
import os, json, pathlib, sys
from datetime import datetime, timezone

BASE = pathlib.Path.home() / "savant"
LOGS = BASE / "logs"
OUT = BASE / "chat_logs"
LOGS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
LOG = LOGS / "chat_extract_v31.log"

def log(msg):
    LOG.open("a", encoding="utf-8").write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    console.print(msg)

def auto_find_json():
    """Locate newest conversations.json file in Downloads or /storage"""
    search_roots = [
        pathlib.Path.home() / "storage/downloads",
        pathlib.Path("/data/data/com.termux/files/home/storage/downloads"),
        pathlib.Path("/storage/emulated/0/Download"),
        pathlib.Path("/sdcard/Download")
    ]
    candidates = []
    for root in search_roots:
        if root.exists():
            for f in root.rglob("conversations*.json"):
                candidates.append(f)
    if not candidates:
        log("❌ No conversations.json found in known locations.")
        sys.exit(1)
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    log(f"📂 Found latest export: {latest}")
    return latest

def extract_latest(fp):
    try:
        data = json.load(open(fp, "r", encoding="utf-8"))
    except Exception as e:
        log(f"❌ JSON load failed: {e}")
        sys.exit(1)
    log(f"📊 {len(data)} conversation(s) detected.")
    # Find conversation mentioning "savant" or largest
    target = None
    largest = 0
    for conv in data:
        dump = json.dumps(conv)
        if "savant" in dump.lower():
            target = conv
            break
        if len(dump) > largest:
            target = conv
            largest = len(dump)
    if not target:
        log("❌ No conversation matched criteria.")
        sys.exit(1)
    # Save results
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw = OUT / f"chat_raw_{ts}.json"
    txt = OUT / f"chat_full_{ts}.txt"
    json.dump(target, open(raw, "w", encoding="utf-8"), indent=2)
    txt.write_text(json.dumps(target, indent=2), encoding="utf-8")
    log(f"✅ Raw JSON saved → {raw}")
    log(f"✅ Full text saved → {txt}")
    log("🏁 Chat extraction complete.")
    return txt, raw

def main():
    log("🧠 Savant Chat Extract v31 — automated mode start")
    fp = auto_find_json()
    extract_latest(fp)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Interrupted by user.")
    except Exception as e:
        log(f"❌ Unhandled error: {e}")
