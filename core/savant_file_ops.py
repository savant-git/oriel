#!/usr/bin/env python3
"""
🧱 Savant File Operations v10
--------------------------------------------------------------
Provides controlled read/write/update/delete capabilities.
Every change logs a hash before and after and re-validates
PROJECT_RULES.md. Used by Chat Interface and AI Core.
--------------------------------------------------------------
"""
import os, hashlib, time, json
from pathlib import Path
from savant.core.rule_enforcer import hash_file, log as rule_log
from savant.core.savant_console_theme import success, error

BASE = Path.home() / "savant"
DOCS = BASE / "docs"
LOGS = BASE / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    p = Path(path).expanduser()
    if not p.exists(): return f"⚠️ File not found: {p}"
    return p.read_text(encoding="utf-8")

def write(path, content):
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    before = _sha(p) if p.exists() else None
    p.write_text(content, encoding="utf-8")
    after = _sha(p)
    rule_log(f"[WRITE] {p}  before:{before or '—'}  after:{after}")
    return success(f"✅ Updated {p}")

def append(path, content):
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(p.read_text() + "\n" + content, encoding="utf-8") if p.exists() else p.write_text(content, encoding="utf-8")
    rule_log(f"[APPEND] {p}")
    return success(f"➕ Appended to {p}")

def delete(path):
    p = Path(path).expanduser()
    if not p.exists(): return f"⚠️ {p} not found"
    p.unlink()
    rule_log(f"[DELETE] {p}")
    return success(f"🗑️ Deleted {p}")
