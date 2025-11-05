"""
api_codeview.py — Safe code-read and suggestion interface.
Lets the local chat view code and return rewritten code
for human review and manual application.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, time, hashlib

app = FastAPI(title="Savant Code Access", version="2025.11")

BASE_DIR = os.path.expanduser("~/savant")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def safe_path(p: str) -> str:
    path = os.path.abspath(os.path.expanduser(p))
    if not path.startswith(BASE_DIR):
        raise PermissionError("Access limited to ~/savant")
    return path

@app.post("/read_file")
async def read_file(payload: dict):
    """Return source code for inspection."""
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

@app.post("/save_suggestion")
async def save_suggestion(payload: dict):
    """
    Store an AI-proposed rewrite as a text file for manual review.
    Does not overwrite the source file.
    """
    path = payload.get("path", "")
    new_code = payload.get("code", "")
    if not path or not new_code:
        return {"error": "path and code required"}
    try:
        safe_path(path)
        stamp = int(time.time())
        log_file = os.path.join(LOG_DIR, f"suggestion_{stamp}.txt")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Suggested rewrite for: {path}\n\n{new_code}")
        return {"status": "saved", "proposal": log_file}
    except Exception as e:
        return {"error": str(e)}
