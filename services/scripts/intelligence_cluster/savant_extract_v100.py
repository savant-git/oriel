#!/usr/bin/env python3
"""
🧠 Savant Extract v100
--------------------------------------------------------------
Extracts conversation logs from local storage (e.g., Download/
conversations.json) and converts them into structured JSON
for analysis and export.
--------------------------------------------------------------
"""

import os, json, ijson, time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from savant.core.savant_console_theme import console, header, divider, success, error, accent
from savant.core.rule_enforcer import log as rule_log

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
DATA = BASE / "data"
EXTRACT_FILE = DATA / "chat_extract.json"
SOURCE = Path("/storage/emulated/0/Download/conversations.json")

LOGS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

header("🧠 Savant Extract v100 — Chat Log Parser")
divider()

if not SOURCE.exists():
    console.print(error(f"❌ Source not found: {SOURCE}"))
    rule_log("[EXTRACT] Failed: missing source file.")
    exit(1)

try:
    output = []
    with open(SOURCE, "r", encoding="utf-8") as f:
        parser = ijson.items(f, "item")
        for msg in parser:
            if isinstance(msg, dict):
                output.append(msg)

    EXTRACT_FILE.write_text(json.dumps(output, indent=2))
    console.print(success(f"✅ Extracted {len(output)} messages → {EXTRACT_FILE}"))
    rule_log(f"[EXTRACT] Success: {len(output)} entries saved.")
except Exception as e:
    console.print(error(f"⚠️ Extraction failed: {e}"))
    rule_log(f"[EXTRACT] Failure: {e}")
