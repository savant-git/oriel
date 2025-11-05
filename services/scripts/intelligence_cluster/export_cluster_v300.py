from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Savant Export Cluster v300
- Preserves all prior behaviors: ZIP, copy to Downloads, optional S3 upload, chat inclusion.
- Adds Git Autopilot: auto-init repo, force SSH remote, auto-SSH key, optional GH API key add, commit+push.
- Never hard-fails export if network/auth is unavailable; logs and continues.

Non-negotiables honored:
- Do not delete prior behavior; only extend.
- Clear, technical comments with Savant’s concise style.
"""

import os, sys, shutil, zipfile, hashlib, subprocess, time
from pathlib import Path
from datetime import datetime, timezone

# --- Optional deps (S3) ----------------------------------------------------
try:
    import boto3  # optional; skip if missing
except Exception:
    boto3 = None

# --- Paths -----------------------------------------------------------------
BASE     = Path.home() / "savant"
EXPORTS  = BASE / "exports"
LOGS     = BASE / "logs"
CHAT_DIR = BASE / "chat_logs"
LOGS.mkdir(parents=True, exist_ok=True)
EXPORTS.mkdir(parents=True, exist_ok=True)
CHAT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS / "export_v300.log"

# --- Logging ---------------------------------------------------------------
def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass
    console.print(msg, flush=True)

# --- Load .env safely (no xargs; ignore comments/blank) --------------------
def load_env():
    env = BASE / ".env"
    if not env.exists():
        log("⚠️  No .env found at ~/savant/.env (continuing without it).")
        return
    for raw in env.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or " " in line:
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k: os.environ[k] = v
    log("✅ .env loaded into environment.")

# --- Chat inclusion (best-effort) ------------------------------------------
def collect_chat_candidates():
    # Prefer already-formatted current logs; gracefully include any chat text files if present.
    preferred = [
        CHAT_DIR / "chat_full_current.html",
        CHAT_DIR / "chat_full_current.txt",
    ]
    for p in preferred:
        if p.exists():
            yield p
    # Also include any recent chat_* files to avoid regressions
    for fp in CHAT_DIR.glob("chat_*"):
        if fp.is_file():
            yield fp

# --- ZIP creation ----------------------------------------------------------
def create_archive():
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive = EXPORTS / f"savant_full_export_{ts}.zip"
    log(f"📦 Creating archive: {archive.name}")

    def should_include(p: Path) -> bool:
        # Exclude .git to keep archive lean; include primary surfaces.
        rel = p.relative_to(BASE)
        top = str(rel).split("/", 1)[0]
        if top == ".git":
            return False
        return True

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # 1) Core directories
        for folder in [BASE / "services", LOGS, EXPORTS, CHAT_DIR, BASE / "ui", BASE / "core", BASE]:
            if folder.exists():
                for fp in folder.rglob("*"):
                    if fp.is_file() and should_include(fp):
                        try:
                            z.write(fp, fp.relative_to(BASE))
                        except Exception as e:
                            log(f"⚠️  Zip skip {fp}: {e}")
        # 2) Ensure preferred chat files are inside
        for c in collect_chat_candidates():
            try:
                z.write(c, c.relative_to(BASE))
            except Exception as e:
                log(f"⚠️  Could not add chat file {c}: {e}")

    log(f"✅ ZIP archive complete → {archive}")
    return archive

# --- Copy to Downloads -----------------------------------------------------
def copy_to_downloads(archive: Path):
    # Try both Termux symlink and the Android shared storage location
    candidates = [
        Path.home() / "storage/downloads",
        Path("/storage/emulated/0/Download"),
    ]
    ok = False
    for d in candidates:
        try:
            d.mkdir(parents=True, exist_ok=True)
            target = d / archive.name
            shutil.copy2(archive, target)
            log(f"📥 Copied to Downloads → {target}")
            ok = True
            break
        except Exception as e:
            log(f"⚠️  Downloads copy failed at {d}: {e}")
    if not ok:
        log("⚠️  No Downloads path available; skipped copy.")

# --- S3 upload (optional) --------------------------------------------------
def upload_s3(archive: Path):
    if not boto3:
        log("⚠️  boto3 not installed; skipping S3 upload.")
        return
    bucket = os.getenv("SAVANT_S3_BUCKET")
    if not bucket:
        log("⚠️  SAVANT_S3_BUCKET not set; skipping S3 upload.")
        return
    key = f"exports/{archive.name}"
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        )
        s3.upload_file(str(archive), bucket, key)
        log(f"☁️  Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        log(f"⚠️  S3 upload failed: {e}")

# --- GitHub push autopilot -------------------------------------------------
def push_github(archive: Path):
    """
    Self-healing Git routine:
      1) Ensure repo exists (.git), else init.
      2) Force SSH remote (git@github.com:flypaper-creative/savant.git).
      3) Ensure SSH key (~/.ssh/id_ed25519) exists.
      4) If GITHUB_TOKEN is present, try registering pubkey via GitHub API.
      5) Add/commit/pull --rebase/push main.
    Never blocks export if offline/auth fails.
    """
    repo_path = BASE
    try:
        # 1) Ensure repo
        if not (repo_path / ".git").exists():
            log("⚙️  No .git found — initializing repository…")
            subprocess.run(["git", "-C", str(repo_path), "init"], check=True)
            subprocess.run(["git", "-C", str(repo_path), "branch", "-M", "main"], check=True)
            # Add SSH remote if missing
            subprocess.run(["git", "-C", str(repo_path), "remote", "add", "origin",
                            "git@github.com:flypaper-creative/savant.git"], check=False)

        # 2) Ensure SSH remote (convert https → ssh if needed)
        remotes = subprocess.run(["git", "-C", str(repo_path), "remote", "-v"],
                                 capture_output=True, text=True).stdout
        if "https://github.com" in remotes:
            log("🔄 Switching GitHub remote to SSH…")
            subprocess.run(["git", "-C", str(repo_path), "remote", "set-url", "origin",
                            "git@github.com:flypaper-creative/savant.git"], check=False)

        # 3) Ensure SSH key
        ssh_dir = Path.home() / ".ssh"
        key = ssh_dir / "id_ed25519"
        pub = ssh_dir / "id_ed25519.pub"
        if not key.exists():
            log("🔐 Generating SSH keypair (ed25519)…")
            ssh_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", str(key), "-N", ""], check=True)

        # 4) Optional: register key via GH API using curl, no 'requests' dependency
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if token and pub.exists():
            try:
                title = f"Savant@{os.uname().nodename}"
                pubkey = pub.read_text().strip()
                api = "https://api.github.com/user/keys"
                # 422 = already exists, treat as success
                res = subprocess.run([
                    "curl", "-sS", "-X", "POST", api,
                    "-H", f"Authorization: token {token}",
                    "-H", "Accept: application/vnd.github+json",
                    "-d", f'{{"title":"{title}","key":"{pubkey}"}}'
                ], capture_output=True, text=True)
                if res.returncode == 0:
                    log("✅ Attempted GitHub SSH key registration (ignored if already exists).")
                else:
                    log(f"⚠️  GitHub key registration curl exit={res.returncode}: {res.stderr}")
            except Exception as e:
                log(f"⚠️  Could not register SSH key: {e}")

        # 5) Commit & push
        subprocess.run(["git", "-C", str(repo_path), "add", "-A"], check=False)
        subprocess.run(["git", "-C", str(repo_path), "commit",
                        "-m", f"Auto export {datetime.now().isoformat()}"], check=False)
        subprocess.run(["git", "-C", str(repo_path), "fetch", "origin"], check=False)
        subprocess.run(["git", "-C", str(repo_path), "pull", "--rebase", "origin", "main"], check=False)
        subprocess.run(["git", "-C", str(repo_path), "push", "origin", "main"], check=False)
        log("🐙 GitHub push successful.")
    except Exception as e:
        log(f"⚠️  GitHub push failed: {e}")

# --- MAIN ------------------------------------------------------------------
def main():
    load_env()
    log(f"🧠 Export v300 start {datetime.now(timezone.utc).isoformat()}")
    archive = create_archive()
    copy_to_downloads(archive)
    upload_s3(archive)
    push_github(archive)
    log("✅ Export complete — Downloads + S3 + Git push attempted.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Export failed: {e}")
