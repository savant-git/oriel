from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧠 Savant Archive v261 — Unified Extract + Export Pipeline
"""
import os, subprocess, time
from datetime import datetime

def run(cmd):
    console.print(f"[{datetime.now():%H:%M:%S}] 🚀 Running: {cmd}")
    subprocess.run(cmd, shell=True)

def main():
    console.print(f"[{datetime.now():%H:%M:%S}] 🧠 Savant Archive v261 — Starting unified extract + export")
    run("python3 ~/savant/services/scripts/intelligence_cluster/savant_extract_v100.py")
    run("python3 ~/savant/services/scripts/intelligence_cluster/savant_export_v191.py")
    console.print(f"[{datetime.now():%H:%M:%S}] 🏁 Archive complete — All tasks successful.")

if __name__ == "__main__":
    main()
