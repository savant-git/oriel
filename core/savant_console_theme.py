#!/usr/bin/env python3
"""
🎨 Savant Console Theme v400
--------------------------------------------------------------
Global styling library for all Savant terminal interfaces.
Applies the unified Gunmetal • Gold • Accent Red color scheme.
--------------------------------------------------------------
"""

from rich.console import Console
from rich.theme import Theme

SAVANT_THEME = Theme({
    # Grays — readability + structure
    "text": "color(245)",
    "dim": "color(247)",
    "divider": "color(247)",
    # Golds — headers, success, key info
    "gold": "color(178)",
    "deepgold": "color(220)",
    "highlight": "bold color(178)",
    # Accent — emphasis, warnings
    "accent": "color(204)",
    "warn": "bold color(204)",
    # Structural
    "rule": "color(247)",
    "ok": "bold color(178)",
    "error": "bold color(204)",
})

console = Console(theme=SAVANT_THEME)

def header(title: str):
    """Display a standardized Savant header block."""
    console.print("\n[divider]" + "─" * 68 + "[/divider]")
    console.print(f"[deepgold]⚙️  {title}[/deepgold]")
    console.print("[accent]" + "─" * 68 + "[/accent]")

def rule_status(msg: str, status: str = "ok"):
    """Print a rule enforcement or status line."""
    if status == "ok":
        console.print(f"[ok]✅ {msg}[/ok]")
    elif status == "warn":
        console.print(f"[warn]⚠️  {msg}[/warn]")
    else:
        console.print(f"[error]❌ {msg}[/error]")

def divider():
    console.print("[divider]" + "─" * 68 + "[/divider]")

def info(label: str, value: str):
    console.print(f"[gold]{label}[/gold]: [text]{value}[/text]")

def success(msg: str):
    console.print(f"[ok]{msg}[/ok]")

def error(msg: str):
    console.print(f"[error]{msg}[/error]")

def accent(msg: str):
    console.print(f"[accent]{msg}[/accent]")

def brand_banner():
    console.print("[divider]" + "━" * 68 + "[/divider]")
    console.print("[deepgold]🧠 Savant Environment — Gunmetal • Gold • Accent[/deepgold]")
    console.print("[accent]" + "━" * 68 + "[/accent]")
    console.print()
