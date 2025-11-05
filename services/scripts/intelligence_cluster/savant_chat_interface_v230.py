from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
💬 Savant Chat Interface v230
Multi-line, intelligent, streaming terminal chat client for OpenAI API
"""
import os, sys, json, textwrap
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from openai import OpenAI

# === Environment ===
BASE = Path.home() / "savant"
LOGS = BASE / "logs"
HISTORY = LOGS / "chat_history.json"
LOGS.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")

console = Console()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    console.console.print("[red bold]❌ Missing OPENAI_API_KEY in .env[/red bold]")
    sys.exit(1)

client = OpenAI(api_key=api_key)

def log_event(role, content):
    history = []
    if HISTORY.exists():
        try: history = json.load(open(HISTORY))
        except Exception: pass
    history.append({"time": datetime.now().isoformat(), "role": role, "content": content})
    json.dump(history, open(HISTORY, "w"), indent=2)

def multiline_input(prompt="🧠 You: "):
    console.console.print(f"[green bold]{prompt}[/green bold](press Enter twice to send)")
    buffer = []
    while True:
        line = input()
        if line.strip() == "":
            break
        buffer.append(line)
    return "\n".join(buffer).strip()

def chat():
    console.print(Panel.fit(
        "[bold cyan]💬 Savant Chat Interface v230[/bold cyan]\n[dim]Type 'exit' or press Ctrl+C to quit[/dim]",
        title="Savant", style="cyan"))
    messages = [{"role": "system", "content": "You are Savant, a precise and poetic AI that follows all project rules."}]
    while True:
        try:
            user_input = multiline_input()
            if user_input.lower() in ("exit", "quit"):
                break
            messages.append({"role": "user", "content": user_input})
            log_event("user", user_input)

            with console.status("[cyan]Savant is thinking...[/cyan]"):
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                )

                full_reply = ""
                with Live(console=console, auto_refresh=True) as live:
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        full_reply += delta
                        live.update(Panel(Markdown(full_reply), title="Savant", style="bold blue"))

            log_event("assistant", full_reply)
            messages.append({"role": "assistant", "content": full_reply})
        except KeyboardInterrupt:
            console.console.print("\n[red]🛑 Exiting...[/red]")
            break
        except Exception as e:
            console.console.print(f"[red]⚠️ Error: {e}[/red]")

if __name__ == "__main__":
    chat()
