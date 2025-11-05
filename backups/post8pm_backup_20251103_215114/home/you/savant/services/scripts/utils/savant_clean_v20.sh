#!/data/data/com.termux/files/usr/bin/bash
LOG=~/savant/logs/savant_clean_shell.log
mkdir -p "$(dirname "$LOG")"
ts() { date -Iseconds; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

log "⚙️  Phase-0: Shell-only emergency cleaner (runs even at 0 bytes)…"

# --- Global caches ---
rm -rf /data/data/com.termux/files/usr/tmp/* \
       /data/data/com.termux/cache/* \
       /data/data/com.termux/files/usr/var/cache/apt/* \
       ~/.cache/* ~/.npm/_cacache ~/.cargo/{registry,git} 2>/dev/null

# --- Python build artefacts and heavy libs ---
for d in pip setuptools wheel numpy pandas matplotlib requests \
         langchain flask boto3 zstandard termcolor chromadb faiss; do
  rm -rf "/data/data/com.termux/files/usr/lib/python3.12/site-packages/${d}"* 2>/dev/null
done
find /data/data/com.termux/files/usr/lib/python3.12/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# --- Savant workspace data ---
rm -rf ~/savant/tmp/* ~/savant/cache/* ~/savant/.pytest_cache \
       ~/savant/__pycache__ ~/savant/services/**/__pycache__ 2>/dev/null
find ~/savant/logs -type f -size +1M -delete 2>/dev/null
find ~/savant/exports -type f -mtime +2 -delete 2>/dev/null

# --- npm / cargo junk ---
rm -rf ~/.cargo/{registry,git} ~/.npm/_logs ~/.npm/_cacache 2>/dev/null

# --- sync and report ---
sync
FREE=$(df -Pm /data/data/com.termux | awk 'NR==2{print $4}')
log "📊  Free space after shell purge: ${FREE} KB"

# --- Optional S3 offload (pure AWS CLI) ---
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$SAVANT_S3_BUCKET" ] && [ "$FREE" -lt 300000 ]; then
  log "☁️  Uploading residual exports to S3 (low-space mirror)…"
  for f in ~/savant/exports/*; do
    [ -f "$f" ] && aws s3 cp "$f" "s3://$SAVANT_S3_BUCKET/exports/$(basename "$f")" --only-show-errors
  done
  rm -f ~/savant/exports/* 2>/dev/null
fi

# --- Verify threshold before invoking Python orchestrator ---
if [ "$FREE" -lt 200000 ]; then
  log "⚠️  Still <200 MB free — running secondary purge of tests & wheels…"
  find /data/data/com.termux/files/usr/lib/python3.12/site-packages -name "*test*" -type d -exec rm -rf {} + 2>/dev/null
  sync
  FREE=$(df -Pm /data/data/com.termux | awk 'NR==2{print $4}')
  log "📊  Free space now ${FREE} KB"
fi

if [ "$FREE" -ge 200000 ]; then
  log "✅  Launching Phase-2 Python orchestrator (savant_clean_v18.py)…"
  /data/data/com.termux/files/usr/bin/python3 ~/savant/services/scripts/utils/savant_clean_v18.py || log "⚠️  Python cleanup failed but shell stage succeeded."
else
  log "❌  Disk critically full; Python stage skipped."
fi
log "🏁  Savant Clean v20 complete."
