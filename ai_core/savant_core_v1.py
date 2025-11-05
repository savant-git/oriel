#!/usr/bin/env python3
"""
🧠 Savant AI Core v1
Central cognitive engine connecting all Savant services.
"""

import os, sys, importlib, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

BASE = Path.home() / "savant"
DOCS = BASE / "docs"
LOGS = BASE / "logs"
DATA = BASE / "data"
AI_MEMORY = DATA / "memory.json"

load_dotenv(BASE / ".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Persistent memory ===
AI_MEMORY.parent.mkdir(parents=True, exist_ok=True)
if not AI_MEMORY.exists():
    AI_MEMORY.write_text(json.dumps({"sessions": []}, indent=2))

def log(msg: str):
    LOGS.mkdir(parents=True, exist_ok=True)
    with open(LOGS / "ai_core.log", "a") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {msg}\n")

def ask(prompt, system=None, model="gpt-4o-mini"):
    """Send prompt to OpenAI and return reply."""
    messages = [{"role": "system", "content": system or "You are Savant, the architect AI."},
                {"role": "user", "content": prompt}]
    resp = client.chat.completions.create(model=model, messages=messages)
    reply = resp.choices[0].message.content
    log(f"Prompt: {prompt[:60]}... | Reply: {reply[:60]}...")
    return reply

def analyze_code(file_path):
    """Read any code file and get analysis/improvement suggestions."""
    code = Path(file_path).read_text()
    system = "You are Savant, an expert code analyst and optimizer."
    question = f"Analyze and suggest precise improvements for:\n```{code}```"
    return ask(question, system)

def improve_code(file_path):
    """Generate an improved version and overwrite safely."""
    code = Path(file_path).read_text()
    system = "You are Savant, rewrite with clarity, efficiency, and elegance."
    suggestion = ask(f"Improve this code:\n```{code}```", system)
    backup = Path(file_path).with_suffix(".bak")
    Path(file_path).replace(backup)
    Path(file_path).write_text(suggestion)
    log(f"Improved {file_path}, backup saved as {backup}")
    return suggestion
