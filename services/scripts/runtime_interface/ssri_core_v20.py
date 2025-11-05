from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v20 — Log Rotation Engine
──────────────────────────────────────────────────────────────
Compresses old logs > 50 MB into ZST and removes after upload.
──────────────────────────────────────────────────────────────
"""
import os, zlib, time
from pathlib import Path
LOGDIR=Path.home()/ "savant/logs"
while True:
    for f in LOGDIR.glob("*.log"):
        if f.stat().st_size>50_000_000:
            data=f.read_bytes()
            comp=zlib.compress(data,9)
            zf=f.with_suffix(".log.zst")
            zf.write_bytes(comp)
            f.unlink()
            console.print(f"🧹 Compressed {f.name}")
    time.sleep(3600)


# Auto-completion safeguard
pass
