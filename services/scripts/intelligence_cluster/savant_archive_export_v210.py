from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
import os, sys, json, re, zipfile, shutil, hashlib, time, html, textwrap, traceback
from pathlib import Path
from datetime import datetime, timezone, timedelta

# -----------------------
# Config & paths
# -----------------------
BASE   = Path.home()/ "savant"
LOGS   = BASE/"logs"
CHAT   = BASE/"chat_logs"
EXPORT = BASE/"exports"
DL     = Path("/storage/emulated/0/Download") if Path("/storage/emulated/0/Download").exists() else (Path.home()/ "storage/downloads")
ENV    = BASE/".env"
LOGS.mkdir(parents=True, exist_ok=True)
CHAT.mkdir(parents=True, exist_ok=True)
EXPORT.mkdir(parents=True, exist_ok=True)
DL.mkdir(parents=True, exist_ok=True)

LOG    = LOGS/"archive_export_v210.log"
NOWUTC = lambda: datetime.now(timezone.utc).isoformat()

# -----------------------
# Logging
# -----------------------
def log(msg):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{NOWUTC()}] {msg}\n")
    finally:
        console.print(msg)

# -----------------------
# Env loader (.env with KEY=VALUE lines; ignores comments)
# -----------------------
def load_env():
    if not ENV.exists():
        log("⚠️  No .env found; S3/Git may be skipped.")
        return
    for ln in ENV.read_text(errors="ignore").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln: 
            continue
        k,v = ln.split("=",1)
        k = k.strip(); v = v.strip().strip('"').strip("'")
        # basic sanity: skip illegal keys
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', k):
            os.environ[k]=v

# -----------------------
# Robust JSON loader (conversations.json)
# -----------------------
def find_conversations_json():
    # Prefer explicit path via ENV; otherwise Downloads; fallback to chat_logs/
    cand = [
        os.environ.get("SAVANT_CONVERSATIONS_JSON","").strip(),
        "/storage/emulated/0/Download/conversations.json",
        str(Path.home()/ "storage/downloads/conversations.json"),
        str(CHAT/"conversations.json"),
    ]
    for c in cand:
        if c and Path(c).exists() and Path(c).is_file():
            return Path(c)
    return None

def load_big_json(path):
    data = path.read_text(encoding="utf-8", errors="ignore")
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        # try repairing common BOM/encoding artifacts
        data = data.replace("\ufeff","").replace("\u0000","")
        return json.loads(data)

# -----------------------
# Chat extraction
# -----------------------
def is_current_chat(item):
    # Heuristic: prefer the newest conversation updated_at / create_time
    ts = item.get("update_time") or item.get("create_time") or 0
    try:
        return float(ts)
    except Exception:
        return 0.0

def normalize_messages(conv):
    """Return an array of (role, content, created_at) tuples; handle multiple export schemas."""
    out = []
    # OpenAI ChatGPT export formats differ; handle known shapes:
    # - conv["mapping"] dict with nodes; each node has "message": {"author": {"role"}, "content": {"parts":[str]}, "create_time": float}
    # - or conv["messages"] list with {author:{role}, content: str|list, create_time: float}
    if isinstance(conv.get("messages"), list):
        for m in conv["messages"]:
            role = (m.get("author") or {}).get("role") or m.get("role") or "assistant"
            ct   = m.get("create_time") or m.get("timestamp") or m.get("update_time")
            parts= m.get("content")
            if isinstance(parts, list):
                text = "\n".join([p.get("text",str(p)) if isinstance(p,dict) else str(p) for p in parts])
            else:
                text = parts if isinstance(parts,str) else json.dumps(parts, ensure_ascii=False)
            out.append((role, text, ct))
        return out

    mapping = conv.get("mapping") or {}
    for node in mapping.values():
        msg = node.get("message")
        if not msg: 
            continue
        role = (msg.get("author") or {}).get("role") or msg.get("role") or "assistant"
        ct   = msg.get("create_time") or msg.get("timestamp") or msg.get("update_time")
        content = msg.get("content")
        text = ""
        if isinstance(content, dict) and "parts" in content:
            parts = content.get("parts") or []
            text = "\n".join([str(p) for p in parts])
        elif isinstance(content, list):
            text = "\n".join([p.get("text",str(p)) if isinstance(p,dict) else str(p) for p in content])
        elif isinstance(content, str):
            text = content
        else:
            text = json.dumps(content, ensure_ascii=False)
        out.append((role, text, ct))
    # sort by timestamp where possible
    def safe_ts(t):
        try:
            return float(t)
        except Exception:
            return 0.0
    out.sort(key=lambda t: safe_ts(t[2]))
    return out

def extract_current_chat_full(conversations):
    """Always FULL current chat (verbatim)."""
    if isinstance(conversations, dict) and "conversations" in conversations:
        convs = conversations["conversations"]
    elif isinstance(conversations, list):
        convs = conversations
    else:
        convs = []

    if not convs:
        raise RuntimeError("No conversations in export.")

    # pick newest by update_time / create_time
    conv = max(convs, key=is_current_chat)
    messages = normalize_messages(conv)
    return conv, messages

