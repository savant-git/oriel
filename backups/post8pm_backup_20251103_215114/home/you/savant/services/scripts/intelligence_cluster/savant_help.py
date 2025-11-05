"""
Enhanced by Savant Clean+Complete Cluster v2.0 — 2025-10-31T04:02:12.741529+00:00
"""
# ===============================================================
# savant_help.py
# Purpose: Auto-generated Savant documentation header.
# Behavior: See savant_help.py_doc.md for extended analysis.
# Notes: Created 2025-10-30 19:48:32
# ===============================================================

#!/usr/bin/env python3
from savant.services.scripts.system_core.command_header import header, footer
"""
Savant Help System (SHS v1.0)
------------------------------
Generates a dynamic, color-coded index of all Savant commands.

Pulls:
 - aliases from ~/.bashrc
 - metadata from docs/*.md (first 2 paragraphs)
 - version strings from version_engine output
Displays results grouped by subsystem.
"""
import os, re, sys, textwrap
from pathlib import Path
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

ROOT = Path.home() / "savant"
DOCS = ROOT / "docs"
BASHRC = Path.home() / ".bashrc"
console = Console(theme=Theme({
    "ai": "bold yellow",
    "cluster": "bold cyan",
    "engine": "bold magenta",
    "guardian": "bold green",
    "utility": "bold blue",
    "header": "bright_white",
    "version": "orange3",
    "warn": "bright_red"
}))

### — Savant Insight —
# Purpose: extract_docs — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:56:11
def extract_docs(name: str):
    path = DOCS / f"{name}.py_doc.md"
    if not path.exists():
        # fallback: maybe scriptname_doc.md
        alt = DOCS / f"{name}_doc.md"
        if not alt.exists():
            return "No documentation found."
        path = alt
    text = path.read_text(errors="ignore")
    summary = textwrap.shorten(" ".join(text.split()[:80]), width=300)
    return summary

### — Savant Insight —
# Purpose: guess_category — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:56:11
def guess_category(script: str):
    script = script.lower()
    if "ai" in script or "personality" in script: return "ai"
    if "cluster" in script or "intelligence" in script: return "cluster"
    if "engine" in script: return "engine"
    if "guard" in script or "rule" in script: return "guardian"
    return "utility"

### — Savant Insight —
# Purpose: load_aliases — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:56:11
def load_aliases():
    aliases = []
    for line in BASHRC.read_text().splitlines():
        m = re.match(r"alias (savant-[a-z0-9_-]+)='python3 (.+)'", line)
        if m: aliases.append((m.group(1), Path(m.group(2)).name))
    return aliases

### — Savant Insight —
# Purpose: load_versions — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:56:11
def load_versions():
    meta = {}
    vm = ROOT / "services/scripts/version_engine/version_map.json"
    if vm.exists():
        try:
            import json; meta = json.loads(vm.read_text())
        except: pass
    return meta

### — Savant Insight —
# Purpose: main — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:56:11
def main():
    aliases = load_aliases()
    versions = load_versions()
    if not aliases:
        console.footer("Error.", "error")
        sys.exit(0)

    table = Table(title=f"SAVANT COMMAND INDEX — {datetime.now().strftime('%Y-%m-%d %H:%M')}", show_lines=True)
    table.add_column("Command", style="header", no_wrap=True)
    table.add_column("Subsystem", style="header")
    table.add_column("Version", style="version")
    table.add_column("Description", style="header")

    for cmd, script in sorted(aliases):
        cat = guess_category(script)
        summary = extract_docs(script)
        version = "—"
        if script in versions:
            version = versions[script].get("version", "—")
        table.add_row(cmd, cat, version, summary, style=cat)

    console.print(table)
    console.print("\n[bold white]Tip:[/] Run [yellow]savant-docs[/] to regenerate documentation.")
    console.print("[bold white]Usage:[/] Type [cyan]savant-[command][/cyan] to execute a module.\n")

if __name__ == "__main__":
    main()

# Auto-completion safeguard
pass
