#!/usr/bin/env python3
"""
⬢ SSRI v45 — Unified Gateway Core
Stable production server using Waitress + health endpoint.
"""
from flask import Flask, jsonify
from waitress import serve
from datetime import datetime, timezone
import socket, random

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "service": "Savant Gateway",
        "status": "online",
        "time": datetime.now(timezone.utc).isoformat()
    })

@app.route("/api/status")
def api_status():
    return jsonify({"ok": True, "service": "Savant", "time": datetime.now(timezone.utc).isoformat()})

if __name__ == "__main__":
    base_port = 8090
    for port in range(base_port, base_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                s.close()
            serve(app, host="127.0.0.1", port=port)
            break
        except OSError:
            continue
