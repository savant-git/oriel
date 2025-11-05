#!/usr/bin/env python3
"""
💬 Savant Web Chat v10
--------------------------------------------------------------
Minimal FastAPI web UI for Savant.
Connects to savant.ai_core.savant_core_v70.ask()
Accessible via http://<vm-ip>:8000
--------------------------------------------------------------
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn, os, sys

# === Make sure savant is importable ===
sys.path.append(str(Path.home()))

from savant.ai_core.savant_core_v70 import ask

app = FastAPI(title="Savant Web Chat", version="v10")

BASE = Path.home() / "savant"
LOGS = BASE / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

# === Serve static frontend ===
app.mount("/static", StaticFiles(directory=str(BASE / "services/web/static")), name="static")

# === Routes ===
@app.get("/", response_class=HTMLResponse)
def index():
    html = """
    <html>
    <head>
        <title>Savant Web Chat</title>
        <style>
            body {
                background-color: #1b1b1b;
                color: #e5e5e5;
                font-family: 'Inter', sans-serif;
                margin: 0; padding: 0;
            }
            .header {
                background-color: #2b2b2b;
                padding: 1rem;
                text-align: center;
                font-size: 1.5rem;
                color: #FFD700;
                border-bottom: 1px solid #333;
            }
            .chatbox {
                display: flex;
                flex-direction: column;
                height: 90vh;
                overflow-y: auto;
                padding: 1rem;
            }
            .msg {
                margin: 0.5rem 0;
                line-height: 1.4;
            }
            .user { color: #FFD700; }
            .bot { color: #c4c4c4; }
            form {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #2b2b2b;
                padding: 1rem;
            }
            input {
                width: 80%;
                padding: 0.5rem;
                border-radius: 4px;
                border: none;
            }
            button {
                background-color: #FFD700;
                color: #1b1b1b;
                border: none;
                padding: 0.5rem 1rem;
                margin-left: 0.5rem;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="header">🧠 Savant Web Chat</div>
        <div id="chatbox" class="chatbox"></div>
        <form id="chatForm">
            <input type="text" id="userInput" placeholder="Type your message..." autofocus required/>
            <button type="submit">Send</button>
        </form>
        <script>
            const form = document.getElementById('chatForm');
            const input = document.getElementById('userInput');
            const chatbox = document.getElementById('chatbox');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const text = input.value.trim();
                if (!text) return;
                chatbox.innerHTML += `<div class="msg user">🧠 You: ${text}</div>`;
                input.value = '';
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                chatbox.innerHTML += `<div class="msg bot">🤖 Savant: ${data.reply}</div>`;
                chatbox.scrollTop = chatbox.scrollHeight;
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    reply = ask(message)
    return JSONResponse({"reply": reply})

if __name__ == "__main__":
    uvicorn.run("savant.services.web.savant_web_v10:app", host="0.0.0.0", port=8000, reload=False)
