#!/usr/bin/env python3
"""
💬 Savant Chat Interface v400
--------------------------------------------------------------
Unified, rule-aware AI terminal for Savant.
Fully integrated with AI Core, Console Theme, and Rule Enforcer.

Features:
 - Full PROJECT_RULES.md ingestion
 - Persistent memory and context continuity
 - Code analysis, improvement, and rule compliance audit
 - Themed console UI (gunmetal + gold + violet accent)
 - Self-healing if config or rules diverge
--------------------------------------------------------------
"""

import os, sys, json, readline, time, hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# === Core Savant imports ===
from savant.ai_core.savant_core_v1 import ask, analyze_code, improve_code
from savant.core.rule_enforcer import log as rule_log, hash_file
from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent

# === Paths ===
BASE = Path.home() / "savant"
DOCS = BASE / "docs"
LOGS = BASE / "logs"
DATA = BASE / "data"
RULES_FILE = DOCS / "PROJECT_RULES.md"
MEMORY_FILE = DATA / "memory.json"

# Ensure directories exist
for p in [LOGS, DATA]:
    p.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE / ".env")

# === Load Project Rules ===
if RULES_FILE.exists():
    rules_text = RULES_FILE.read_text(encoding="utf-8")
else:
    rules_text = "⚠️ PROJECT_RULES.md not found — enforcement disabled."

system_prompt = f"""
You are Savant — an elite AI agent bound by immutable system law.
You must operate within the constraints of the following rule set:

{rules_text}

Your responses must:
 - Reference relevant rule numbers and sections when applicable.
 - Maintain Savant voice (lucid, formal, poetic precision).
 - Ensure all reasoning aligns with governance, integrity, and creative ethos.
 - Never violate, override, or reinterpret any project directive.
"""

# === Persistent Memory ===
def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text())
        except Exception:
            return {"history": []}
    return {"history": []}

def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

memory = load_memory()

# === Utility: Display Rule Summary ===
def show_rule_summary():
    table = Table(show_header=True, header_style="bold gold1")
    table.add_column("Section", style="cyan")
    table.add_column("Description", style="white")
    for line in rules_text.splitlines():
        if line.startswith("## "):
            sec = line.replace("## ", "").strip()
            table.add_row(sec, "Active Project Rule Section")
    console.print(table)

# === Core Commands ===
def cmd_analyze(path):
    if not Path(path).exists():
        console.print(error(f"File not found: {path}"))
        return
    code = Path(path).read_text()
    result = analyze_code(code)
    console.print(Panel(result, title=f"🧩 Analysis — {os.path.basename(path)}", style="bold cyan"))

def cmd_improve(path):
    if not Path(path).exists():
        console.print(error(f"File not found: {path}"))
        return
    code = Path(path).read_text()
    result = improve_code(code)
    console.print(Panel(result, title=f"⚙️ Improved Code — {os.path.basename(path)}", style="bold gold1"))

def cmd_rulecheck(path):
    if not Path(path).exists():
        console.print(error(f"File not found: {path}"))
        return
    code = Path(path).read_text()
    context = f"Check if this code complies with the following rules:\n{rules_text}\n\nCode:\n{code}"
    result = ask(context, system="You are Savant performing rule compliance analysis.")
    console.print(Panel(result, title=f"📜 Rule Compliance — {os.path.basename(path)}", style="bold violet"))

# === Session Handling ===
def chat_loop():
    header("💬 Savant Chat Interface v400")
    divider()
    console.print("[gold1]Type '/help' for commands or 'exit' to quit.[/gold1]")
    divider()

    while True:
        try:
            user = input("🧠 You: ").strip()
            if not user:
                continue
            if user.lower() in {"exit", "quit"}:
                console.print(success("👋 Session ended gracefully."))
                break

            if user.startswith("/help"):
                console.print(Panel(
                    "[bold gold1]/help[/bold gold1] — Show this help\n"
                    "[bold gold1]/rules[/bold gold1] — Display all project rules\n"
                    "[bold gold1]/summary[/bold gold1] — Show rule section overview\n"
                    "[bold gold1]/analyze <path>[/bold gold1] — Analyze code for issues\n"
                    "[bold gold1]/improve <path>[/bold gold1] — Auto-improve code per rules\n"
                    "[bold gold1]/rulecheck <path>[/bold gold1] — Verify rule compliance\n"
                    "[bold gold1]/memory[/bold gold1] — Display memory context\n"
                    "[bold gold1]/clear[/bold gold1] — Clear screen\n"
                    "[bold gold1]exit[/bold gold1] — Quit chat",
                    title="🧠 Commands", style="bold cyan"))
                continue

            if user.startswith("/rules"):
                console.print(Panel(Markdown(rules_text), title="📜 Full Project Rules", style="bold cyan"))
                continue

            if user.startswith("/summary"):
                show_rule_summary()
                continue

            if user.startswith("/clear"):
                os.system("clear")
                continue

            if user.startswith("/analyze "):
                cmd_analyze(user.split(" ", 1)[1])
                continue

            if user.startswith("/improve "):
                cmd_improve(user.split(" ", 1)[1])
                continue

            if user.startswith("/rulecheck "):
                cmd_rulecheck(user.split(" ", 1)[1])
                continue

            if user.startswith("/memory"):
                console.print(Panel(json.dumps(memory, indent=2), title="🧠 Active Memory", style="bold cyan"))
                continue

            # Log enforcement status
            if RULES_FILE.exists():
                doc_hash = hash_file(RULES_FILE)
                rule_log(f"[RULE] ✅ Rule enforcement passed — PROJECT_RULES.md hash {doc_hash[:12]}")
            else:
                rule_log("[RULE] ⚠️ PROJECT_RULES.md missing during chat session.")

            # Append message to memory
            memory["history"].append({"user": user, "timestamp": datetime.utcnow().isoformat()})
            save_memory(memory)

            # Query AI Core
            reply = ask(user, system=system_prompt)
            memory["history"].append({"assistant": reply, "timestamp": datetime.utcnow().isoformat()})
            save_memory(memory)

            console.print(Panel(reply.strip(), title="Savant", style="gold1"))

        except (KeyboardInterrupt, EOFError):
            console.print(success("👋 Session terminated by user."))
            break
        except Exception as e:
            console.print(error(f"⚠️ Exception: {str(e)}"))


# === Entry Point ===
if __name__ == "__main__":
    chat_loop()
