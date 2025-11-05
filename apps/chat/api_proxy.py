from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import requests, os

AI_CORE = "http://127.0.0.1:8000"  # Savant AI Core endpoint
app = FastAPI(title="Savant Chat Proxy")

@app.get("/")
async def root():
    try:
        r = requests.get(f"{AI_CORE}/")
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/chat")
async def chat(msg: dict):
    r = requests.post(f"{AI_CORE}/chat", json=msg, timeout=120)
    return r.json()

@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    r = requests.post(f"{AI_CORE}/upload",
                      files={"file": (file.filename, await file.read())})
    return r.json()

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Savant Chat connected to AI Core.")
    while True:
        data = await ws.receive_text()
        r = requests.post(f"{AI_CORE}/chat", json={"message": data}).json()
        await ws.send_json(r)
