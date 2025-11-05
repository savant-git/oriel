#!/data/data/com.termux/files/usr/bin/bash
echo "⚙️  Savant Unified Clean Cycle — $(date -Iseconds)"

BASE="$HOME/savant"
LOG="$BASE/logs/savant_clean.log"
mkdir -p "$BASE/logs"

# --- Load environment (.env) ------------------------------------
if [ -f "$BASE/.env" ]; then
  set -o allexport; source "$BASE/.env"; set +o allexport
else
  echo "⚠️  No .env file found — skipping key exports" | tee -a "$LOG"
fi

# ================================================================
# 1. RUN INTELLIGENCE CLUSTER CLEANING / COMPLETION
# ================================================================
CLEAN_SCRIPT="$BASE/services/scripts/intelligence_cluster/clean_complete.py"
if [ -f "$CLEAN_SCRIPT" ]; then
  echo "🧠 Running clean_complete.py first..." | tee -a "$LOG"
  python3 "$CLEAN_SCRIPT" >> "$LOG" 2>&1 || echo "⚠️  clean_complete.py encountered errors" | tee -a "$LOG"
else
  echo "⚠️  clean_complete.py missing — skipping intelligence scan" | tee -a "$LOG"
fi

# ================================================================
# 2. CLOUD OFFLOAD LARGE FILES
# ================================================================
echo "☁️  Uploading large (>25 MB) files to S3 before purge..." | tee -a "$LOG"
find "$BASE" -type f -size +25M ! -path "*/.git/*" ! -name "*.env" | while read -r file; do
  rel="${file#$HOME/}"
  key="offload/${rel//\//_}"
  python3 - "$file" "$SAVANT_S3_BUCKET" "$key" <<'PY'
import sys,boto3,os
from pathlib import Path
file,bucket,key=sys.argv[1:4]
if not bucket: sys.exit(0)
try:
    s3=boto3.client("s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    s3.upload_file(file,bucket,key)
    print(f"✅ Uploaded {file} → s3://{bucket}/{key}")
    Path(file).unlink()
except Exception as e:
    print(f"⚠️  Upload failed for {file}: {e}")
PY
done

# ================================================================
# 3. COMPRESS LOGS + OLD EXPORTS
# ================================================================
echo "🗜️  Compressing old logs/exports..." | tee -a "$LOG"
find "$BASE/logs" -type f -mtime +3 -exec gzip -9 {} \; 2>/dev/null
find "$BASE/exports" -type f -mtime +5 -exec gzip -9 {} \; 2>/dev/null
find "$BASE/exports" -type f -mtime +15 -delete 2>/dev/null

# ================================================================
# 4. REMOVE BUILD, CACHE, NODE & PYTHON TEMP FILES
# ================================================================
echo "🧹  Removing caches, build dirs, and temp files..." | tee -a "$LOG"
rm -rf "$BASE"/**/__pycache__ "$BASE"/**/*.pyc "$BASE"/**/*.pyo 2>/dev/null
rm -rf "$BASE/tmp" "$BASE/cache" "$BASE/.pytest_cache" "$BASE/.mypy_cache" 2>/dev/null
rm -rf "$HOME/.cache/pip" "$HOME/.npm" "$HOME/.gradle" "$HOME/.android" 2>/dev/null
find "$BASE/services/web" -type d \( -name "node_modules" -o -name "dist" -o -name "build" \) -exec rm -rf {} + 2>/dev/null

# ================================================================
# 5. CLEAR TERMUX & SYSTEM CACHES
# ================================================================
echo "🧽  Clearing Termux package caches..." | tee -a "$LOG"
pkg clean -y 2>/dev/null || true
apt autoremove -y 2>/dev/null || true
apt clean -y 2>/dev/null || true
rm -rf /data/data/com.termux/files/usr/tmp/* /data/data/com.termux/cache/* 2>/dev/null

# ================================================================
# 6. REMOVE SWAPFILE IF EXISTS
# ================================================================
if [ -f "$HOME/swapfile" ]; then
  echo "💾  Removing swapfile..." | tee -a "$LOG"
  swapoff "$HOME/swapfile" 2>/dev/null || true
  rm -f "$HOME/swapfile"
fi

# ================================================================
# 7. FINAL FREE SPACE REPORT
# ================================================================
echo "📊  Disk space after cleanup:" | tee -a "$LOG"
df -h "$HOME" | tee -a "$LOG"

echo "✅ Savant Clean Complete — $(date -Iseconds)" | tee -a "$LOG"
