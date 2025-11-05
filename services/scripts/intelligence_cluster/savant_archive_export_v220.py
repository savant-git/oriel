from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive+Export v220
- Full current chat extraction, formatting, export (same pipeline as v210)
- Enhanced UI aesthetics with Savant brand (matte black, kinetic typography, GSAP)
- Supports TOC, animated transitions, subtle parallax, dark glow effect
"""

import os, sys, json, re, html, zipfile, shutil, hashlib, traceback
from datetime import datetime, timezone
from pathlib import Path

BASE   = Path.home()/ "savant"
LOGS   = BASE/"logs"
CHAT   = BASE/"chat_logs"
EXPORT = BASE/"exports"
DL     = Path("/storage/emulated/0/Download") if Path("/storage/emulated/0/Download").exists() else (Path.home()/ "storage/downloads")
LOGS.mkdir(parents=True, exist_ok=True)
CHAT.mkdir(parents=True, exist_ok=True)
EXPORT.mkdir(parents=True, exist_ok=True)
DL.mkdir(parents=True, exist_ok=True)
LOG    = LOGS/"archive_export_v220.log"

def log(msg):
    ts=datetime.now(timezone.utc).isoformat()
    LOG.open("a").write(f"[{ts}] {msg}\n")
    console.print(msg)

def find_conversations_json():
    for p in [
        Path("/storage/emulated/0/Download/conversations.json"),
        Path.home()/ "storage/downloads/conversations.json",
        CHAT/"conversations.json"
    ]:
        if p.exists(): return p
    return None

def load_big_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        log(f"⚠️ JSON load error: {e}")
        raise

def normalize_messages(conv):
    out=[]
    mapping=conv.get("mapping") or {}
    for node in mapping.values():
        msg=node.get("message")
        if not msg: continue
        role=(msg.get("author") or {}).get("role") or "assistant"
        content=msg.get("content")
        if isinstance(content,dict) and "parts" in content:
            text="\n".join(content["parts"])
        else:
            text=str(content)
        out.append((role,text,msg.get("create_time")))
    out.sort(key=lambda x:x[2] or 0)
    return out

def extract_current_chat_full(data):
    convs=data.get("conversations") if isinstance(data,dict) else data
    conv=max(convs,key=lambda c:(c.get("update_time") or c.get("create_time") or 0))
    return conv, normalize_messages(conv)

# --- Savant aesthetic HTML ---
CSS = """
:root {
  --bg: #0a0a0b;
  --surface: #101012;
  --ink: #e8e8e8;
  --accent1: #d7b46a;
  --accent2: #8b8b8b;
  --user: #6ab4ff;
  --ai: #8cffb4;
  --code-bg: #0f0f13;
}
*{box-sizing:border-box;}
html,body{height:100%;margin:0;background:var(--bg);color:var(--ink);font:400 15pt "Inter",system-ui,-apple-system,Segoe UI,Roboto;}
.container{max-width:1200px;margin:auto;padding:40px;}
h1{font:900 30pt "Orbitron",sans-serif;text-transform:uppercase;letter-spacing:3px;margin-bottom:16px;background:linear-gradient(90deg,var(--accent1),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.toc{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin-bottom:32px;backdrop-filter:blur(8px);}
.toc a{display:block;color:var(--accent1);text-decoration:none;padding:8px 12px;border-radius:8px;transition:background 0.2s;}
.toc a:hover{background:rgba(255,255,255,0.05);}
.block{margin-bottom:36px;padding:24px;border-left:6px solid transparent;background:var(--surface);border-radius:12px;box-shadow:0 0 25px rgba(0,0,0,0.35);}
.role-user{border-color:var(--user);}
.role-ai{border-color:var(--ai);}
pre{background:var(--code-bg);padding:14px;border-radius:8px;overflow-x:auto;font-family:ui-monospace,Consolas,Menlo;}
.footerbar{position:fixed;bottom:0;left:0;right:0;background:rgba(15,15,18,0.95);padding:16px;text-align:center;border-top:1px solid rgba(255,255,255,0.1);}
.homebtn{font:700 20pt "Orbitron";background:linear-gradient(90deg,var(--accent1),var(--accent2));border:none;padding:10px 20px;color:#000;border-radius:8px;cursor:pointer;}
.homebtn:hover{filter:brightness(1.1);}
hr{border:0;border-top:1px solid rgba(255,255,255,0.08);}
"""

JS = """
document.addEventListener("DOMContentLoaded",()=>{
  if(window.gsap){
    gsap.from("h1",{duration:1.4,y:-60,opacity:0,ease:"power3.out"});
    gsap.from(".block",{duration:1,y:60,opacity:0,stagger:0.08,ease:"power2.out"});
  }
});
"""

def html_escape(s): return html.escape(s, quote=False)

def render_blocks(conv_title, items):
    toc=[]; blocks=[]
    for i,(role,content,ct) in enumerate(items,1):
        ident=f"b{i}"
        head=content.strip().splitlines()[0:1]
        topic=head[0][:60] if head else f"{role} {i}"
        toc.append(f'<a href="#{ident}">{i}. {html_escape(topic)}</a>')
        role_cls="role-user" if role=="user" else "role-ai"
        blocks.append(f"""
<section id="{ident}" class="block {role_cls}">
<div class="meta"><strong>{role.upper()}</strong></div>
<div class="content">{html_escape(content).replace("\\n","<br>")}</div>
</section>
""")
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_escape(conv_title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Orbitron:wght@600;900&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<style>{CSS}</style></head>
<body><div class="container">
<h1 id="top">{html_escape(conv_title)}</h1>
<div class="toc"><strong>Table of Contents</strong><hr>{"".join(toc)}</div>
{"".join(blocks)}
</div>
<div class="footerbar"><button class="homebtn" onclick="window.scrollTo({top:0,behavior:'smooth'})">Home</button></div>
<script>{JS}</script>
</body></html>"""

def main():
    log("🧠 Savant Archive+Export v220 started.")
    cj=find_conversations_json()
    if not cj:
        log("❌ No conversations.json found.")
        return
    data=load_big_json(cj)
    conv,msgs=extract_current_chat_full(data)
    title=conv.get("title") or "Savant Chat Export"
    html_out=CHAT/"chat_full_current.html"
    txt_out=CHAT/"chat_full_current.txt"
    html_doc=render_blocks(title,msgs)
    html_out.write_text(html_doc,encoding="utf-8")
    txt_out.write_text("\n\n".join(f"{r.upper()}: {t}" for r,t,_ in msgs),encoding="utf-8")
    log(f"✅ HTML saved: {html_out}")
    log(f"✅ TXT saved: {txt_out}")
    zipf=EXPORT/f"savant_full_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(zipf,"w",zipfile.ZIP_DEFLATED) as z:
        for p in [html_out,txt_out]: z.write(p,p.name)
    shutil.copy2(zipf, DL/zipf.name)
    log(f"📦 Copied ZIP to Downloads: {DL/zipf.name}")
    log("🏁 Done — Savant brand archive complete.")
