from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⚙️  SAVANT AUTONOMOUS ITERATION CORE  v2.0
──────────────────────────────────────────
Text + Visual Co-Iteration Engine
Each cycle refines both textual and visual outputs using
OpenAI GPT + image models (or other providers in future).
"""
import os, json, time, requests
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home()/ "savant"
LOG  = ROOT/ "logs/iteration_core_v2.log"
OUT  = ROOT/ "exports"/"iterations"
OUT.mkdir(parents=True, exist_ok=True)

INTERVALS = {"10s":10,"1m":60,"5m":300,"30m":1800}
PERSONAS = {
  "bauhaus_designer": "minimalist geometric thinker valuing balance, clarity, and rhythm.",
  "da_vinci_thinker": "Renaissance inventor blending art, anatomy, and engineering brilliance.",
  "elon_engineer": "iterative technologist focused on rapid prototyping and impact.",
  "zen_architect": "quiet perfectionist designing through harmony and emptiness.",
  "savant_default": "supreme intelligence in design, branding, and development."
}

def gpt_call(prompt:str, persona:str):
    key=os.getenv("OPENAI_API_KEY")
    proj=os.getenv("OPENAI_PROJECT")
    headers={"Authorization":f"Bearer {key}"}
    if proj: headers["OpenAI-Project"]=proj
    payload={
        "model":"gpt-4o-mini",
        "messages":[
            {"role":"system","content":f"You are {persona}"},
            {"role":"user","content":prompt}
        ]
    }
    r=requests.post("https://api.openai.com/v1/chat/completions",
                    headers=headers,json=payload,timeout=90)
    if r.status_code!=200:
        return f"[Error {r.status_code}] {r.text[:160]}"
    return r.json()["choices"][0]["message"]["content"]

def image_call(prompt:str, folder:Path, idx:int):
    key=os.getenv("OPENAI_API_KEY")
    headers={"Authorization":f"Bearer {key}"}
    payload={"model":"gpt-image-1","prompt":prompt,"size":"1024x1024"}
    r=requests.post("https://api.openai.com/v1/images/generations",
                    headers=headers,json=payload,timeout=120)
    if r.status_code!=200:
        return f"[Image Error {r.status_code}] {r.text[:160]}"
    b64=r.json()["data"][0]["b64_json"]
    import base64; img=base64.b64decode(b64)
    fp=folder/f"iter_{idx:03d}.png"; fp.write_bytes(img)
    return f"🖼 Generated {fp.name}"

def iteration_loop(base_prompt:str, persona_key:str, interval:str, max_cycles:int=5):
    persona=PERSONAS.get(persona_key,PERSONAS["savant_default"])
    delay=INTERVALS.get(interval,60)
    session=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    folder=OUT/f"iteration_v2_{session}"
    folder.mkdir(parents=True,exist_ok=True)
    console.print(f"🧠 Starting AIC v2.0 session {session}")
    prompt=base_prompt
    for i in range(1,max_cycles+1):
        console.print(f"⏳ Cycle {i}/{max_cycles} [{persona_key}] → delay {delay}s")
        time.sleep(delay)
        result=gpt_call(prompt,persona)
        (folder/f"iter_{i:03d}.txt").write_text(result)
        rule_status(f"✅ Saved text iteration {i}", "ok")
        img_status=image_call(prompt,folder,i)
        console.print(img_status)
        prompt=f"Evaluate and refine the previous output and visual for greater clarity and creativity.\n\nText preview:\n{result[:180]}"
    console.print(f"✨ All {max_cycles} text+image iterations complete → {folder}")

def main():
    console.print(f"\n🚀 SAVANT AIC v2.0 — {datetime.now().isoformat()}")
    base=input("🧩 Enter base prompt: ").strip()
    persona=input(f"🎭 Choose persona {list(PERSONAS.keys())}: ").strip() or "savant_default"
    interval=input(f"⏱ Choose interval {list(INTERVALS.keys())}: ").strip() or "1m"
    cycles=int(input("🔁 How many iterations (1-20)? ").strip() or "5")
    iteration_loop(base,persona,interval,cycles)

if __name__=="__main__":
    main()


# Auto-completion safeguard
pass
