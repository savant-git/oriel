#!/usr/bin/env python3
"""
⬢ Savant Archive-Export v200
Creates a visually rich, fully interactive HTML log of your conversations.
Includes syntax highlighting, dark/light mode, search, TOC, and perfect encoding.
"""

import os, re, json, zipfile, shutil, subprocess, html, boto3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE=Path.home()/ "savant"
LOGS=BASE/"logs"; CHAT_DIR=BASE/"chat_logs"; EXPORTS=BASE/"exports"
for d in (LOGS,CHAT_DIR,EXPORTS): d.mkdir(parents=True,exist_ok=True)
LOG_FILE=LOGS/"archive_export_v200.log"

def log(msg):
    ts=datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a",encoding="utf-8") as f:f.write(f"[{ts}] {msg}\n")
    print(msg)

def clean_text(t:str)->str:
    if not t: return ""
    t=re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]","",t)
    t=(t.replace("â€”","—").replace("â€“","–").replace("â€˜","‘")
       .replace("â€™","’").replace("â€œ","“").replace("â€�","”"))
    return html.escape(t.strip())

def safe_time(ts_raw):
    try:
        if not ts_raw: return None
        if isinstance(ts_raw,(int,float)) and 1000000000<ts_raw<20000000000:
            return datetime.fromtimestamp(ts_raw,timezone.utc)
    except Exception: pass
    return None

def format_code_blocks(text):
    """Detect triple-backtick code and wrap in <pre><code> blocks with language tag."""
    def repl(match):
        lang=match.group(1) or "plaintext"
        code=html.escape(match.group(2))
        return f"<pre><code class='language-{lang}'>{code}</code></pre>"
    return re.sub(r"```(\w*)\n([\s\S]*?)```",repl,text)

def parse_msgs(json_path,days:int):
    data=json.loads(Path(json_path).read_text(encoding="utf-8"))
    cutoff=datetime.now(timezone.utc)-timedelta(days=days)
    blocks,toc=[],[]; i=1
    for conv in data:
        title=clean_text(conv.get("title") or f"Conversation {i}")
        msgs=[]
        for node in (conv.get("mapping") or {}).values():
            msg=node.get("message") or {}
            ts=safe_time(msg.get("create_time"))
            if not ts or ts<cutoff: continue
            cont=msg.get("content") or {}; parts=cont.get("parts") or []
            role=(msg.get("author") or {}).get("role","system").lower()
            text=format_code_blocks("\n\n".join(str(p) for p in parts))
            if text: msgs.append((role,ts,text))
        if msgs:
            block=[f"<section id='b{i}'><h2>{title}</h2>"]
            for role,ts,txt in msgs:
                color=role
                local=ts.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                block.append(f"""
<div class='msg {color}'>
  <div class='meta'>{role.title()} — {local}</div>
  <div class='body'>{txt}</div>
</div>""")
            block.append("</section>")
            blocks.append("\n".join(block))
            toc.append(f"<li><a href='#b{i}'>{title}</a></li>")
            i+=1
    return blocks,toc

