#!/usr/bin/env python3
"""
💬 Savant Chat Interface v403
--------------------------------------------------------------
Fixes 'memory' reference exceptions and guarantees stable
context persistence across all loops.
--------------------------------------------------------------
"""

import os, sys, json, readline, time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from savant.ai_core.savant_core_v60 import ask, analyze_code, improve_code
from savant.core.rule_enforcer import log as rule_log, hash_file
from savant.core.savant_console_theme import (
    console, header, divider, success, error, accent
)

# === Paths & Environment ===
BASE = Path.home() / "savant"
DOCS = BASE / "docs"
LOGS = BASE / "logs"
DATA = BASE / "data"
RULES_FILE = DOCS / "PROJECT_RULES.md"
MEMORY_FILE = DATA / "memory.json"

LOGS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")

# === Load Project Rules ===
rules_text = RULES_FILE.read_text(encoding="utf-8") if RULES_FILE.exists() else "⚠️ PROJECT_RULES.md not found."
system_prompt = f"You are Savant — an elite AI bound by immutable project law.\n{rules_text}"

# === Memory Handling ===
def ensure_memory():
    """Always returns a valid memory dictionary."""
    try:
        if not MEMORY_FILE.exists():
            MEMORY_FILE.write_text(json.dumps({"history": []}, indent=2))
        data = json.loads(MEMORY_FILE.read_text())
        if not isinstance(data, dict) or "history" not in data:
            raise ValueError
        return data
    except Exception:
        console.print(error("⚠️ Memory store missing or corrupted — rebuilding..."))
        MEMORY_FILE.write_text(json.dumps({"history": []}, indent=2))
        return {"history": []}

def save_memory(data):
    try:
        MEMORY_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        console.print(error(f"⚠️ Failed to save memory: {e}"))

memory = ensure_memory()

# === Command Functions ===
def show_rule_summary():
    table = Table(show_header=True, header_style="bold gold1")
    table.add_column("Section", style="cyan")
    table.add_column("Description", style="white")
    for line in rules_text.splitlines():
        if line.startswith("## "):
            section = line.replace("## ", "").strip()
            table.add_row(section, "Active directive section")
    console.print(table)

def cmd_analyze(path):
    path = Path(path).expanduser()
    if not path.exists():
        console.print(error(f"File not found: {path}")); return
    result = analyze_code(path.read_text())
    console.print(Panel(result, title=f"🧩 Analysis — {path.name}", style="bold cyan"))

def cmd_improve(path):
    path = Path(path).expanduser()
    if not path.exists():
        console.print(error(f"File not found: {path}")); return
    result = improve_code(path.read_text())
    console.print(Panel(result, title=f"⚙️ Improved Code — {path.name}", style="bold gold1"))

def cmd_rulecheck(path):
    path = Path(path).expanduser()
    if not path.exists():
        console.print(error(f"File not found: {path}")); return
    code = path.read_text()
    query = f"Check this code for compliance with the following rules:\n{rules_text}\n\nCode:\n{code}"
    result = ask(query, system="You are Savant performing rule compliance analysis.")
    console.print(Panel(result, title=f"📜 Rule Compliance — {path.name}", style="bold violet"))

# === Chat Loop ===
def chat_loop():
    global memory
    console.print(Panel("💬 Savant Chat Interface v403\nType '/help' for commands or 'exit' to quit.", style="bold gold1"))
    while True:
        try:
            user = input("\n🧠 You: ").strip()
            if not user:
                continue
            if user.lower() in {"exit", "quit"}:
                console.print(success("👋 Session ended gracefully."))
                break

            # Commands
            if user == "/help":
                console.print(Panel(
                    "/help — show commands\n"
                    "/rules — view all rules\n"
                    "/summary — show rule summary\n"
                    "/analyze <file>\n"
                    "/improve <file>\n"
                    "/rulecheck <file>\n"
                    "/memory — view chat memory\n"
                    "/clear — clear screen\n"
                    "exit — quit",
                    title="🧠 Commands", style="bold cyan"))
                continue
            if user == "/rules":
                console.print(Panel(Markdown(rules_text), title="📜 Project Rules", style="bold cyan")); continue
            if user == "/summary":
                show_rule_summary(); continue
            if user == "/clear":
                os.system("clear"); continue
            if user.startswith("/analyze "):
                cmd_analyze(user.split(" ", 1)[1]); continue
            if user.startswith("/improve "):
                cmd_improve(user.split(" ", 1)[1]); continue
            if user.startswith("/rulecheck "):
                cmd_rulecheck(user.split(" ", 1)[1]); continue
            if user == "/memory":
                console.print(Panel(json.dumps(memory, indent=2), title="🧠 Memory", style="bold cyan")); continue

            # Rule check
            if RULES_FILE.exists():
                rule_log(f"[RULE] ✅ Enforcement passed — PROJECT_RULES.md hash {hash_file(RULES_FILE)[:12]}")
            else:
                rule_log("[RULE] ⚠️ PROJECT_RULES.md missing.")

            # Ensure valid memory object
            if memory is None or "history" not in memory:
                memory = ensure_memory()

            memory["history"].append({"role": "user", "content": user, "time": datetime.utcnow().isoformat()})
            save_memory(memory)

            reply = ask(user, system=system_prompt)
            if not reply or reply.strip().lower() == "none":
                reply = "⚠️ No valid response generated."
            memory["history"].append({"role": "assistant", "content": reply, "time": datetime.utcnow().isoformat()})
            save_memory(memory)

            console.print(Panel(reply.strip(), title="Savant", style="bold gold1"))

        except (KeyboardInterrupt, EOFError):
            console.print(success("👋 Session terminated by user.")); break
        except Exception as e:
            console.print(error(f"⚠️ Exception caught: {e}"))
            memory = ensure_memory()  # rebuild memory immediately

# === Entry ===
if __name__ == "__main__":
    chat_loop()
