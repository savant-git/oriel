#!/usr/bin/env python3
"""
⬢ Savant Extract v200
Full verbatim extractor for ChatGPT conversations.json, preserving formatting,
code blocks, and both sides of the conversation. Integrates directly with
the Savant export pipeline (savant-export).
"""

import os, json, sys, time, zipfile, shutil, datetime, tempfile, subprocess
from pathlib import Path
from html import escape

# --- CONFIG -------------------------------------------------------
BASE     = Path.home() / "savant"
CHAT_DIR = BASE / "chat_logs"
LOGS     = BASE / "logs"
EXPORTS  = BASE / "exports"
LOG_FILE = LOGS / "extract_v200.log"

for d in [CHAT_DIR, LOGS, EXPORTS]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

# --- UTILITY ------------------------------------------------------
def ask_path():
    print()
    print("📄 Enter path to conversations.json:")
    p = input("→ ").strip()
    fp = Path(p).expanduser()
    if not fp.exists():
        print("❌ File not found.")
        sys.exit(1)
    return fp

def ask_days():
    while True:
        try:
            days = int(input("How many days of messages to export (1-10)? ").strip())
            if 1 <= days <= 10:
                return days
        except ValueError:
            pass
        print("⚠️ Enter a number between 1 and 10.")

# --- HTML RENDERING ENGINE ---------------------------------------
def render_message(role, content, timestamp):
    color = "#a2d2ff" if role == "user" else "#b9fbc0"
    safe = escape(content).replace("\n", "<br>")
    return f"""
    <div style="background:{color};padding:15px;margin:8px;border-radius:8px;line-height:1.5;">
      <strong>{role.upper()}</strong> <small>{timestamp}</small><br>
      {safe}
    </div>
    """

def render_html(messages):
    html = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
            "<title>Savant Chat Export</title>",
            "<style>body{font-family:sans-serif;font-size:18px;margin:20px;} pre{background:#222;color:#eee;padding:10px;border-radius:6px;overflow:auto;} .toc a{text-decoration:none;color:#000;} .home{position:fixed;bottom:0;left:0;right:0;background:white;padding:20px;text-align:center;border-top:1px solid #ccc;font-size:24px;} </style>",
            "</head><body>"]
    html.append("<h1>🧠 Savant Chat Archive</h1><div class='toc'><h2>Table of Contents</h2><ul>")
    for i, m in enumerate(messages):
        html.append(f"<li><a href='#block_{i}'>Exchange {i+1} — {m['role'].capitalize()}</a></li>")
    html.append("</ul></div>")
    for i, m in enumerate(messages):
        html.append(f"<a id='block_{i}'></a>")
        html.append(render_message(m['role'], m['content'], m['timestamp']))
    html.append("<div class='home'><a href='#top'>🏠 Home</a></div>")
    html.append("</body></html>")
    return "\n".join(html)

# --- JSON PARSER -------------------------------------------------
def parse_conversations(json_path, days_back):
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(days=days_back)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_msgs = []
    for conv in data:
        mapping = conv.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message")
            if not msg or not msg.get("author") or not msg.get("content"):
                continue
            parts = msg["content"].get("parts", [])
            if not parts: continue
            ts = msg.get("create_time") or conv.get("update_time") or conv.get("create_time")
            try:
                timestamp = datetime.datetime.fromtimestamp(float(ts), tz=datetime.timezone.utc)
            except Exception:
                timestamp = now
            if timestamp < cutoff:
                continue
            all_msgs.append({
                "role": msg["author"]["role"],
                "content": "\n".join(parts),
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
    all_msgs.sort(key=lambda m: m["timestamp"])
    return all_msgs

# --- SAVE OUTPUT -------------------------------------------------
def save_outputs(messages):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_file = CHAT_DIR / f"chat_full_current_{ts}.txt"
    html_file = CHAT_DIR / f"chat_full_current_{ts}.html"

    # TXT
    with txt_file.open("w", encoding="utf-8") as f:
        for m in messages:
            f.write(f"[{m['timestamp']}] {m['role'].upper()}:\n{m['content']}\n\n")

    # HTML
    html_file.write_text(render_html(messages), encoding="utf-8")

    log(f"✅ Saved chat log → {txt_file}")
    log(f"✅ Saved HTML → {html_file}")
    return txt_file, html_file

# --- EXPORT INTEGRATION ------------------------------------------
def trigger_export():
    export_script = BASE / "services/scripts/intelligence_cluster/export_cluster_v87.py"
    if not export_script.exists():
        log("⚠️ Export script not found. Skipping.")
        return
    try:
        log("🚀 Running savant-export pipeline...")
        subprocess.run(["python3", str(export_script)], check=True)
        log("✅ Export pipeline finished.")
    except Exception as e:
        log(f"⚠️ Export pipeline failed: {e}")

# --- MAIN ---------------------------------------------------------
def main():
    print("✨ Savant Extract v200 — Verbatim Mode")
    json_path = ask_path()
    days = ask_days()

    log(f"🧠 Extracting from {json_path}, last {days} days")
    messages = parse_conversations(json_path, days)
    if not messages:
        log("❌ No messages found in selected range.")
        sys.exit(0)

    txt_file, html_file = save_outputs(messages)
    log("🧩 Inserting chat log into export pipeline...")
    trigger_export()
    log("🏁 Savant Extract v200 complete.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Fatal error: {e}")
