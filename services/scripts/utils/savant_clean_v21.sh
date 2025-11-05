#!/data/data/com.termux/files/usr/bin/bash
LOG=~/savant/logs/savant_clean_shell.log
mkdir -p "$(dirname "$LOG")"
ts() { date -Iseconds; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

log "⚙️  Phase-0: Bare-metal full cleanup (pure shell, OOM-safe)…"

# --- Core temp & cache paths ---
rm -rf /data/data/com.termux/files/usr/tmp/* \
       /data/data/com.termux/cache/* \
       /data/data/com.termux/files/usr/var/cache/apt/* \
       ~/.cache/* ~/.npm/_cacache ~/.cargo/{registry,git} 2>/dev/null

# --- Heavy Python packages (safe to rebuild) ---
for d in pip setuptools wheel numpy pandas matplotlib requests \
         flask boto3 langchain zstandard faiss chromadb termcolor; do
  rm -rf "/data/data/com.termux/files/usr/lib/python3.12/site-packages/${d}"* 2>/dev/null
done
find /data/data/com.termux/files/usr/lib/python3.12/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# --- Savant workspace ---
rm -rf ~/savant/tmp/* ~/savant/cache/* ~/savant/.pytest_cache \
       ~/savant/__pycache__ ~/savant/services/**/__pycache__ 2>/dev/null
find ~/savant/logs -type f -size +1024k -delete 2>/dev/null
find ~/savant/exports -type f -mtime +2 -delete 2>/dev/null

# --- npm / cargo ---
rm -rf ~/.cargo/{registry,git} ~/.npm/_logs ~/.npm/_cacache 2>/dev/null

# --- Report space ---
sync
FREE=$(df -Pk /data/data/com.termux | awk 'NR==2{print $4}')
log "📊  Free space after purge: ${FREE:-0} KB"

# --- Optional S3 offload using awscli if present ---
if command -v aws >/dev/null 2>&1 && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$SAVANT_S3_BUCKET" ]; then
  log "☁️  S3 mirror active — uploading exports and logs…"
  for f in ~/savant/exports/*; do
    [ -f "$f" ] && aws s3 cp "$f" "s3://$SAVANT_S3_BUCKET/exports/$(basename "$f")" --only-show-errors
  done
  tar czf /tmp/savant_logs.tar.gz -C ~/savant logs 2>/dev/null && \
    aws s3 cp /tmp/savant_logs.tar.gz "s3://$SAVANT_S3_BUCKET/logs/savant_logs_$(date +%s).tar.gz" --only-show-errors
  rm -f ~/savant/exports/* ~/savant/logs/* /tmp/savant_logs.tar.gz 2>/dev/null
fi

sync
FREE=$(df -Pk /data/data/com.termux | awk 'NR==2{print $4}')
log "📊  Final free space: ${FREE:-0} KB"
log "✅  Savant Clean v21 finished (no Python phase executed)."