# -----------------------
# Formatting (HTML+TXT)
# -----------------------
CSS = """
:root {
  --bg:#0e0f12; --ink:#e6e6e6; --muted:#9ba3af;
  --user:#cde8ff; --ai:#d1f7c4; --accent:#f8b84e; --accent2:#ff9a1f;
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0; font: 400 14pt/1.6 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";}
a{color:var(--accent)}
.container{max-width:1100px; margin:0 auto; padding:28px}
header{position:sticky;top:0;background:linear-gradient(180deg,#0e0f12 70%,#0e0f1200); z-index:10}
h1{font-size:28pt;margin:8px 0;color:var(--ink);letter-spacing:.3px}
.toc{background:#14161b;border:1px solid #1e2633;border-radius:16px;padding:16px;margin:16px 0}
.toc a{display:block;text-decoration:none;padding:8px 10px;border-radius:10px;color:var(--ink)}
.toc a:hover{background:#1b2230}
.block{background:#101319;border:1px solid #1b2230;border-radius:18px;padding:18px;margin:18px 0; overflow:hidden}
.meta{color:var(--muted);font-size:12pt;margin-bottom:6px}
.role-user{background:rgba(205,232,255,.06); border-left:6px solid #77baf5}
.role-ai{background:rgba(209,247,196,.06); border-left:6px solid #7ddc80}
pre, code{font: 500 12pt/1.5 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New"; color:#e6e6e6; background:#0a0b0f}
pre{white-space:pre-wrap;word-break:break-word;border:1px solid #1f2633;border-radius:12px;padding:14px;margin:12px 0;overflow:auto}
kbd{font:500 11pt ui-monospace;background:#212734;border:1px solid #2c3444;border-bottom-width:3px;border-radius:6px;padding:0 6px;color:#d8dee9}
.footerbar{position:fixed;left:0;right:0;bottom:0;background:#0f1116;border-top:1px solid #1d2330;padding:14px;display:flex;justify-content:center}
.homebtn{font-size:24pt;background:linear-gradient(90deg,var(--accent),var(--accent2));color:#191b20;padding:8px 18px;border:none;border-radius:12px;font-weight:700;cursor:pointer}
.homebtn:hover{filter:brightness(1.05)}
blockquote{border-left:4px solid #2a3344;padding-left:10px;color:#c9d2e2}
hr{border:0;border-top:1px solid #232b3a;margin:24px 0}
"""

def html_escape(s:str)->str:
    return html.escape(s, quote=False)

def md_code_to_html(s:str)->str:
    # Very simple fence detection for ```lang ... ```
    lines = s.splitlines()
    out=[]; fence=False; buff=[]
    fence_lang=""
    for ln in lines:
        if ln.strip().startswith("```"):
            if not fence:
                fence=True; fence_lang=ln.strip().strip("`").strip()
                if fence_lang and fence_lang!="```": fence_lang=fence_lang
                buff=[]
            else:
                code = "\n".join(buff)
                out.append(f"<pre><code>{html_escape(code)}</code></pre>")
                fence=False; buff=[]; fence_lang=""
        else:
            (buff if fence else out).append(html_escape(ln))
    if buff: # dangling fence
        out.append(f"<pre><code>{html_escape('\n'.join(buff))}</code></pre>")
    return "\n".join(out)

def render_blocks_as_html(conv_title, items):
    # Build TOC & blocks
    toc = []
    body = []
    for idx, (role, content, ct) in enumerate(items, start=1):
        # Label for block
        block_id = f"b{idx:04d}"
        # Name from first line (fallback to role + idx)
        first_line = (content or "").strip().splitlines()[0:1]
        topic = (first_line[0].strip() if first_line else f"{role} {idx}").replace("<","&lt;")[:120]
        toc.append(f'<a href="#{block_id}">{idx}. {topic}</a>')
        # Role style
        role_class = "role-user" if role=="user" else "role-ai"
        # Convert markdown code fences
        html_body = md_code_to_html(content or "")
        stamp = ""
        try:
            ts = float(ct) if ct is not None else 0.0
            stamp = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC") if ts>0 else ""
        except Exception:
            stamp=""
        body.append(
          f'<section id="{block_id}" class="block {role_class}">'
          f'<div class="meta">{role.upper()} {f"• {stamp}" if stamp else ""}</div>'
          f'{html_body}'
          f'</section>'
        )
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_escape(conv_title or "Savant Chat Export")}</title>
<style>{CSS}</style>
</head><body>
<header class="container">
  <h1 id="top">{html_escape(conv_title or "Savant Chat Export")}</h1>
  <div class="toc">
    <strong>Table of Contents</strong>
    {' '.join(toc) if toc else '<div>(empty)</div>'}
  </div>
</header>
<main class="container">
  {"".join(body)}
</main>
<div class="footerbar">
  <button class="homebtn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">Home</button>
