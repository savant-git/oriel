#!/usr/bin/env python3
"""
Savant Chat CLI — interacts with the local AI Core through HTTP.
"""

import requests, uuid, time, json, os

API = "http://127.0.0.1:8000/chat"
session_id = str(uuid.uuid4())

print("🧠 Savant Chat CLI connected to AI Core")
print(f"Session ID: {session_id[:8]}")
print("Type 'exit' to quit.\n")

while True:
    msg = input("> ").strip()
    if msg.lower() in {"exit", "quit"}:
        print("Session closed.")
        break

    payload = {"message": msg, "session_id": session_id}
    t0 = time.time()
    try:
        r = requests.post(API, json=payload, timeout=180)
        dt = time.time() - t0
    except Exception as e:
        print("Connection error:", e)
        continue

    try:
        data = r.json()
    except Exception:
        print("Invalid response:", r.text)
        continue

    reply = data.get("reply", "")
    rule_hash = data.get("rule_hash", "none")[:8]
    adh = data.get("adherence", data.get("adherence_score", 0))
    print(f"\n[# {session_id[:6]}-{rule_hash}] ({dt:.2f}s) adherence:{adh}")
    print(reply)
    print()
