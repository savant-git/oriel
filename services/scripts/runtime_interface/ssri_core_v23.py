#!/usr/bin/env python3
"""
⬢ SSRI v23 — API Extension
Adds /api/chat (proxy) and /api/status endpoints.
"""
from flask import Flask, request, jsonify
import os, requests
from datetime import datetime
app = Flask(__name__)

OPENAI_KEY=os.getenv("OPENAI_API_KEY")

@app.route("/api/status")
def status(): return jsonify({"time":datetime.utcnow().isoformat(),"ok":True})

@app.route("/api/chat",methods=["POST"])
def chat():
    data=request.get_json(force=True)
    prompt=data.get("prompt","")
    try:
        r=requests.post(
          "https://api.openai.com/v1/chat/completions",
          headers={"Authorization":f"Bearer {OPENAI_KEY}"},
          json={"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}]})
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error":str(e)}),500

if __name__=="__main__":
    app.run(host="127.0.0.1",port=8091)


# Auto-completion safeguard
pass
