from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Display all registered Savant Iteration Engine upgrades.
"""
import json, pathlib
REG = pathlib.Path.home()/ "savant/services/scripts/iteration_engine/layer_registry.json"
data=json.loads(REG.read_text())
layers={}
for e in data:
    layers.setdefault(e["layer"],[]).append(e)
for k,v in layers.items():
    console.print(f"\n\033[93m{k}\033[0m — {len(v)} modules")
    for e in v[:5]:
        console.print(f"   {e['id']:03d}: {e['path']}")
console.print(f"\nTotal modules: {len(data)}")


# Auto-completion safeguard
pass
