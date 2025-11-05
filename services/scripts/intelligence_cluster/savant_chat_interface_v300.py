from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
💬 Savant Chat Interface v300
Full-buffer terminal interface for OpenAI API with Savant integration.
"""

import os, sys, json, textwrap, subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from openai import OpenAI

# === Initialize Environment ===
BASE = Path.home() / "savant"
LOGS = BASE / "logs"
HISTORY = LOGS / "chat_history.json"
RULES = BASE / "docs" / "PROJECT_RULES.md"
LOGS.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")
console = Console()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    console.console.print("[red bold]❌ Missing OPENAI_API_KEY in .env[/red bold]")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# === Utility ===
def log_event(role, content):
    history = []
    if HISTORY.exists():
        try:
            history = json.load(open(HISTORY))
        except Exception:
            pass
    history.append({"time": datetime.now().isoformat(), "role": role, "content": content})
    json.dump(history, open(HISTORY, "w"), indent=2)

def read_large_input():
    """Reads unlimited-length multiline input (pastes, scripts, etc)."""
    console.console.print("[green bold]🧠 Paste or type your input. Press Ctrl+D (EOF) or Enter twice to send.[/green bold]")
    buffer = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not buffer.strip():
        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    break
                lines.append(line)
            except EOFError:
                break
        buffer = "\n".join(lines)
    return buffer.strip()

def open_file(target):
    """Safely open and display a file within ~/savant."""
    path = (BASE / target).resolve()
    if not path.exists() or not path.is_file() or not str(path).startswith(str(BASE)):
        return f"⚠️ File not found or outside Savant directory: {target}"
    content = path.read_text(encoding="utf-8", errors="ignore")
    preview = "\n".join(content.splitlines()[:60])
    return f"📄 **{target}**\n```text\n{preview}\n```"

def load_rules():
    """Reads project rules."""
    if RULES.exists():
        return RULES.read_text(encoding="utf-8")
    return "⚠️ PROJECT_RULES.md not found."

# === Chat Core ===
def chat():
    console.print(Panel.fit(
        "[bold cyan]💬 Savant Chat Interface v300[/bold cyan]\nType '/help' for commands. Press Ctrl+D or type 'exit' to quit.",
        title="Savant", style="cyan"
    ))

    # === Load Project Rules ===
from pathlib import Path

DOCS = Path.home() / "savant/docs/PROJECT_RULES.md"
if DOCS.exists():
    try:
        with open(DOCS, "r", encoding="utf-8") as f:
            rules_text = f.read()
        system_prompt = (
            "You are Savant — a governed AI bound by the following non-negotiable rules:\n\n"
            + rules_text
            + "\n\nYour behavior, tone, and logic must fully comply with these rules. "
              "You may not ignore or forget them under any circumstance."
        )
    except Exception as e:
        system_prompt = f"You are Savant, but the rules could not be read: {e}"
else:
    system_prompt = "You are Savant. PROJECT_RULES.md not found."
    if HISTORY.exists():
        try:
            old = json.load(open(HISTORY))
            for m in old[-15:]:
                messages.append({"role": m["role"], "content": m["content"]})
        except Exception:
            pass

    while True:
        try:
            user_input = read_large_input()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                break

            # Handle commands
            if user_input.startswith("/"):
                cmd, *args = user_input.strip().split(" ", 1)
                arg = args[0] if args else ""
                if cmd == "/help":
                    console.print("""
📘 [bold cyan]Commands:[/bold cyan]
/open <file>     – view a file in ~/savant
/rules           – show project rules
/clear           – clear chat history
/save            – save current log snapshot
/exit            – quit chat
""")
                    continue
                elif cmd == "/open":
                    console.console.print(Markdown(open_file(arg)))
                    continue
                elif cmd == "/rules":
                    console.console.print(Markdown(load_rules()))
                    continue
                elif cmd == "/clear":
                    if HISTORY.exists(): HISTORY.unlink()
                    console.console.print("[yellow]🧹 Chat history cleared.[/yellow]")
                    continue
                elif cmd == "/save":
                    backup = LOGS / f"chat_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    if HISTORY.exists():
                        subprocess.run(["cp", str(HISTORY), str(backup)])
                        console.console.print(f"[green]💾 Saved chat backup → {backup}[/green]")
                    continue

            messages.append({"role": "user", "content": user_input})
            log_event("user", user_input)

            with console.status("[cyan]Savant is thinking...[/cyan]"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7
                )
            reply = response.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            log_event("assistant", reply)
            console.console.print(Panel(Markdown(reply), title="Savant", style="bold blue"))

        except KeyboardInterrupt:
            console.console.print("\n[red]🛑 Exiting...[/red]")
            break
        except Exception as e:
            console.console.print(f"[red]⚠️ Error: {e}[/red]")

if __name__ == "__main__":
    chat()
