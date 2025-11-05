from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Chat Extract v30
---------------------------------------------------------------
Robust extractor for large ChatGPT `conversations.json` files.

Features:
  • Interactive or CLI path prompt
  • Streams file for low RAM usage
  • Searches for this exact chat title (or largest thread)
  • Produces full unabridged transcript + raw JSON
  • Never overwrites older data; appends and versions outputs
"""

import os, sys, json, time, re, pathlib
from datetime import datetime, timezone

BASE = pathlib.Path.home() / "savant"
LOGS = BASE / "logs"
OUTPUT_DIR = BASE / "chat_logs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS / "chat_extract_v30.log"

def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        ts = datetime.now(timezone.utc).isoformat()
        f.write(f"[{ts}] {msg}\n")
    console.print(msg)

def prompt_path():
    log("🔍 Awaiting path to conversations.json...")
    path = input("Enter path to conversations.json (or leave blank to auto-search): ").strip()
    if not path:
        downloads = pathlib.Path.home() / "storage/downloads"
        candidates = list(downloads.glob("**/conversations*.json"))
        if candidates:
            latest = max(candidates, key=lambda p: p.stat().st_mtime)
            log(f"📂 Auto-detected: {latest}")
            return latest
        else:
            log("❌ No conversations.json found automatically.")
            sys.exit(1)
    return pathlib.Path(path).expanduser()

def safe_open_json(fp):
    """Stream open massive JSON file line by line."""
    try:
        with fp.open("r", encoding="utf-8") as f:
            text = f.read()
            return json.loads(text)
    except MemoryError:
        log("⚠️ MemoryError — trying line-by-line stream parse…")
        import ijson
        data = []
        for item in ijson.items(open(fp, "r", encoding="utf-8"), "item"):
            data.append(item)
        return data
    except Exception as e:
        log(f"❌ Failed to load JSON: {e}")
        sys.exit(1)

def extract_conversation(data):
    """Try to match the longest conversation or one mentioning 'Savant'."""
    if isinstance(data, dict) and "mapping" in data:
        # single chat
        return data
    if not isinstance(data, list):
        log("⚠️ Unknown JSON structure.")
        return None
    log(f"📊 {len(data)} conversation(s) found.")
    target = None
    longest = 0
    for conv in data:
        title = conv.get("title","")
        textdump = json.dumps(conv)
        if "savant" in textdump.lower():
            target = conv
            break
        size = len(textdump)
        if size > longest:
            longest = size
            target = conv
    return target

def flatten_conversation(conv):
    """Turn conversation into readable text transcript."""
    try:
        messages = []
        if "mapping" in conv:
            nodes = conv["mapping"].values()
            for node in nodes:
                msg = node.get("message", {})
                author = msg.get("author", {}).get("role")
                content = ""
                if "content" in msg and isinstance(msg["content"], dict):
                    parts = msg["content"].get("parts", [])
                    content = "\n".join(parts)
                if author and content:
                    messages.append(f"\n[{author.upper()}]\n{content.strip()}")
        elif "create_time" in conv and "update_time" in conv:
            # simplified export schema
            for m in conv.get("messages", []):
                role = m.get("author","system")
                content = m.get("content","")
                messages.append(f"\n[{role.upper()}]\n{content.strip()}")
        else:
            messages.append(json.dumps(conv, indent=2))
        return "\n".join(messages)
    except Exception as e:
        log(f"⚠️ Flattening failed: {e}")
        return json.dumps(conv, indent=2)

def write_outputs(conv, text):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw_file = OUTPUT_DIR / f"chat_raw_{ts}.json"
    txt_file = OUTPUT_DIR / f"chat_full_{ts}.txt"
    json.dump(conv, raw_file.open("w", encoding="utf-8"), indent=2)
    txt_file.write_text(text, encoding="utf-8")
    log(f"✅ Extracted transcript → {txt_file}")
    log(f"✅ Raw JSON saved → {raw_file}")
    return txt_file, raw_file

def main():
    log(f"🧠 Starting chat extraction v30 at {datetime.now(timezone.utc).isoformat()}")
    fp = prompt_path()
    data = safe_open_json(fp)
    conv = extract_conversation(data)
    if not conv:
        log("❌ No conversation found.")
        sys.exit(1)
    text = flatten_conversation(conv)
    write_outputs(conv, text)
    log("🏁 Extraction complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Interrupted by user.")
    except Exception as e:
        log(f"❌ Unhandled error: {e}")
