from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
──────────────────────────────────────────────────────────────
⬢ SSRI v21 — Migration Validator Stage III
──────────────────────────────────────────────────────────────
Performs 10-point diagnostic and prints MIGRATION READY if all pass:
  1 OpenAI API    2 GitHub  3 S3  4 Server Port  5 Daemon Log  
  6 Export Engine 7 Runtime Loop 8 Version Engine  9 Integrity  10 Disk space
──────────────────────────────────────────────────────────────
"""
import os, socket, shutil, requests, boto3
from pathlib import Path
ok=[]
def chk(name,cond): ok.append(name if cond else f"{name} ❌")
def port_open(p=8080):
    s=socket.socket();res=s.connect_ex(("127.0.0.1",p))==0;s.close();return res
# Checks
chk("OpenAI",requests.get("https://api.openai.com/v1/models",
    headers={"Authorization":f"Bearer {os.getenv('OPENAI_API_KEY','')}"}
).status_code==200)
chk("GitHub",requests.get("https://api.github.com/user",
    headers={"Authorization":f"token {os.getenv('GITHUB_TOKEN','')}"}
).status_code==200)
try:boto3.client("s3").list_buckets();chk("S3",True)
except:chk("S3",False)
chk("ServerPort",port_open())
chk("DaemonLog",(Path.home()/ "savant/logs/server_daemon.log").exists())
chk("ExportEngine",(Path.home()/ "savant/services/scripts/intelligence_cluster/export_cluster.py").exists())
chk("RuntimeLoop",(Path.home()/ "savant/services/scripts/intelligence_cluster/autonomous_runtime.sh").exists())
chk("VersionEngine",(Path.home()/ "savant/services/scripts/version_engine/triadic_version_engine.py").exists())
chk("Integrity",(Path.home()/ "savant/services/guardian/immutable_guard.py").exists())
chk("DiskFree",shutil.disk_usage("/").free>500_000_000)
summary="\n".join(ok)
console.print(summary)
if all("❌" not in i for i in ok):
    rule_status("✅ MIGRATION READY — You can safely run Savant natively.", "ok")
else:
    rule_status("⚠️ Migration not yet ready.", "warn")


# Auto-completion safeguard
pass
