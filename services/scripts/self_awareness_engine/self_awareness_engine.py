from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧠  SAVANT SELF-AWARENESS ENGINE v1.0
Build 6 of the Autonomous Runtime Stack
───────────────────────────────────────
Evaluates Savant’s internal health, version coherence,
and module registry. Automatically triggers protection,
export, and synchronization when anomalies are detected.
"""
import os, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.home()/ "savant"
LOG  = ROOT/ "logs/self_awareness.log"
META = ROOT/ "services/meta/version_map.json"
REPORT = ROOT/ "services/meta/self_state.json"

def run(cmd):
    subprocess.run(cmd, shell=True, check=False,
        stdout=open(LOG,"a"), stderr=subprocess.STDOUT)

def scan_environment():
    services = sum(1 for _ in (ROOT/"services").rglob("*.py"))
    meta = json.loads(META.read_text()) if META.exists() else {}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services,
        "meta": meta.get("meta_version","unknown"),
        "issues": []
    }

def analyze(report):
    if report["meta"]=="unknown": report["issues"].append("version_map_missing")
    if report["services"] < 50:   report["issues"].append("incomplete_service_stack")
    return report

def auto_heal(report):
    if not report["issues"]: return
    console.print(f"⚙️ Auto-heal triggered → {report['issues']}")
    run("savant-protect")
    run("savant-export")

def persist(report):
    REPORT.write_text(json.dumps(report, indent=2))
    console.print(f"📘 Self-state recorded → {REPORT}")

def main():
    console.print(f"\n🧠 Running Savant Self-Awareness Engine at {datetime.now().isoformat()}")
    report = analyze(scan_environment())
    auto_heal(report)
    persist(report)
    rule_status("✅ SAE cycle complete.", "ok")

if __name__=="__main__":
    main()


# Auto-completion safeguard
pass