def build_html(blocks,toc):
    prism_css="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css"
    prism_js="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"
    addons_js="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"
    style=f"""
    <style>
    body{{font-family:'Inter',Arial,sans-serif;font-size:18pt;line-height:1.6;
         background:#111;color:#eee;margin:0;padding:0;max-width:1100px;margin:auto;}}
    header{{background:linear-gradient(90deg,#ffb300,#ff8f00);color:#111;padding:25px;
            position:sticky;top:0;z-index:1000;}}
    h1{{margin:0;font-size:32pt;}}
    #toc{{padding:20px;background:#222;border-radius:12px;}}
    #toc ul{{list-style:none;padding:0;margin:0;}}
    #toc li{{margin:8px 0;}}
    #toc a{{color:#ffd54f;text-decoration:none;}}
    #toc a:hover{{text-decoration:underline;}}
    .msg.user{{background:#1565c0;color:#fff;padding:14px;border-radius:10px;margin:12px 0;}}
    .msg.assistant{{background:#2e7d32;color:#fff;padding:14px;border-radius:10px;margin:12px 0;}}
    .msg.system{{background:#555;color:#fff;padding:14px;border-radius:10px;margin:12px 0;}}
    .meta{{font-size:14pt;color:#ccc;margin-bottom:4px;}}
    pre{{background:#000;padding:12px;border-radius:8px;overflow-x:auto;font-size:14pt;}}
    code{{font-family:'JetBrains Mono',monospace;}}
    #search{{width:100%;padding:10px;font-size:16pt;margin:15px 0;border-radius:8px;border:1px solid #444;}}
    #homebar{{position:fixed;bottom:0;left:0;right:0;background:#ffb300;color:#111;
             text-align:center;padding:20px;border-top:2px solid #333;}}
    #homebar a{{font-size:24pt;font-weight:bold;color:#111;text-decoration:none;}}
    </style>"""
    script=f"""
    <script>
    function filterChats() {{
      const q=document.getElementById('search').value.toLowerCase();
      document.querySelectorAll('.msg').forEach(el=>{{
        el.style.display=el.innerText.toLowerCase().includes(q)?'block':'none';
      }});
    }}
    function toggleTheme(){{
      const b=document.body;
      if(b.dataset.theme==='light'){{b.dataset.theme='dark';b.style.background='#111';b.style.color='#eee';}}
      else{{b.dataset.theme='light';b.style.background='#fff';b.style.color='#000';}}
    }}
    </script>
    """
    toc_html=f"<div id='toc'><input id='search' onkeyup='filterChats()' placeholder='🔍 Search...'><ul>{''.join(toc)}</ul></div>"
    footer="<div id='homebar'><a href='#top'>⬆ Home</a> | <a href='javascript:toggleTheme()'>☀️/🌙</a></div>"
    body=f"<header><h1>Savant Chat Log</h1></header><a name='top'></a>{toc_html}<hr>{''.join(blocks)}{footer}"
    return f"<html><head><meta charset='utf-8'><link rel='stylesheet' href='{prism_css}'><script src='{prism_js}'></script><script src='{addons_js}'></script>{style}{script}</head><body>{body}</body></html>"

def export_all(chat_fp):
    ts=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    arc=EXPORTS/f"savant_full_export_{ts}.zip"
    with zipfile.ZipFile(arc,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for folder in [BASE/"services",BASE/"chat_logs",BASE/"logs"]:
            for f in folder.rglob("*"):
                if f.is_file(): z.write(f,f.relative_to(BASE))
    log(f"📦 Archive → {arc}")
    dl=Path("/storage/emulated/0/Download")
    if not dl.exists(): dl=Path.home()/ "storage/downloads"
    dl.mkdir(parents=True,exist_ok=True)
    tgt=dl/arc.name; shutil.copy2(arc,tgt); log(f"📥 Copied → {tgt}")
    try:
        b=os.getenv("SAVANT_S3_BUCKET")
        if b:
            s3=boto3.client("s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
            s3.upload_file(str(arc),b,f"exports/{arc.name}")
            log(f"☁️ Uploaded → s3://{b}/exports/{arc.name}")
    except Exception as e: log(f"⚠️ S3 upload failed: {e}")

def main():
    print("How many days of messages to export (1–10)? ",end="")
    try: days=int(input().strip() or "1")
    except: days=1
    days=max(1,min(days,10))
    j=Path("/storage/emulated/0/Download/conversations.json")
    if not j.exists(): return log("❌ conversations.json not found in Downloads.")
    log(f"🧠 Building chat log from messages within last {days} day(s)…")
    blocks,toc=parse_msgs(j,days)
    html=build_html(blocks,toc)
    fp=CHAT_DIR/"chat_full_current.html"
    fp.write_text(html,encoding="utf-8")
    log(f"✅ Chat formatted → {fp}")
    export_all(fp)
    log("✅ Archive-Export v200 complete.")
