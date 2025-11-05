from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Cleanup v5.0 — Dependency Rebuild
Restores pip packages from latest dependency manifest.
"""
from pathlib import Path
import subprocess
MANIFESTS = sorted(Path.home().glob("savant/dependency_manifest_*.txt"))
if MANIFESTS:
    latest = MANIFESTS[-1]
    console.print(f"📦 Rebuilding from {latest}")
    subprocess.run(["pip","install","-r",str(latest)])
else:
    rule_status("⚠️ No dependency manifests found.", "warn")
