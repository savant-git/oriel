#!/usr/bin/env python3
import json, zipfile, shutil, os
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home()/"savant"
CHAT_DIR = BASE/"chat_logs"; CHAT_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS = BASE/"exports";   EXPORTS.mkdir(parents=True, exist_ok=True)

def ask_path():
    print("📄 Enter path to conversations.json:")
    p = input("→ ").strip()
    return Path(p)

def choose_scope():
    print("\nChoose extraction scope:")
    print("1. Current chat only\n2. Project chats\n3. All chats")
    c = input("→ Select (1-3): ").strip()
    return {"1":"current","2":"project","3":"all"}.get(c,"current")

def format_chat(data,scope):
    out=[]
    for conv in data:
        title = conv.get("title") or "Untitled Chat"
        msgs = conv.get("mapping",{}).values()
        block=[f"\n\n=== {title} ===\n"]
        for m in msgs:
            msg=m.get("message")
            if not msg or "author" not in msg or "content" not in msg: continue
            role=msg["author"].get("role","system").upper()
            parts=msg["content"].get("parts",[])
            text="\n".join(p for p in parts if isinstance(p,str))
            if text.strip():
                block.append(f"\n[{role}]\n{text.strip()}\n")
        out.extend(block)
        if scope=="current": break
    return "\n".join(out)

def parse_json(path,scope):
    print(f"🧩 Parsing {path.name} …")
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    txt=format_chat(data,scope)
    ts=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_fp=CHAT_DIR/f"chat_full_{scope}_{ts}.txt"
    out_fp.write_text(txt,encoding="utf-8")
    print(f"✅ Saved formatted chat → {out_fp}")
    # remove raw json to save space
    try: os.remove(path)
    except Exception: pass
    return out_fp

def make_export(chat_fp):
    ts=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    zip_fp=EXPORTS/f"savant_full_export_{ts}.zip"
    print(f"📦 Creating export → {zip_fp}")
    with zipfile.ZipFile(zip_fp,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.write(chat_fp,chat_fp.relative_to(BASE))
    print("✅ Export complete and chat embedded.")
    return zip_fp

def main():
    path=ask_path()
    if not path.exists():
        print("❌ File not found.")
        return
    scope=choose_scope()
    chat_fp=parse_json(path,scope)
    make_export(chat_fp)

if __name__=="__main__":
    main()
