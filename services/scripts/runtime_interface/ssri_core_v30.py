#!/usr/bin/env python3
"""
⬢ SSRI v30 — Safe Shutdown API
Allows remote POST /shutdown to gracefully end all Savant daemons.
"""
from flask import Flask,request,jsonify
import os,signal
from datetime import datetime
app=Flask(__name__)

@app.route("/shutdown",methods=["POST"])
def shutdown():
    os.kill(os.getpid(),signal.SIGINT)
    return jsonify({"ok":True,"message":"Savant shutting down","time":datetime.utcnow().isoformat()})

if __name__=="__main__":
    app.run(host="127.0.0.1",port=8099)


# Auto-completion safeguard
pass
