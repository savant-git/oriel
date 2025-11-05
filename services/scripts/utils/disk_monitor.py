from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Cleanup v5.0 — Disk Monitor
Auto-triggers cleanup when free space < 5 GB.
"""
import shutil, subprocess
free_gb = shutil.disk_usage("/data/data/com.termux/files/home").free / (1024**3)
console.print(f"💾 Free space: {free_gb:.2f} GB")
if free_gb < 5:
    rule_status("⚠️  Low disk space — running savant-clean automatically.", "warn")
    subprocess.Popen(["bash","~/savant/services/scripts/utils/savant_clean_orchestrator.sh"])
else:
    rule_status("✅ Disk space OK.", "ok")