</div>
</body></html>
"""

def render_txt(items):
    out=[]
    for idx,(role,content,ct) in enumerate(items, start=1):
        out.append(f"{'='*80}\n[{idx}] {role.upper()} @ {ct}\n{'-'*80}\n{content}\n")
    return "\n".join(out)

# -----------------------
# Export packaging
# -----------------------
def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def zip_path()->Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return EXPORT/f"savant_full_export_{ts}.zip"

def create_zip(payload_paths):
    zf = zip_path()
    with zipfile.ZipFile(zf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in payload_paths:
            p = Path(p)
            if p.is_file():
                # path relative inside ZIP
                rel = p.relative_to(BASE) if BASE in p.parents or p == BASE else p.name
                z.write(p, rel)
    return zf

def copy_to_downloads(fp:Path):
    try:
        DL.mkdir(parents=True, exist_ok=True)
        tgt = DL/fp.name
        shutil.copy2(fp, tgt)
        log(f"📥 Copied to Downloads → {tgt}")
    except Exception as e:
        log(f"⚠️  Copy to Downloads failed: {e}")

def s3_upload(fp:Path):
    bkt = os.environ.get("SAVANT_S3_BUCKET","").strip()
    if not bkt:
        log("☁️  No S3 bucket configured; skipping S3 upload.")
        return
    try:
        import boto3
        s3 = boto3.client("s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_DEFAULT_REGION","us-east-1"))
        key=f"exports/{fp.name}"
        s3.upload_file(str(fp), bkt, key)
        log(f"☁️  Uploaded to s3://{bkt}/{key}")
    except Exception as e:
        log(f"⚠️  S3 upload failed: {e}")

def ensure_git():
    # Return True if repo exists and remote is set
    import subprocess
    try:
        subprocess.run(["git","-C",str(BASE), "status"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def git_push_zip(fp:Path):
    # Ensure ≤ 50MB for GitHub; if larger, re-zip lighter contents
    import subprocess, math, tempfile
    SIZE = fp.stat().st_size
    if SIZE > 50*1024*1024:
        log(f"⚠️  ZIP is {SIZE/1024/1024:.1f} MB > 50 MB; creating slim ZIP for GitHub push.")
        # Slim: include chat HTML+TXT and manifests only
        slim = fp.with_name(fp.stem + "_slim.zip")
        with zipfile.ZipFile(slim, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in [CHAT/"chat_full_current.html", CHAT/"chat_full_current.txt"]:
                if p.exists(): z.write(p, p.relative_to(BASE))
        fp = slim
        log(f"✅ Slim ZIP ready → {fp.name} ({fp.stat().st_size/1024/1024:.1f} MB)")
    try:
        subprocess.run(["git","-C",str(BASE),"add",str(fp.relative_to(BASE))], check=True)
        subprocess.run(["git","-C",str(BASE),"commit","-m",f"Auto export {datetime.now().isoformat()}"], check=True)
        subprocess.run(["git","-C",str(BASE),"push","-u","origin","main"], check=True)
        log("🐙 GitHub push successful.")
    except Exception as e:
        log(f"⚠️  GitHub push failed: {e}")

# -----------------------
# MAIN
# -----------------------
def main():
    console.print("✨ Savant environment ready — Archive+Export v210")
    load_env()
    # 1) conversations.json
    cj = find_conversations_json()
    if not cj:
        log("❌ No conversations.json found. Place it in Downloads or set SAVANT_CONVERSATIONS_JSON in .env.")
        sys.exit(1)

    # 2) Load + extract FULL current chat
    log("🧠 Loading conversations.json …")
    data = load_big_json(cj)
    conv, msgs = extract_current_chat_full(data)
    conv_title = conv.get("title") or "Savant Chat Export"

    # 3) Format HTML & TXT
    log("🧩 Formatting chat (HTML+TXT)…")
    html_path = CHAT/"chat_full_current.html"
    txt_path  = CHAT/"chat_full_current.txt"

    html_doc = render_blocks_as_html(conv_title, msgs)
    html_path.write_text(html_doc, encoding="utf-8")
    txt_path.write_text(render_txt(msgs), encoding="utf-8")

    log(f"✅ Wrote HTML → {html_path}")
    log(f"✅ Wrote TXT  → {txt_path}")

    # 4) Bundle ZIP (include scripts + logs + chat HTML/TXT)
    payload = []
    for p in [html_path, txt_path]:
        payload.append(p)
    # Important project dirs
    for root in [BASE/"services", BASE/"ui", CHAT, LOGS]:
        if root.exists():
            for fp in root.rglob("*"):
                if fp.is_file():
                    payload.append(fp)

    log("📦 Creating archive…")
    zf = create_zip(payload)
    log(f"✅ Archive complete → {zf} (SHA256={sha256(zf)})")

    # 5) Copy to Downloads
    copy_to_downloads(zf)

    # 6) Upload to S3 (full ZIP)
    s3_upload(zf)

    # 7) GitHub push (slim ZIP if >50 MB)
    if ensure_git():
        git_push_zip(zf)
    else:
        log("🐙 Git repo not initialized at ~/savant; skipping GitHub push.")

    log("🏁 Archive+Export v210 finished.")
    rule_status("✅ Done.", "ok")
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Fatal error: {e}\n{traceback.format_exc()}")
        sys.exit(1)
