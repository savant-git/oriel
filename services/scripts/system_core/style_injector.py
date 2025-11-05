from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
"""
Enhanced by Savant Clean+Complete Cluster v2.0 — 2025-10-31T04:02:12.296133+00:00
"""
# ===============================================================
# style_injector.py
# Purpose: Auto-generated Savant documentation header.
# Behavior: See style_injector.py_doc.md for extended analysis.
# Notes: Created 2025-10-30 19:28:19
# ===============================================================

#!/usr/bin/env python3
"""
Savant Style Injector & Aesthetic Harmonizer (SIAH v1.0)
────────────────────────────────────────────────────────
Scans all Savant scripts and harmonizes:
 - command header usage (UCHS system)
 - correct Savant symbol language
 - meta-version markers
 - ensures each script prints its own contextual header

Never overwrites destructively — creates timestamped backups.
"""
import os, re, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "savant"
LOG = ROOT / "logs" / "style_injector.log"
HEADER_IMPORT = "from savant.services.scripts.system_core.command_header import header, footer"

### — Savant Insight —
# Purpose: log — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:34:44
def log(msg:str):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

### — Savant Insight —
# Purpose: inject_style — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:34:44
def inject_style(path: Path):
    text = path.read_text(errors="ignore")
    if "command_header import" in text:
        log(f"⚙  Already styled: {path.name}")
        return

    backup = path.with_suffix(f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(path, backup)

    # Replace emoji banners with header() calls
    text = re.sub(r"print\(.*🧠.*\)", 'header("Savant Core", "1.0", "Restored aesthetic", "core")', text)
    text = re.sub(r"print\(.*🚀.*\)", 'header("Savant Init", "1.0", "Deployment banner", "init")', text)
    text = re.sub(r"print\(.*✅.*\)", 'footer("Complete.", "done")', text)
    text = re.sub(r"print\(.*⚠️.*\)", 'footer("Error.", "error")', text)

    # Ensure import line at top
    lines = text.splitlines()
    if not any("command_header" in l for l in lines[:10]):
        lines.insert(1, HEADER_IMPORT)
    styled = "\n".join(lines)
    path.write_text(styled, encoding="utf-8")

    log(f"⛓️  Styled {path.name}")

### — Savant Insight —
# Purpose: scan_all — auto-annotated by Savant DocSynth
# Added 2025-10-30 19:34:44
def scan_all():
    for py in (ROOT / "services").rglob("*.py"):
        if py.name.startswith("__") or "system_core" in str(py):
            continue
        inject_style(py)
    log("☑  Style harmonization complete.")

if __name__ == "__main__":
    console.print("⛓️  Running Savant Style Injector & Aesthetic Harmonizer v1.0")
    scan_all()
    console.print("☑  All scripts harmonized with unified headers.")


# Auto-completion safeguard
pass
