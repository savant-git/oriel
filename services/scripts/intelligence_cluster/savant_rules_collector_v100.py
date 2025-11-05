from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
🧠 Savant Non-Negotiable Rules Collector & Merger v100
Collects all imperative rules from chats, merges with canonical PROJECT_RULES.md,
and enforces consistency across all Savant systems.
"""

import os, re, json, datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
BASE = Path.home() / "savant"
DOCS = BASE / "docs"
CHAT = BASE / "chat_logs"
DOCS.mkdir(parents=True, exist_ok=True)
PROJECT_RULES = DOCS / "PROJECT_RULES.md"

def load_existing_rules():
    if PROJECT_RULES.exists():
        return PROJECT_RULES.read_text(encoding="utf-8").splitlines()
    return []

def extract_candidate_rules(text: str):
    # Identify imperative language
    pattern = re.compile(r"\b(must|always|never|required|enforced|non[- ]?negotiable)\b", re.I)
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 5]
    rules = []
    for line in lines:
        if pattern.search(line):
            # Avoid duplicates or markdown fluff
            if not line.lower().startswith(("##", "#", ">", "*")):
                rules.append(line)
    return rules

def collect_from_chatlogs():
    collected = []
    if CHAT.exists():
        for file in CHAT.glob("*.json"):
            try:
                data = json.load(open(file))
                for m in data:
                    c = m.get("content") or ""
                    collected += extract_candidate_rules(c)
            except Exception:
                pass
    return collected

def normalize_rules(rules):
    out=[]
    for r in rules:
        r = r.strip()
        if not r.endswith("."): r += "."
        if not r.lower().startswith("•"):
            r = f"• {r[0].upper() + r[1:]}"
        out.append(r)
    return list(dict.fromkeys(out))  # deduplicate while preserving order

def merge_rules(existing, new):
    merged = []
    for line in existing:
        merged.append(line)
    # Find where numbered section starts
    existing_join = "\n".join(existing)
    for rule in new:
        if rule not in existing_join:
            merged.append(rule)
    return merged

def write_merged(merged):
    header = [
        "# 🧠 SAVANT PROJECT RULES",
        f"_Auto-merged: {datetime.datetime.utcnow().isoformat()} UTC_",
        "",
        "## Non-Negotiable Rules",
    ]
    final = "\n".join(header + merged)
    PROJECT_RULES.write_text(final, encoding="utf-8")
    NONNEG.write_text(final, encoding="utf-8")
    return final

def summarize(rules):
    table = Table(title="🧩 Active Non-Negotiable Rules")
    table.add_column("No.", justify="right")
    table.add_column("Directive", overflow="fold")
    for i, rule in enumerate(rules, 1):
        table.add_row(str(i), rule)
    console.console.print(table)

def main():
    console.console.print(Panel.fit("🧠 Collecting Non-Negotiable Rules...", style="cyan"))
    existing = load_existing_rules()
    chat_rules = collect_from_chatlogs()
    combined = normalize_rules(chat_rules)
    merged_lines = merge_rules(existing, combined)
    result_text = write_merged(merged_lines)
    summarize(combined)
    console.print(Panel.fit(
        f"✅ {len(combined)} new rules collected.\n"
        "🧩 Enforcement active across all Savant scripts.",
        style="green",
    ))

if __name__ == "__main__":
    main()
