#!/usr/bin/env python3
"""
💬 Savant Chat Interface v600
--------------------------------------------------------------
Adds direct, rule-safe file editing, instant persistence,
and integrated commit logging.
--------------------------------------------------------------
"""
import os, json
from datetime import datetime
from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown
from savant.ai_core.savant_core_v70 import ask
from savant.core.rule_enforcer import hash_file, log as rule_log
from savant.core.savant_console_theme import console, success, error
from savant.core.savant_file_ops import read, write, append, delete

BASE = Path.home() / "savant"
DOCS = BASE / "docs"
RULES_FILE = DOCS / "PROJECT_RULES.md"

def chat_loop():
    console.print(Panel("💬 Savant Chat v600 — Full File Control\nType '/help' for commands.", style="bold gold1"))
    while True:
        try:
            user = input("\n🧠 You: ").strip()
            if not user: continue
            if user.lower() in {"exit","quit"}:
                console.print(success("👋 Session ended.")); break
            if user == "/help":
                console.print(Panel(
                    "/help\n/rules\n/edit <file>\n/append <file>\n/new <file>\n/delete <file>\n/commit <msg>\n/summary\n/exit",
                    title="🧠 Commands", style="bold cyan")); continue
            if user == "/rules":
                console.print(Panel(Markdown(read(RULES_FILE)), title="📜 PROJECT_RULES.md", style="bold cyan")); continue
            if user.startswith("/edit "):
                f = user.split(" ",1)[1]; console.print(Markdown(read(f))); continue
            if user.startswith("/append "):
                f = user.split(" ",1)[1]; console.print("Enter text to append (end with Ctrl-D):")
                content = "".join(iter(lambda: input()+ "\n", ""))
                console.print(append(f, content)); continue
            if user.startswith("/new "):
                f = user.split(" ",1)[1]; console.print("Enter file content (end with Ctrl-D):")
                content = "".join(iter(lambda: input()+ "\n", ""))
                console.print(write(f, content)); continue
            if user.startswith("/delete "):
                f = user.split(" ",1)[1]; console.print(delete(f)); continue
            if user.startswith("/commit "):
                msg = user.split(" ",1)[1]; rule_log(f"[COMMIT] {msg}"); console.print(success("💾 Committed.")); continue
            if user == "/summary":
                console.print(Panel(f"PROJECT_RULES.md hash: {hash_file(RULES_FILE)[:12]}", style="bold gold1")); continue

            # Default → AI query
            reply = ask(user)
            console.print(Panel(reply, title="Savant", style="bold gold1"))

        except (KeyboardInterrupt, EOFError):
            console.print(success("👋 Terminated by user.")); break
        except Exception as e:
            console.print(error(f"⚠️ {e}"))

if __name__ == "__main__":
    chat_loop()
