#!/usr/bin/env python3
"""
SAVANT CORE — Rule-Enforced OpenAI Backend (Reference-Number Edition)
Loads API key from ~/savant/.env and enforces reference numbers
and line numbering in every chat reply.
"""

from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.responses import JSONResponse
import openai, os, hashlib, logging, time
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

# ==========================================================
# ENVIRONMENT SETUP
# ==========================================================
ENV_PATH = os.path.expanduser("~/savant/.env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

openai.api_key = os.getenv("OPENAI_API_KEY")

RULE_PATH = os.path.expanduser("~/savant/docs/PROJECT_RULES.md")
LOG_DIR = os.path.expanduser("~/savant/logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "savant_core.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

# ==========================================================
# RULE HELPERS
# ==========================================================
def read_rules():
    try:
        with open(RULE_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

def hash_rules():
    text = read_rules()
    return hashlib.sha256(text.encode()).hexdigest() if text else "none"

def enforce_rule_integrity():
    text = read_rules()
    if not text:
        raise HTTPException(status_code=500, detail="PROJECT_RULES.md missing or empty")
    return hash_rules(), text

# ==========================================================
# FASTAPI APP
# ==========================================================
app = FastAPI(title="Savant Core", version="2025.11")

@app.middleware("http")
async def guard(request: Request, call_next):
    before = hash_rules()
    response = await call_next(request)
    after = hash_rules()
    if before != after:
        return JSONResponse(status_code=403, content={"error": "RULESET_CHANGED_DURING_REQUEST"})
    return response

@app.get("/")
async def status():
    return {"status": "ok", "rule_hash": hash_rules()}

# ==========================================================
# MAIN CHAT ENDPOINT
# ==========================================================
@app.post("/chat")
async def chat(payload: dict):
    rule_hash, rule_text = enforce_rule_integrity()
    msg = payload.get("message", "").strip()
    if not msg:
        return {"error": "Empty message."}
    sid = payload.get("session_id") or str(uuid4())

    # =================== System Prompt =====================
    system_prompt = (
        "You are the Savant AI Core.\n"
        "Always and silently obey every rule from PROJECT_RULES.md.\n"
        "You must include in EVERY reply:\n"
        " • A reference number in the format [#xxxx] where xxxx is a 4-digit sequence starting at 0001.\n"
        " • Line numbers (1., 2., 3., …) for multi-line responses.\n"
        " • No restatement of the rules unless explicitly asked.\n"
        " • Concise, technically precise, and helpful output focused on the Savant project.\n"
        "Increment the reference number for each new user interaction.\n\n"
        f"{rule_text}"
    )

    try:
        t0 = time.time()
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg},
            ],
            temperature=0.3,
            max_tokens=1200,
        )
        dt = round(time.time() - t0, 2)
        reply = response.choices[0].message.content.strip()
        logging.info(f"CHAT {sid[:8]} {rule_hash} {dt}s {msg[:80]}")
        return {
            "reply": reply,
            "session_id": sid,
            "rule_hash": rule_hash,
            "latency_sec": dt,
        }
    except Exception as e:
        logging.error(str(e))
        return {"error": str(e)}

# ==========================================================
# WEBSOCKET (optional streaming)
# ==========================================================
@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Savant Core websocket ready.")
    while True:
        msg = await ws.receive_text()
        await ws.send_text(f"[{hash_rules()[:8]}] {msg}")
