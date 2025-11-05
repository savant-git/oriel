#!/usr/bin/env python3
"""
🧠 Savant AI Core v70
--------------------------------------------------------------
Unified logic engine powering both CLI and Web interfaces.
Handles model calls, context preservation, and rule awareness.
--------------------------------------------------------------
"""

import os, json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# === Environment Setup ===
BASE = Path.home() / "savant"
DOCS = BASE / "docs" / "PROJECT_RULES.md"
LOGS = BASE / "logs"
LOGS.mkdir(exist_ok=True, parents=True)
load_dotenv(BASE / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Global Memory ===
HISTORY = LOGS / "chat_history.json"
if not HISTORY.exists():
    HISTORY.write_text("[]", encoding="utf-8")

def log_interaction(role, content):
    data = json.loads(HISTORY.read_text())
    data.append({"role": role, "content": content})
    HISTORY.write_text(json.dumps(data[-100:], indent=2))

def ask(prompt: str) -> str:
    """
    Unified AI Core interface function.
    Accepts text prompt, reads project rules, and returns reply.
    """
    rules = "(rules unavailable)"
    if DOCS.exists():
        rules = DOCS.read_text(encoding="utf-8")

    log_interaction("user", prompt)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are Savant, bound by the following rules:\n{rules}"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
    )

    reply = completion.choices[0].message.content.strip()
    log_interaction("assistant", reply)
    return reply
