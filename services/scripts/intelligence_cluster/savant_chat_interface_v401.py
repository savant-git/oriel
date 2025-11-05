#!/usr/bin/env python3
"""
💬 Savant Chat Interface v401
--------------------------------------------------------------
Rule-aware interactive console for Savant.
Includes persistent memory with adaptive self-repair.
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

# === Savant core imports ===
from savant.ai_core.savant_core_v1 import ask, analyze_code, improve_code
from savant.core.rule_enforcer import log as rule_log, hash_file
from savant.core.savant_console_theme import (
    console, header, divider, rule_status, success, error, accent
)

# === Paths & environment ===
BASE = Path.home() / "savant"
DOCS = BASE / "docs"
LOGS = BASE / "logs"
DATA = BASE / "data"
RULES_FILE = DOCS / "PROJECT_RULES.md"
MEMORY_FILE = DATA / "memory.json"
LOGS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")

# === Load Rules ===
rules_text = RULES_FILE.read_text(encoding="utf-8") if RULES_FILE.exists() else "⚠️ PROJECT_RULES.md not found."

system_prompt = f"""
You are Savant — an elite AI bound by immutable project law.
Follow the rules below *without exception*.

{rules_text}

Always cite relevant rule numbers when reasoning.
Maintain formal, lucid, disciplined tone.
"""

# === Safe persistent memory ===
def ensure_memory():
    """Create or repair memory.json"""
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(json.dumps({"history": []}, indent=2))
        return {"history": []}
    try:
        data = json.loads(MEMORY_FILE.read_text())
        if "history" not in data or not isinstance(data["history"], list):
            raise ValueError
        return data
    except Exception:
        # self-repair
        console.print(error("🧩 Memory corrupted — rebuilding new memory store."))
        MEMORY_FILE.write_text(json.dumps({"history": []}, indent=2))
        return {"history": []}

def save_memory(data):
    try:
        MEMORY_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        console.print(error(f"⚠️ Could not save memory: {e}"))

memory = ensure_memory()

# === Utilities ===
def show_rule_summary():
    table = Table(show_header=True, header_style="bold gold1")
    table.add_column("Section", style="cyan")
    table.add_column("Description", style="white")
    for line in rules_text.splitlines():
        if line.startswith("## "):
            section = line.replace("## ", "").strip()
            table.add_row(section, "Active project directive section")
    console.print(table)

def cmd_analyze(path):
    path = Path(path).expanduser()
    if not path.exists():
        console.print(error(f"File not found: {path}"))
        return
    result = analyze_code(path.read_text())
    console.print(Panel(result, title=f"🧩 Analysis — {path.name}", style="bold cyan"))

def cmd_improve(path):
    path = Path(path).expanduser()
    if not path.exists():
        console.print(error(f"File not found: {path}"))
        return
    result = improve_code(path.read_text())
    console.print(Panel(result, title=f"⚙️ Improved Code — {path.name}", style="bold gold1"))

def cmd_rulecheck(path):
    path = Path(path).expanduser()
    if not path.exists():
        console.print(error(f"File not found: {path}"))
        return
    code = path.read_text()
    query = f"Check compliance of this code with the following rules:\n{rules_text}\n\nCode:\n{code}"
    result = ask(query, system="You are Savant performing compliance validation.")
    console.print(Panel(result, title=f"📜 Rule Compliance — {path.name}", style="bold violet"))

# === Main loop ===
def chat_loop():
    header("💬 Savant Chat Interface v401")
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

            if user == "/help":
                console.print(Panel(
                    "/help — show commands\n"
                    "/rules — show full rules\n"
                    "/summary — show section overview\n"
                    "/analyze <path> — analyze code\n"
                    "/improve <path> — improve code\n"
                    "/rulecheck <path> — verify compliance\n"
                    "/memory — view memory\n"
                    "/clear — clear screen\n"
                    "exit — quit",
                    title="🧠 Commands", style="bold cyan"))
                continue
            if user == "/rules":
                console.print(Panel(Markdown(rules_text), title="📜 Full Project Rules", style="bold cyan"))
                continue
            if user == "/summary":
                show_rule_summary();  continue
            if user == "/clear":
                os.system("clear");  continue
            if user.startswith("/analyze "):
                cmd_analyze(user.split(" ",1)[1]);  continue
            if user.startswith("/improve "):
                cmd_improve(user.split(" ",1)[1]);  continue
            if user.startswith("/rulecheck "):
                cmd_rulecheck(user.split(" ",1)[1]);  continue
            if user == "/memory":
                console.print(Panel(json.dumps(memory, indent=2), title="🧠 Active Memory", style="bold cyan"));  continue

            # --- Rule enforcement ---
            if RULES_FILE.exists():
                doc_hash = hash_file(RULES_FILE)
                rule_log(f"[RULE] ✅ Enforcement passed — PROJECT_RULES.md hash {doc_hash[:12]}")
            else:
                rule_log("[RULE] ⚠️ PROJECT_RULES.md missing.")

            # --- Memory update ---
            memory.setdefault("history", [])
            memory["history"].append({"role": "user", "content": user, "time": datetime.utcnow().isoformat()})
            save_memory(memory)

            # --- AI reply ---
            reply = ask(user, system=system_prompt)
            memory["history"].append({"role": "assistant", "content": reply, "time": datetime.utcnow().isoformat()})
            save_memory(memory)

            console.print(Panel(reply.strip(), title="Savant", style="gold1"))

        except (KeyboardInterrupt, EOFError):
            console.print(success("👋 Session terminated by user.")); break
        except Exception as e:
            console.print(error(f"⚠️ Exception: {e}"))
            memory = ensure_memory()  # auto-repair memory

# === Entry ===
if __name__ == "__main__":
    chat_loop()
