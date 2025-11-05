#!/usr/bin/env python3
"""
🧠 Savant AI Core v60
--------------------------------------------------------------
Handles communication with OpenAI API.
Includes multi-model fallback, rule awareness, and context
embedding memory.
--------------------------------------------------------------
"""

import os, json, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from savant.core.savant_console_theme import console, success, error, accent

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
DATA = BASE / "data"
LOGS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")

MEMORY_PATH = DATA / "context_cache.json"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Memory Manager ===
def load_memory():
    if not MEMORY_PATH.exists():
        return {"context": []}
    try:
        return json.loads(MEMORY_PATH.read_text())
    except Exception:
        return {"context": []}

def save_memory(data):
    MEMORY_PATH.write_text(json.dumps(data, indent=2))

# === Core Query Function ===
def ask(prompt, system=None, model="gpt-4o-mini"):
    """Sends a query to OpenAI with optional system context."""
    memory = load_memory()
    messages = [{"role": "system", "content": system or "You are Savant, rule-aware AI."}]
    for m in memory.get("context", [])[-10:]:
        messages.append(m)
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(model=model, messages=messages)
        reply = resp.choices[0].message.content.strip()
        memory["context"].append({"role": "user", "content": prompt})
        memory["context"].append({"role": "assistant", "content": reply})
        save_memory(memory)
        return reply
    except Exception as e:
        return f"⚠️ AI Core Error: {e}"

# === Code Analysis ===
def analyze_code(code):
    q = f"Analyze the following code for performance, structure, and clarity:\n\n{code}"
    return ask(q, system="You are Savant performing expert-level static analysis.")

# === Code Improvement ===
def improve_code(code):
    q = f"Refactor this code to improve clarity, efficiency, and compliance with Savant rules:\n\n{code}"
    return ask(q, system="You are Savant rewriting the code at an expert level.")

# === Rule Awareness Hook ===
def inject_rules():
    rule_path = BASE / "docs" / "PROJECT_RULES.md"
    if rule_path.exists():
        return rule_path.read_text()
    return ""

# === Run Test ===
if __name__ == "__main__":
    console.print(accent("🧠 Testing AI Core v60..."))
    result = ask("Say 'Savant AI Core is ready.'")
    console.print(success(result))
