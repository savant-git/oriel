from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Extract v60
Ensures extract pipeline callable by `savant-extract` or internally by `savant-archive`.
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
CHAT = BASE / "chat_logs"
LOGS.mkdir(parents=True, exist_ok=True)
CHAT.mkdir(parents=True, exist_ok=True)
LOG = LOGS / "chat_extract_v60.log"

def log(m):
    LOG.open("a").write(f"[{datetime.now(timezone.utc).isoformat()}] {m}\n")

def find_json():
    for p in [
        Path("/storage/emulated/0/Download/conversations.json"),
        Path.home() / "storage/downloads/conversations.json",
        CHAT / "conversations.json",
    ]:
        if p.exists():
            return p
    return None

def main():
    log("🧠 Starting chat extraction")
    src = find_json()
    if not src:
        rule_status("❌ conversations.json not found", "error")
        return
    raw = json.loads(src.read_text(encoding="utf-8", errors="ignore"))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = CHAT / f"chat_raw_current_{stamp}.json"
    dest.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
    log(f"✅ Saved raw JSON → {dest}")
    rule_status(f"✅ Chat extracted: {dest}", "ok")

if __name__ == "__main__":
    main()
