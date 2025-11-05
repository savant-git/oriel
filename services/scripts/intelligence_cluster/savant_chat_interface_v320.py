from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Savant Chat Interface v320
--------------------------------------------------------------
An intelligent terminal interface for interacting with Savant AI.
Features:
 - Reads and embeds PROJECT_RULES.md into each chat session
 - Logs full conversation to logs/chat_history.json
 - Displays rule enforcement status inline
--------------------------------------------------------------
"""

import os
import json
import readline
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
from openai import OpenAI
import subprocess

# === Paths ===
BASE = Path.home() / "savant"
LOGS = BASE / "logs"
DOCS = BASE / "docs" / "PROJECT_RULES.md"
LOGS.mkdir(parents=True, exist_ok=True)
HISTORY = LOGS / "chat_history.json"

# === Load .env and enforce rules ===
load_dotenv(BASE / ".env")

console = Console()

# Run rule enforcement before session
rule_check = subprocess.run(
    ["python3", str(BASE / "core" / "rule_enforcer.py")],
    capture_output=True,
    text=True,
)
console.console.print(Panel(rule_check.stdout.strip(), title="Rule Enforcement"))

# === Load rules for context ===
if DOCS.exists():
    try:
        rules_text = DOCS.read_text(encoding="utf-8")
        system_prompt = (
            "You are Savant — an AI bound by the following non-negotiable project rules:\n\n"
            + rules_text
            + "\n\nYou must always operate within these directives. Never disregard or alter them."
        )
    except Exception as e:
        system_prompt = f"You are Savant, but the rules could not be read: {e}"
else:
    system_prompt = "You are Savant, but PROJECT_RULES.md is missing."

# === Initialize AI client ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

messages = [{"role": "system", "content": system_prompt}]
if HISTORY.exists():
    try:
        previous = json.loads(HISTORY.read_text(encoding="utf-8"))
        if isinstance(previous, list):
            messages.extend(previous[-10:])  # load last 10 exchanges
    except Exception:
        pass

console.console.print(Panel("💬 Savant Chat Interface v320\nType '/help' for commands, 'exit' to quit.", title="Savant"))

while True:
    try:
        user_input = console.input("\n🧠 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            console.console.print("\n[bold gold3]Session ended. Goodbye.[/bold gold3]")
            break
        if user_input.lower() == "/help":
            console.print(
                "[cyan]Commands:[/cyan]\n"
                "  exit — quit chat\n"
                "  /rules — show active project rules\n"
                "  /log — view last messages\n"
            )
            continue
        if user_input.lower() == "/rules":
            console.console.print(Markdown(rules_text if DOCS.exists() else "Rules not found."))
            continue
        if user_input.lower() == "/log":
            if HISTORY.exists():
                console.console.print(HISTORY.read_text(encoding="utf-8"))
            else:
                console.console.print("[grey58]No log yet.[/grey58]")
            continue

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        console.console.print(Panel(Markdown(reply), title="Savant"))

        HISTORY.write_text(json.dumps(messages[-50:], indent=2), encoding="utf-8")

    except KeyboardInterrupt:
        console.console.print("\n[bold gold3]Session interrupted by user.[/bold gold3]")
        break
    except Exception as e:
        console.console.print(f"[red]⚠️ Error: {e}[/red]")
