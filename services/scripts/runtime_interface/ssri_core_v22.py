#!/usr/bin/env python3
"""
⬢ SSRI v22 — Gateway Core
Minimal HTTP layer that exposes the runtime loop and OpenAI link.
"""
from flask import Flask, jsonify
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def root(): return jsonify({"savant":"online","version":"v22"})

@app.route("/api/ping")
def ping(): return jsonify({"time":datetime.utcnow().isoformat()})

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8090)


# Auto-completion safeguard
pass
