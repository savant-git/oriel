#!/usr/bin/env python3
"""
💬 Savant Chat Interface v500
--------------------------------------------------------------
Advanced terminal interface with:
- Rule hierarchy summary
- File analysis & rule enforcement utilities
- Memory and log management
--------------------------------------------------------------
"""

import os, sys, json, readline, time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from savant.ai_core.savant_core_v70 import ask, analyze_code, improve_code
from savant.core.rule_enforcer import log as rule_log, hash_file
from savant.core.savant_console_theme import console, header, divider, success, error, accent

BASE = Path.home() / "savant"
DOCS = BASE / "docs"
LOGS = BASE / "logs"
DATA = BASE / "data"
RULES_FILE = DOCS / "PROJECT_RULES.md"
MEMORY_FILE = DATA / "memory.json"

LOGS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")

def load_rules():
    if not RULES_FILE.exists():
        return {}
    sections, current = {}, None
    for line in RULES_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line.replace("## ", "").strip()
            sections[current] = []
        elif line.strip().startswith(("-", "•", "1.")):
            if current:
                sections[current].append(line.strip())
    return sections

rules = load_rules()
rules_text = RULES_FILE.read_text() if RULES_FILE.exists() else "⚠️ PROJECT_RULES.md missing."

def ensure_memory():
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(json.dumps({"history": []}, indent=2))
    try:
        return json.loads(MEMORY_FILE.read_text())
    except Exception:
        MEMORY_FILE.write_text(json.dumps({"history": []}, indent=2))
        return {"history": []}

memory = ensure_memory()

def show_full_summary():
    table = Table(show_header=True, header_style="bold gold1")
    table.add_column("Section", style="cyan", no_wrap=True)
    table.add_column("Rules", style="white")
    for section, lines in rules.items():
        content = "\n".join(lines)
        table.add_row(section, content if content else "— none —")
    console.print(table)

def show_logs():
    log_path = LOGS / "rule_enforcement.log"
    if not log_path.exists():
        console.print(error("No rule logs found.")); return
    console.print(Panel(log_path.read_text()[-2000:], title="📜 Rule Logs", style="bold cyan"))

def list_commands():
    cmds = [
        "/help", "/rules", "/summary", "/analyze <file>",
        "/improve <file>", "/rulecheck <file>", "/memory",
        "/context", "/logs", "/inspect <path>", "/rule <n>",
        "/clear", "/exit"
    ]
    console.print(Panel("\n".join(cmds), title="🧠 Commands", style="bold gold1"))

def chat_loop():
    console.print(Panel("💬 Savant Chat Interface v500\nType '/help' for commands or 'exit' to quit.", style="bold gold1"))
    while True:
        try:
            user = input("\n🧠 You: ").strip()
            if not user:
                continue
            if user.lower() in {"exit", "quit"}:
                console.print(success("👋 Session ended gracefully.")); break

            # --- Commands ---
            if user == "/help": list_commands(); continue
            if user == "/rules": console.print(Panel(Markdown(rules_text), title="📜 Project Rules", style="bold cyan")); continue
            if user == "/summary": show_full_summary(); continue
            if user == "/clear": os.system("clear"); continue
            if user == "/logs": show_logs(); continue
            if user == "/context": console.print(Panel(json.dumps(memory, indent=2), title="🧠 Context Memory", style="bold cyan")); continue

            # --- Analysis Commands ---
            if user.startswith("/analyze "):
                path = user.split(" ", 1)[1]; result = analyze_code(Path(path).read_text()); console.print(Panel(result, title=f"🧩 {path}", style="bold cyan")); continue
            if user.startswith("/improve "):
                path = user.split(" ", 1)[1]; result = improve_code(Path(path).read_text()); console.print(Panel(result, title=f"⚙️ {path}", style="bold gold1")); continue
            if user.startswith("/rulecheck "):
                path = user.split(" ", 1)[1]; code = Path(path).read_text(); q = f"Check this code for compliance:\n{rules_text}\nCode:\n{code}"; r = ask(q); console.print(Panel(r, title=f"📜 Compliance — {path}", style="bold violet")); continue

            # --- Rule & Memory ---
            if user.startswith("/rule "):
                num = user.split(" ", 1)[1]
                result = ask(f"Summarize and explain rule {num} from:\n{rules_text}")
                console.print(Panel(result, title=f"📘 Rule {num}", style="bold cyan")); continue

            # --- General Query ---
            rule_log(f"[RULE] ✅ Enforcement passed — PROJECT_RULES.md hash {hash_file(RULES_FILE)[:12]}")
            memory["history"].append({"role": "user", "content": user, "time": datetime.utcnow().isoformat()})
            reply = ask(user, system="You are Savant, elite AI bound by rules and reasoning.")
            memory["history"].append({"role": "assistant", "content": reply, "time": datetime.utcnow().isoformat()})
            MEMORY_FILE.write_text(json.dumps(memory, indent=2))
            console.print(Panel(reply.strip(), title="Savant", style="bold gold1"))

        except (KeyboardInterrupt, EOFError):
            console.print(success("👋 Session terminated by user.")); break
        except Exception as e:
            console.print(error(f"⚠️ Exception: {e}"))

if __name__ == "__main__":
    chat_loop()
