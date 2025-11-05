#!/usr/bin/env python3
"""
⬢ SSRI v25 — Persistence Bridge
Connects Gateway to the Savant DB / logs system.
"""
import sqlite3,os
from flask import Flask,request,jsonify
from datetime import datetime
DB=os.path.expanduser("~/savant/data/savant.db")
os.makedirs(os.path.dirname(DB),exist_ok=True)
app=Flask(__name__)

def log_entry(role,msg):
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS chatlog(ts TEXT, role TEXT, msg TEXT)")
        c.execute("INSERT INTO chatlog VALUES(?,?,?)",(datetime.utcnow().isoformat(),role,msg))
        c.commit()

@app.route("/api/store",methods=["POST"])
def store():
    d=request.get_json(force=True)
    log_entry(d.get("role","user"),d.get("msg",""))
    return jsonify({"ok":True})

@app.route("/api/history")
def history():
    with sqlite3.connect(DB) as c:
        rows=c.execute("SELECT * FROM chatlog ORDER BY ts DESC LIMIT 20").fetchall()
    return jsonify([{"time":r[0],"role":r[1],"msg":r[2]} for r in rows])

if __name__=="__main__":
    app.run(host="127.0.0.1",port=8093)


# Auto-completion safeguard
pass
