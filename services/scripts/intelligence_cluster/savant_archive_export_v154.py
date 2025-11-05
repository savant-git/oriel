from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Archive-Export v154
Filters individual messages by actual post time, not conversation creation.
Outputs UTF-8-safe HTML with refined 18 pt text & 24 pt Home button.
"""

import os, re, json, zipfile, shutil, subprocess, boto3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE=Path.home()/ "savant"
LOGS=BASE/"logs"; CHAT_DIR=BASE/"chat_logs"; EXPORTS=BASE/"exports"
for d in (LOGS,CHAT_DIR,EXPORTS): d.mkdir(parents=True,exist_ok=True)
LOG_FILE=LOGS/"archive_export_v154.log"

def log(msg):
    ts=datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a",encoding="utf-8") as f: f.write(f"[{ts}] {msg}\n")
    console.print(msg)

def clean_text(t:str)->str:
    t=(t or "").encode("utf-8","ignore").decode("utf-8","ignore")
    t=re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]","",t)
    t=t.replace("â€”","—").replace("â€“","–").replace("â€˜","‘").replace("â€™","’").replace("â€œ","“").replace("â€�","”")
    return t.strip()

def normalize(p): return clean_text(p if isinstance(p,str) else json.dumps(p,ensure_ascii=False))

# ---------------------------------------------------------------
# 1️⃣ Parse conversations.json and filter messages by timestamp
# ---------------------------------------------------------------
def parse_recent_msgs(json_path,days:int):
    data=json.loads(Path(json_path).read_text(encoding="utf-8"))
    cutoff=datetime.now(timezone.utc)-timedelta(days=days)
    blocks,toc=[],[]; i=1
    for conv in sorted(data,key=lambda c:c.get("create_time",0),reverse=True):
        title=clean_text(conv.get("title") or f"Conversation {i}")
        msgs=[]
        for node in (conv.get("mapping") or {}).values():
            msg=node.get("message") or {}
            ts_raw=msg.get("create_time")
            if not ts_raw: continue
            ts=datetime.fromtimestamp(ts_raw,timezone.utc)
            if ts<cutoff: continue
            cont=msg.get("content") or {}; parts=cont.get("parts") or []
            role=(msg.get("author") or {}).get("role","system").lower()
            text=" ".join(normalize(p) for p in parts)
            if text: msgs.append((role,ts,text))
        if msgs:
            block=[f"<a name='b{i}'></a>",f"<h2>{title}</h2>"]
            for role,ts,txt in msgs:
                color="user" if role=="user" else "assistant" if role=="assistant" else "system"
                block.append(f"<div class='msg {color}'><b>{role.title()}:</b> {txt}</div>")
            blocks.append("\n".join(block))
            toc.append(f"<li><a href='#b{i}'>{title}</a></li>")
            i+=1
    return blocks,toc

# ---------------------------------------------------------------
def format_html(blocks,toc):
    style="""
    <style>
    body{font-family:Arial,Helvetica,sans-serif;font-size:18pt;line-height:1.6;
         background:#fafafa;color:#222;padding:20px;max-width:900px;margin:auto;}
    h1,h2{color:#111;border-bottom:1px solid #ddd;padding-bottom:6px;}
    ul{list-style:none;padding:0;} ul li{margin:6px 0;}
    a{text-decoration:none;color:#0077cc;} a:hover{text-decoration:underline;}
    .msg.user{background:#b3e5fc;padding:12px;border-radius:8px;margin:10px 0;}
    .msg.assistant{background:#c8e6c9;padding:12px;border-radius:8px;margin:10px 0;}
    .msg.system{background:#eeeeee;padding:12px;border-radius:8px;margin:10px 0;}
    #homebar{position:fixed;bottom:0;left:0;right:0;background:white;padding:20px;
             text-align:center;border-top:1px solid #ccc;}
    #homebar a{font-size:24pt;font-weight:bold;color:#222;text-decoration:none;}
    </style>
    """
    toc_html="<ul>"+"\n".join(toc)+"</ul>"
    footer="<div id='homebar'><a href='#top'>⬆ Home</a></div>"
    return f"<html><head><meta charset='utf-8'><title>Savant Chat Log</title>{style}</head><body><a name='top'></a><h1>Savant Chat Log</h1>{toc_html}<hr>"+"\n<hr>\n".join(blocks)+footer+"</body></html>"

# ---------------------------------------------------------------
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
    try:
        subprocess.run(["git","-C",str(BASE),"add","."],check=True)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Auto export {datetime.now().isoformat()}"],check=True)
        subprocess.run(["git","-C",str(BASE),"push"],check=True)
        log("🐙 GitHub push successful.")
    except Exception as e: log(f"⚠️ GitHub push failed: {e}")
    try:
        subprocess.run(["am","start","-a","android.intent.action.VIEW","-d",f"file://{chat_fp}"],check=False)
        log("🌐 Opened in mobile browser.")
    except Exception as e: log(f"⚠️ Viewer launch failed: {e}")

# ---------------------------------------------------------------
def main():
    console.print("How many days of messages to export (1-10)? ",end="")
    try: days=int(input().strip() or "1")
    except: days=1
    days=max(1,min(days,10))
    j=Path("/storage/emulated/0/Download/conversations.json")
    if not j.exists(): return log("❌ conversations.json not found in Downloads.")
    log(f"🧠 Building chat log from messages within last {days} day(s)…")
    blocks,toc=parse_recent_msgs(j,days)
    html=format_html(blocks,toc)
    fp=CHAT_DIR/"chat_full_current.html"
    fp.write_text(html,encoding="utf-8")
    log(f"✅ Chat formatted → {fp}")
    export_all(fp)
    log("✅ Archive-Export v154 complete.")

if __name__=="__main__":
    try: main()
    except Exception as e: log(f"❌ Fatal error: {e}")
