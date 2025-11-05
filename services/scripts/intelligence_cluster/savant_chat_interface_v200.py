from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
💬 Savant Chat Interface v200 — full terminal chat client for OpenAI API
"""
import os, json, readline
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv
from openai import OpenAI

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
HISTORY = LOGS / "chat_history.json"
load_dotenv(BASE / ".env")
console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def log_event(role, content):
    LOGS.mkdir(parents=True, exist_ok=True)
    history = []
    if HISTORY.exists():
        try: history = json.load(open(HISTORY))
        except: pass
    history.append({"time": datetime.now().isoformat(), "role": role, "content": content})
    json.dump(history, open(HISTORY, "w"), indent=2)

def chat():
    console.print(Panel.fit(
        "[bold cyan]💬 Savant Interactive Chat Interface v200[/bold cyan]\nType 'exit' to quit.",
        title="Savant", style="cyan"))
    messages = [{"role":"system","content":"You are Savant, a precise and poetic AI bound to project rules."}]
    while True:
        user = Prompt.ask("[bold green]🧠 You[/bold green]")
        if user.lower() in ("exit","quit"): break
        try:
            messages.append({"role":"user","content":user})
            log_event("user", user)
            with console.status("[cyan]Thinking...[/cyan]"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7)
            reply = response.choices[0].message.content
            messages.append({"role":"assistant","content":reply})
            log_event("assistant", reply)
            console.console.print(Panel(Markdown(reply), title="Savant", style="bold blue"))
        except Exception as e:
            console.console.print(f"[red]⚠️ Error:[/red] {e}")

if __name__ == "__main__":
    chat()
