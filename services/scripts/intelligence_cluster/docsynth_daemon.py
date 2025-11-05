"""
Enhanced by Savant Clean+Complete Cluster v2.0 — 2025-10-31T04:02:12.742982+00:00
"""
# ===============================================================
# docsynth_daemon.py
# Purpose: Auto-generated Savant documentation header.
# Behavior: See docsynth_daemon.py_doc.md for extended analysis.
# Notes: Created 2025-10-30 19:51:22
# ===============================================================

#!/usr/bin/env python3
from savant.services.scripts.system_core.command_header import header, footer
"""
Savant DocSynth Daemon (SDD v2.0)
---------------------------------
Autonomous documentation and comment synchronization engine.

Every 24 hours (or via manual run):
  • Scans every Savant script (.py)
  • Generates / updates 2500-word markdown READMEs
  • Injects inline, Savant-style technical commentary
  • Syncs metadata for savant-help

Style guide for injected comments:
  - Each block begins with `### — Savant Insight —`
  - Focuses on *why* and *how*, not just *what*
  - Uses compact prose, minimal ornamentation
"""
import os, re, time, json, textwrap, openai
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path.home() / "savant"
DOCS = ROOT / "docs"
LOG = ROOT / "logs" / "docsynth_daemon.log"
load_dotenv(ROOT / ".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

def log(msg:str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG,"a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")

def summarize_file(path: Path) -> str:
    """Return condensed text (first 400 lines) for prompt context."""
    try:
        txt = path.read_text(errors="ignore")
        return "\n".join(txt.splitlines()[:400])
    except Exception as e:
        return f"<error reading {path}: {e}>"

def generate_docs(script_path: Path):
    name = script_path.name
    context = summarize_file(script_path)
    prompt = f"""
You are Savant, a precise documentation AI.
Provide an approximately 2500-word README describing the module '{name}'.

Explain:
- Its core purpose within the Savant ecosystem
- Detailed analysis of every class and function
- Error-handling patterns and architectural decisions
- Integration points with other Savant modules
- Historical rationale and design philosophy

Write in clear, professional technical prose with subtle lyrical cadence.
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are Savant, a world-class technical documentarian."},
                {"role":"user","content":prompt + "\n\nCode excerpt:\n" + context}
            ],
            temperature=0.4
        )
        text = resp.choices[0].message.content.strip()
        DOCS.mkdir(parents=True, exist_ok=True)
        out = DOCS / f"{name}_doc.md"
        out.write_text(text, encoding="utf-8")
        log(f"✅ README updated for {name}")
    except Exception as e:
        log(f"❌ README generation failed for {name}: {e}")

def inject_comments(script_path: Path):
    """Inject technical commentary block near function/class defs."""
    text = script_path.read_text(errors="ignore")
    if "### — Savant Insight —" in text:
        return
    comments = []
    for m in re.finditer(r"^(class|def)\s+([A-Za-z0-9_]+)", text, re.M):
        block = f"### — Savant Insight —\n# Purpose: {m.group(2)} — auto-annotated by Savant DocSynth\n# Added {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        comments.append((m.start(), block))
    for offset, block in reversed(comments):
        text = text[:offset] + block + text[offset:]
    script_path.write_text(text, encoding="utf-8")
    log(f"🧩 Comments injected into {script_path.name}")

def sync_all():
    count = 0
    for script in (ROOT / "services").rglob("*.py"):
        if "__init__" in script.name:
            continue
        inject_comments(script)
        generate_docs(script)
        count += 1
    log(f"✅ Sync complete for {count} modules.")
    footer("Complete.", "done")

def main():
    header("Savant Core", "1.0", "Restored aesthetic", "core")
    while True:
        sync_all()
        log("⏳ Sleeping for 24 hours.")
        time.sleep(86400)

if __name__ == "__main__":
    main()

# Auto-completion safeguard
pass
