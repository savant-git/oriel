from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
⬢ Termux-to-S3 Overlay v1.0
Redirects heavy Termux temp/build dirs to S3 mirrors.
"""
import os, shutil, tarfile, boto3, time
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MIRROR = HOME/"savant/mirrors"
LOG = HOME/"savant/logs/t2s3_overlay.log"
BUCKET = os.getenv("SAVANT_S3_BUCKET")
REGION = os.getenv("AWS_DEFAULT_REGION","us-east-1")

PATHS = [
    HOME/".cache",
    HOME/".cargo",
    HOME/".rustup",
    Path("/data/data/com.termux/files/usr/tmp"),
    Path("/data/data/com.termux/files/usr/var/cache/apt/archives")
]

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    console.print(f"[{ts}] {msg}")
    try:
        with LOG.open("a") as f: f.write(f"[{ts}] {msg}\n")
    except Exception: pass

def ensure_mirror(p: Path):
    m = MIRROR/p.name
    if not m.exists():
        m.mkdir(parents=True, exist_ok=True)
    if p.exists() and not p.is_symlink():
        log(f"→ Moving {p} → {m}")
        shutil.move(str(p), str(m))
    if not p.exists():
        p.symlink_to(m)
        log(f"🔗 Linked {p} → {m}")

def compress_and_upload(p: Path):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive = MIRROR/f"{p.name}_{ts}.tar.zst"
    try:
        import zstandard as zstd
        log(f"🧩 Compressing {p.name}")
        c = zstd.ZstdCompressor(level=9)
        with tarfile.open(archive.with_suffix(".tar"), "w") as tar:
            tar.add(str(p), arcname=p.name)
        with open(archive.with_suffix(".tar"),"rb") as f_in, open(archive,"wb") as f_out:
            f_out.write(c.compress(f_in.read()))
        os.remove(archive.with_suffix(".tar"))
        log(f"☁️ Uploading {archive.name}")
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=REGION)
        s3.upload_file(str(archive), BUCKET, f"termux_overlay/{archive.name}")
        log(f"✅ Uploaded {archive.name}")
    except Exception as e:
        log(f"⚠️ Upload failed for {p.name}: {e}")

def main():
    MIRROR.mkdir(parents=True, exist_ok=True)
    for p in PATHS: ensure_mirror(p)
    for p in PATHS:
        try: compress_and_upload(MIRROR/p.name)
        except Exception as e: log(f"⚠️ Skip {p.name}: {e}")
    log("✅ T2S3 cycle complete.")

if __name__=="__main__":
    main()
