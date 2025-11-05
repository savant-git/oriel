#!/usr/bin/env python3
"""
⬢ SSRI v42 — Self-Learning Interval Loop
Triggers autonomous learning and synthesis cycles at defined intervals.
"""
import os, subprocess, time
from pathlib import Path
from datetime import datetime, timezone

LOG = Path.home()/ "savant/logs/self_learning_loop.log"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

INTERVAL_MINUTES = 60  # adjustable
while True:
    log("🧠 Initiating autonomous learning cycle...")
    try:
        subprocess.run(["python3", str(Path.home()/ "savant/services/scripts/intelligence_cluster/autonomous_knowledge_cluster.py")])
        log("✅ Knowledge cluster updated.")
        subprocess.run(["python3", str(Path.home()/ "savant/services/scripts/intelligence_cluster/intelligence_loop.py")])
        log("✅ Intelligence loop complete.")
    except Exception as e:
        log(f"❌ Learning error: {e}")
    log(f"⏳ Waiting {INTERVAL_MINUTES} minutes before next cycle.")
    time.sleep(INTERVAL_MINUTES * 60)


# Auto-completion safeguard
pass
