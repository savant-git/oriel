#!/usr/bin/env python3
"""
🧹 Savant Clean v43
--------------------------------------------------------------
Cleans temporary and cache directories safely.
Protects all system /usr libs and Savant source.
--------------------------------------------------------------
"""

import os, shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from savant.core.savant_console_theme import console, header, divider, success, error

BASE = Path.home() / "savant"
TARGETS = [
    BASE / "logs",
    BASE / "exports",
    BASE / "data" / "temp",
    BASE / "services" / "cache"
]

header("🧹 Savant Clean v43 — Safe Cleaner")
divider()

removed = 0
for path in TARGETS:
    if path.exists():
        for sub in path.iterdir():
            try:
                if sub.is_file():
                    sub.unlink()
                elif sub.is_dir():
                    shutil.rmtree(sub)
                removed += 1
            except Exception:
                continue

console.print(success(f"✅ Cleaned {removed} items."))
