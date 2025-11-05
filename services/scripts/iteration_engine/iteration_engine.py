from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
Savant Iteration Engine (SIE v1.0)
────────────────────────────────────────────────────────────────────
Performs recursive prompt iteration cycles using OpenAI or local models,
adapting prompts each round based on feedback quality and persona context.
Supports timed iteration loops and interface via FastAPI.

Non-negotiable principles:
 - Self-refinement: every output improves its own prompt.
 - Persona infusion: behavior is altered by simulated mindsets.
 - Reflection persistence: iteration memory saved to logs/iteration_history.json
"""

import os, json, asyncio, openai, random, textwrap, uvicorn
from fastapi import FastAPI, WebSocket
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
LOGS.mkdir(exist_ok=True)
HISTORY = LOGS / "iteration_history.json"
app = FastAPI(title="Savant Iteration Engine")

# ------------------- CONFIG -------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"
PERSONAS = {
    "tesla": "Think like Nikola Tesla: analytical, visionary, inventive, focused on elegant engineering.",
    "kubrick": "Think like Stanley Kubrick: visual precision, thematic depth, psychological tension.",
    "nietzsche": "Think like Friedrich Nietzsche: poetic, iconoclastic, philosophical rebellion.",
    "da_vinci": "Think like Leonardo da Vinci: polymathic, observational, artistic and scientific synthesis.",
    "collective": "Think as a collective intelligence of designers, philosophers, engineers, and artists."
}

# ------------------- CORE FUNCTIONS -------------------
def log_event(entry: dict):
    history = []
    if HISTORY.exists():
        try:
            history = json.loads(HISTORY.read_text())
        except Exception:
            history = []
    history.append(entry)
    HISTORY.write_text(json.dumps(history[-200:], indent=2))

async def generate_iteration(prompt:str, persona:str):
    sys = f"You are Savant Iteration Engine. {PERSONAS.get(persona,'Be thoughtful and precise.')}"
    r = await asyncio.to_thread(lambda: openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": f"Iteration prompt:\n{prompt}\n\nImprove and refine this idea."}
        ]
    ))
    result = r.choices[0].message.content.strip()
    return result

async def iterate(prompt:str, persona:str, interval:int, max_iters:int, ws:WebSocket=None):
    cur_prompt = prompt
    for i in range(1, max_iters+1):
        start=datetime.now(timezone.utc).isoformat()
        result = await generate_iteration(cur_prompt, persona)
        refined_prompt = await generate_iteration(f"Refine further:\n{result}", persona)
        cur_prompt = refined_prompt
        entry={
            "iteration": i,
            "timestamp": start,
            "persona": persona,
            "input": prompt,
            "result": result,
            "refined_prompt": refined_prompt
        }
        log_event(entry)
        msg = f"🌀 Iteration {i}/{max_iters} complete — persona: {persona}"
        console.print(msg)
        if ws:
            await ws.send_json(entry)
        await asyncio.sleep(interval)
    return cur_prompt

# ------------------- FASTAPI INTERFACE -------------------
@app.websocket("/iterate")
async def ws_iterate(ws:WebSocket):
    await ws.accept()
    config = await ws.receive_json()
    prompt = config.get("prompt","Design a modern logo.")
    persona = config.get("persona","collective")
    interval = int(config.get("interval",30))
    max_iters = int(config.get("max_iters",5))
    await iterate(prompt, persona, interval, max_iters, ws)
    await ws.send_text("✅ Iteration session complete.")
    await ws.close()

@app.get("/history")
def get_history():
    if HISTORY.exists():
        return json.loads(HISTORY.read_text())
    return []

@app.post("/run_once")
async def run_once(data:dict):
    result = await generate_iteration(data.get("prompt","Create something extraordinary."),
                                      data.get("persona","collective"))
    return {"result": result}

# ------------------- ENTRYPOINT -------------------
if __name__ == "__main__":
    console.print("⛓️  SIE v1.0 online — Iterative Cognitive Loop ready.")
    uvicorn.run(app, host="0.0.0.0", port=8088)


# Auto-completion safeguard
pass
