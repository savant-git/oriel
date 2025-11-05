#!/usr/bin/env python3
"""
⬢ SSRI v24 — Visual Console
Serves a lightweight HTML dashboard for runtime monitoring.
"""
from flask import Flask,send_from_directory,jsonify
from pathlib import Path
from datetime import datetime
import psutil,os

app=Flask(__name__,static_folder=str(Path.home()/ "savant/services/web/dashboard"))
@app.route("/")
def index(): return send_from_directory(app.static_folder,"index.html")

@app.route("/api/sysinfo")
def sysinfo():
    cpu=psutil.cpu_percent(interval=0.5)
    mem=psutil.virtual_memory().percent
    return jsonify({"time":datetime.utcnow().isoformat(),"cpu":cpu,"mem":mem})

if __name__=="__main__":
    app.run(host="127.0.0.1",port=8092)


# Auto-completion safeguard
pass
