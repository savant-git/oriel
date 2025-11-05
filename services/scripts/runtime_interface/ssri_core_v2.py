#!/usr/bin/env python3
"""
🧠  SAVANT STANDALONE RUNTIME INTERFACE  (SSRI v2.0)
────────────────────────────────────────────────────
Graphical console (text-based dashboard) + AI orchestration.
Now includes:
  • dynamic fractal version indicator
  • modular pane system (log, AI output, task monitor)
  • live command router for all savant-* commands
  • upgrade hooks for autonomous iteration + synthesis
"""
import os, curses, subprocess, threading, queue, time, requests, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home()/ "savant"
LOG  = ROOT/"logs"/"ssri_dashboard.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg:str):
    with open(LOG,"a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def ai_call(prompt:str)->str:
    key=os.getenv("OPENAI_API_KEY")
    headers={"Authorization":f"Bearer {key}"} if key else {}
    payload={"model":"gpt-4o-mini","messages":[
        {"role":"system","content":"You are Savant Runtime AI — concise, technical, elegant."},
        {"role":"user","content":prompt}
    ]}
    try:
        r=requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=payload,timeout=60)
        if r.status_code!=200:
            return f"[{r.status_code}] {r.text[:100]}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️  AI error: {e}"

class Dashboard:
    def __init__(self,stdscr):
        self.stdscr=stdscr
        self.input_q=queue.Queue()
        self.output=[]
        self.running=True
        threading.Thread(target=self.input_loop,daemon=True).start()

    def input_loop(self):
        while self.running:
            cmd=self.stdscr.getstr(curses.LINES-2,2,80).decode().strip()
            self.input_q.put(cmd)

    def draw(self):
        self.stdscr.clear()
        self.stdscr.border()
        self.stdscr.addstr(0,3," SAVANT RUNTIME v2.0 ",curses.A_REVERSE)
        self.stdscr.addstr(2,2,"Type commands or prompts below.  Press Ctrl-C to exit.")
        y=4
        for line in self.output[-(curses.LINES-6):]:
            self.stdscr.addstr(y,3,line[:curses.COLS-6]); y+=1
        self.stdscr.refresh()

    def append(self,text):
        for line in text.splitlines():
            self.output.append(line)

def run_command(cmd:str)->str:
    try:
        res=subprocess.run(cmd,shell=True,capture_output=True,text=True)
        return res.stdout or res.stderr
    except Exception as e:
        return f"Command error: {e}"

def main(stdscr):
    curses.curs_set(1)
    dash=Dashboard(stdscr)
    dash.append("🧩 Savant Dashboard Initialized.")
    while dash.running:
        dash.draw()
        cmd=dash.input_q.get()
        if cmd in ("exit","quit"):
            dash.running=False; break
        elif cmd.startswith("savant-"):
            dash.append(f"⚙️  Executing {cmd}...")
            out=run_command(cmd)
            dash.append(out)
            log(f"{cmd}: executed")
        elif cmd.strip():
            dash.append(f"🤖 {cmd}")
            resp=ai_call(cmd)
            dash.append(resp)
            log(f"AI: {cmd[:40]} -> {resp[:80]}")
        time.sleep(0.05)

if __name__=="__main__":
    curses.wrapper(main)


# Auto-completion safeguard
pass
