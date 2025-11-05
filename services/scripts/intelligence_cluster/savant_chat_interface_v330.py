from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
💬 Savant Chat Interface v330
--------------------------------------------------------------
A unified terminal interface for interacting with the Savant AI Core.
Now rule-aware: displays PROJECT_RULES.md summary on launch.
--------------------------------------------------------------
"""

import os, sys, json, readline, textwrap
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from openai import OpenAI
import subprocess

# === Paths and Environment ===
BASE = Path.home() / "savant"
DOCS = BASE / "docs" / "PROJECT_RULES.md"
LOGS = BASE / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
HISTORY = LOGS / "chat_history.json"
load_dotenv(BASE / ".env")

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Run Rule Enforcer ===
ENFORCER = BASE / "core" / "rule_enforcer.py"
if ENFORCER.exists():
    result = subprocess.run(["python3", str(ENFORCER)], capture_output=True, text=True)
    console.print(Panel(result.stdout.strip(), title="Rule Enforcement", style="bold yellow"))
else:
    console.print("[bold red]⚠️ Rule enforcer missing! Skipping compliance check.[/bold red]")

# === Load and Display Rule Summary ===
if DOCS.exists():
    with open(DOCS, "r", encoding="utf-8") as f:
        rules_lines = f.readlines()
    headers = [line.strip() for line in rules_lines if line.startswith("##")]
    preview = "\n".join(headers[:3]) if headers else "(No headers found)"
    console.print(Panel(preview, title="Active Project Rules", style="bold cyan"))
else:
    console.print("[bold red]⚠️ PROJECT_RULES.md not found.[/bold red]")
    preview = ""

# === Chat Loop ===
messages = [{"role": "system", "content": f"You are Savant, governed by the following rules:\n{preview}"}]

console.print(Panel("💬 Savant Chat Interface v330\nType '/help' for commands or 'exit' to quit.",
                    title="Savant", style="bold green"))

while True:
    try:
        user_input = Prompt.ask("\n🧠 You")
        if user_input.lower().strip() in ["exit", "quit"]:
            console.print("[bold yellow]Session ended.[/bold yellow]")
            break
        if user_input.strip() == "":
            continue

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        console.print(Panel(Markdown(reply), title="Savant", style="bold green"))

        # Save chat history
        with open(HISTORY, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Session interrupted.[/bold yellow]")
        break
    except Exception as e:
        console.print(f"[bold red]⚠️ Error: {e}[/bold red]")
