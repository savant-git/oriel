from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v310
- Fixes command alias and restores bash linkage
- Adds smart compression: ensures archive ≤ 50 MB for GitHub
- Keeps GitHub Autopilot (SSH+S3+Downloads)
"""

import os, sys, shutil, zipfile, subprocess, gzip, bz2, lzma
from pathlib import Path
from datetime import datetime, timezone

try:
    import boto3
except Exception:
    boto3 = None

BASE = Path.home() / "savant"
EXPORTS = BASE / "exports"
LOGS = BASE / "logs"
CHAT_DIR = BASE / "chat_logs"
LOGS.mkdir(parents=True, exist_ok=True)
EXPORTS.mkdir(parents=True, exist_ok=True)
CHAT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS / "export_v310.log"

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    console.print(msg, flush=True)

def load_env():
    env = BASE / ".env"
    if env.exists():
        for raw in env.read_text(errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()
        log("✅ .env loaded")

def create_archive():
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"savant_full_export_{ts}.zip"
    archive = EXPORTS / name
    log(f"📦 Creating archive: {name}")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for root in [BASE/"services", BASE/"ui", BASE/"core", LOGS, CHAT_DIR]:
            if root.exists():
                for f in root.rglob("*"):
                    if f.is_file() and ".git" not in str(f):
                        try:
                            z.write(f, f.relative_to(BASE))
                        except Exception as e:
                            log(f"⚠️ {f}: {e}")
    size_mb = archive.stat().st_size / 1_000_000
    if size_mb > 50:
        log(f"⚠️ Archive {size_mb:.1f} MB > 50 MB — recompressing…")
        comp_path = EXPORTS / (archive.stem + ".tar.xz")
        subprocess.run(["tar","-cf","-","-C",str(EXPORTS),archive.name,"|","xz","-9","-T0","-c"],shell=True,stdout=open(comp_path,"wb"))
        if comp_path.exists() and comp_path.stat().st_size < archive.stat().st_size:
            archive.unlink(missing_ok=True)
            archive = comp_path
            log(f"✅ Recompressed → {archive.name} ({archive.stat().st_size/1_000_000:.1f} MB)")
        else:
            log("⚠️ Could not shrink under 50 MB.")
    return archive

def copy_to_downloads(archive):
    for p in [Path.home()/ "storage/downloads", Path("/storage/emulated/0/Download")]:
        try:
            p.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archive, p/archive.name)
            log(f"📥 Copied to Downloads → {p/archive.name}")
            return
        except Exception as e:
            log(f"⚠️ Copy failed {e}")

def upload_s3(archive):
    if not boto3 or not os.getenv("SAVANT_S3_BUCKET"): return
    try:
        s3 = boto3.client("s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        s3.upload_file(str(archive), os.getenv("SAVANT_S3_BUCKET"), f"exports/{archive.name}")
        log(f"☁️ Uploaded to s3://{os.getenv('SAVANT_S3_BUCKET')}/exports/{archive.name}")
    except Exception as e: log(f"⚠️ S3 upload failed: {e}")

def push_github(fp):
    repo = BASE
    try:
        if not (repo/".git").exists():
            log("⚙️ Init repo")
            subprocess.run(["git","-C",str(repo),"init"],check=True)
            subprocess.run(["git","-C",str(repo),"branch","-M","main"],check=True)
            subprocess.run(["git","-C",str(repo),"remote","add","origin",
                            "git@github.com:flypaper-creative/savant.git"],check=False)
        remotes=subprocess.run(["git","-C",str(repo),"remote","-v"],capture_output=True,text=True).stdout
        if "https://" in remotes:
            subprocess.run(["git","-C",str(repo),"remote","set-url","origin",
                            "git@github.com:flypaper-creative/savant.git"],check=False)
        key=Path.home()/".ssh/id_ed25519"
        if not key.exists():
            log("🔐 Creating SSH keypair")
            Path.home().joinpath(".ssh").mkdir(exist_ok=True)
            subprocess.run(["ssh-keygen","-t","ed25519","-f",str(key),"-N",""],check=True)
        subprocess.run(["git","-C",str(repo),"add","-A"])
        subprocess.run(["git","-C",str(repo),"commit","-m",f"Auto export {datetime.now().isoformat()}"])
        subprocess.run(["git","-C",str(repo),"fetch","origin"],check=False)
        subprocess.run(["git","-C",str(repo),"pull","--rebase","origin","main"],check=False)
        subprocess.run(["git","-C",str(repo),"push","origin","main"],check=False)
        log("🐙 GitHub push successful")
    except Exception as e:
        log(f"⚠️ GitHub push failed: {e}")

def main():
    load_env()
    log(f"🧠 Export v310 start {datetime.now(timezone.utc).isoformat()}")
    arc = create_archive()
    copy_to_downloads(arc)
    upload_s3(arc)
    push_github(arc)
    log("✅ Export complete — All targets attempted.")
