from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧠  SAVANT STANDALONE RUNTIME INTERFACE  (SSRI v1.0)
────────────────────────────────────────────────────
Interactive console that routes natural language input
to Savant’s internal modules and OpenAI runtime.
"""
import os, subprocess, shlex, json, readline, requests
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home()/"savant"
LOG  = ROOT/"logs"/"ssri_console.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    with open(LOG,"a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def run_cmd(cmd):
    try:
        console.print(f"⚙️  Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        rule_status(f"❌  Command failed: {e}", "error")

def ai_response(prompt:str)->str:
    key=os.getenv("OPENAI_API_KEY")
    proj=os.getenv("OPENAI_PROJECT")
    if not key:
        return "❌  No API key loaded."
    headers={"Authorization":f"Bearer {key}"}
    if proj: headers["OpenAI-Project"]=proj
    payload={
        "model":"gpt-4o-mini",
        "messages":[
            {"role":"system","content":"You are the Savant AI runtime. Respond concisely and clearly."},
            {"role":"user","content":prompt}
        ]
    }
    try:
        r=requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=payload,timeout=60)
        if r.status_code!=200:
            return f"[Error {r.status_code}] {r.text[:160]}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Connection error: {e}"

def main():
    console.print("\n🚀 SAVANT STANDALONE RUNTIME INTERFACE — SSRI v1.0")
    console.print("Type 'help' for guidance or 'exit' to leave.\n")
    while True:
        try:
            cmd=input("savant > ").strip()
        except (EOFError,KeyboardInterrupt):
            console.print("\n👋 Goodbye.")
            break
        if not cmd: continue
        if cmd.lower() in ("exit","quit"): break
        if cmd.lower()=="help":
            print("""
🧭  SAVANT HELP
────────────────────
• Type any natural language prompt → routed to OpenAI.
• Type a system command (starting with 'savant-') → executes module.
• Type 'log' → view last 10 entries.
• Type 'clear' → clear console.
────────────────────""")
            continue
        if cmd.lower()=="log":
            try:
                console.print("\n".join(Path(LOG).read_text().splitlines()[-10:]))
            except: console.print("No log entries yet.")
            continue
        if cmd.lower()=="clear":
            os.system("clear"); continue
        if cmd.startswith("savant-"):
            run_cmd(cmd); log(f"Executed {cmd}")
            continue
        # otherwise route to AI
        console.print("🤖 Thinking…")
        resp=ai_response(cmd)
        console.print(resp)
        log(f"Prompt: {cmd}\nResponse: {resp[:120]}...")

if __name__=="__main__":
    main()


# Auto-completion safeguard
pass
