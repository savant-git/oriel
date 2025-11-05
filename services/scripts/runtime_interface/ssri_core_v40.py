from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ SSRI v40 — Bootlink Daemon
Ensures Savant automatically launches all core services at Termux startup.
Creates ~/.termux/boot/ directory hook for persistent runtime activation.
"""
import os
from pathlib import Path
from datetime import datetime, timezone

BOOTDIR = Path.home() / ".termux/boot"
SCRIPT  = BOOTDIR / "00_savant_boot.sh"
LOG     = Path.home() / "savant/logs/bootlink_daemon.log"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

BOOTDIR.mkdir(parents=True, exist_ok=True)
boot_script = f"""#!/data/data/com.termux/files/usr/bin/bash
echo "🚀 Savant Bootlink launching at $(date -Iseconds)" >> "$HOME/savant/logs/bootlink_daemon.log"
source "$HOME/.bashrc"
savant-supervisor
"""
SCRIPT.write_text(boot_script)
os.chmod(SCRIPT, 0o755)
log("✅ Savant Bootlink installed — autostart enabled.")
rule_status("✅ Savant Bootlink installed — autostart enabled.", "ok")


# Auto-completion safeguard
pass
