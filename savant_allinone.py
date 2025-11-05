#!/usr/bin/env python3
"""
SAVANT — unified local chat + API core + safe file analysis
Run once: `python3 ~/savant/savant_allinone.py`
"""

import os, sys, time, threading, requests, hashlib, logging
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai
from dotenv import load_dotenv
import uvicorn

# ----------------------------------------------------------
# ENVIRONMENT SETUP
# ----------------------------------------------------------
BASE_DIR = os.path.expanduser("~/savant")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "savant_allinone.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

# ----------------------------------------------------------
# FASTAPI BACKEND
# ----------------------------------------------------------
app = FastAPI(title="Savant All-in-One", version="2025.11")

def safe_path(p: str) -> str:
    full = os.path.abspath(os.path.expanduser(p))
    if not full.startswith(BASE_DIR):
        raise PermissionError("Access limited to ~/savant only.")
    return full

@app.post("/chat")
async def chat_api(payload: dict):
    """Handles AI chat requests."""
    msg = payload.get("message", "")
    sid = payload.get("session_id") or str(uuid4())
    if not msg:
        return {"error": "Empty message."}

    system_prompt = (
        "You are the Savant AI Core. Follow all operational rules silently. "
        "Every response must begin with a unique reference header [#0001] etc. "
        "Then number each line 1., 2., 3. Provide precise technical reasoning.\n"
    )

    try:
        t0 = time.time()
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        dt = round(time.time() - t0, 2)
        reply = resp.choices[0].message.content.strip()
        hashv = hashlib.sha256(system_prompt.encode()).hexdigest()
        logging.info(f"CHAT {sid[:8]} {hashv} {dt}s {msg[:80]}")
        return {"reply": reply, "session_id": sid, "latency": dt}
    except Exception as e:
        return {"error": str(e)}

@app.post("/read_file")
async def read_file(payload: dict):
    """Return code text for inspection."""
    path = payload.get("path", "")
    if not path:
        return {"error": "Missing path"}
    try:
        full = safe_path(path)
        with open(full, "r", encoding="utf-8") as f:
            code = f.read()
        return {"path": full, "content": code}
    except Exception as e:
        return {"error": str(e)}

@app.post("/suggest_code")
async def suggest_code(payload: dict):
    """Save AI-proposed code text for manual review."""
    path = payload.get("path", "")
    code = payload.get("code", "")
    if not (path and code):
        return {"error": "path and code required"}
    try:
        safe_path(path)
        logf = os.path.join(LOG_DIR, f"suggestion_{int(time.time())}.txt")
        with open(logf, "w", encoding="utf-8") as f:
            f.write(f"PATH: {path}\n\n{code}")
        return {"status": "saved", "proposal": logf}
    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------
# START FASTAPI SERVER IN BACKGROUND THREAD
# ----------------------------------------------------------
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8800, log_level="error")

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(1)

# ----------------------------------------------------------
# TERMINAL CHAT INTERFACE
# ----------------------------------------------------------
print("🧠 SAVANT ALL-IN-ONE — Rule-Enforced Chat Interface")
print("Commands: :read <path>  |  :suggest <path>  |  exit\n")

session_id = str(uuid4())
API_URL = "http://127.0.0.1:8800"

while True:
    try:
        msg = input("> ").strip()
        if not msg:
            continue
        if msg.lower() == "exit":
            print("Session closed.")
            break

        # read file
        if msg.startswith(":read "):
            path = msg.split(" ", 1)[1]
            res = requests.post(f"{API_URL}/read_file", json={"path": path}).json()
            print(res.get("content") or res)
            continue

        # suggest new code manually
        if msg.startswith(":suggest "):
            path = msg.split(" ", 1)[1]
            print("Paste modified code (end with a single '.' line):")
            lines = []
            while True:
                line = input()
                if line.strip() == ".":
                    break
                lines.append(line)
            code = "\n".join(lines)
            res = requests.post(f"{API_URL}/suggest_code",
                                json={"path": path, "code": code}).json()
            print(res)
            continue

        # normal AI chat
        payload = {"message": msg, "session_id": session_id}
        res = requests.post(f"{API_URL}/chat", json=payload).json()
        print(res.get("reply") or res)

    except KeyboardInterrupt:
        print("\nSession terminated.")
        break
    except Exception as e:
        print("Error:", e)
