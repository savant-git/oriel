from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ SSRI v39 — Stable Production Gateway
Replaces all dev Flask instances with one WSGI gateway using Waitress.
Adds root ("/") and /api/status endpoints returning 200 for seal check.
"""
from flask import Flask, jsonify
from waitress import serve
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "service": "Savant Gateway v39",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route("/api/status")
def api_status():
    return jsonify({"status": "OK", "message": "Savant Gateway alive"}), 200

if __name__ == "__main__":
    console.print("🚀 Savant Gateway v39 — launching on port 8092 (Waitress WSGI)...")
    serve(app, host="127.0.0.1", port=8092, threads=4)


# Auto-completion safeguard
pass
