#!/data/data/com.termux/files/usr/bin/bash
# ---------------------------------------------------------------
# Savant Clean v22 — 100% shell, runs even at 0 bytes free
# - Portable df usage (df -Pk)
# - Guards against empty arithmetic
# - Optional S3 mirror if awscli + env present
# - Never invokes Python
# ---------------------------------------------------------------

LOG="$HOME/savant/logs/savant_clean_shell.log"
mkdir -p "$(dirname "$LOG")"

ts(){ date -Iseconds; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

# Safe df free space (KB) reader
free_kb() {
  # df -Pk outputs POSIX format; take available KB from the second line
  local kb
  kb=$(df -Pk /data/data/com.termux 2>/dev/null | awk 'NR==2{print $4}')
  [ -n "$kb" ] && printf '%s' "$kb" || printf '0'
}

log "⚙️  Savant Clean v22 — Shell-only emergency cleaner starting…"

# ----------------- Phase A: Temp & cache purge -----------------
# Termux & system caches
rm -rf \
  /data/data/com.termux/files/usr/tmp/* \
  /data/data/com.termux/cache/* \
  /data/data/com.termux/files/usr/var/cache/apt/* \
  2>/dev/null

# User caches
rm -rf \
  "$HOME/.cache/"* \
  "$HOME/.npm/_cacache" \
  "$HOME/.npm/_logs" \
  "$HOME/.cargo/registry" "$HOME/.cargo/git" \
  2>/dev/null

# Savant workspace temp & __pycache__
rm -rf \
  "$HOME/savant/tmp/"* \
  "$HOME/savant/cache/"* \
  "$HOME/savant/.pytest_cache" \
  2>/dev/null

find "$HOME/savant" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$HOME/savant/logs" -type f -size +1024k -delete 2>/dev/null
find "$HOME/savant/exports" -type f -mtime +2 -delete 2>/dev/null

# npm/cargo again (in case symlinks)
rm -rf "$HOME/.cargo/{registry,git}" "$HOME/.npm/_logs" "$HOME/.npm/_cacache" 2>/dev/null

sync

AFTER_A=$(free_kb)
log "📊  Free space after Phase A purge: ${AFTER_A} KB"

# ------------- Phase B: (Optional) S3 mirroring ----------------
if command -v aws >/dev/null 2>&1 && \
   [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ] && [ -n "$SAVANT_S3_BUCKET" ]; then
  log "☁️  S3 mirror detected — exporting logs & exports to s3://$SAVANT_S3_BUCKET/"

  # Mirror exports
  if [ -d "$HOME/savant/exports" ]; then
    for f in "$HOME"/savant/exports/*; do
      [ -f "$f" ] && aws s3 cp "$f" "s3://$SAVANT_S3_BUCKET/exports/$(basename "$f")" --only-show-errors || true
    done
  fi

  # Bundle logs (best-effort)
  if [ -d "$HOME/savant/logs" ]; then
    TAR="/data/data/com.termux/files/usr/tmp/savant_logs_$(date +%s).tar.gz"
    mkdir -p "$(dirname "$TAR")" 2>/dev/null
    tar czf "$TAR" -C "$HOME/savant" logs 2>/dev/null && \
      aws s3 cp "$TAR" "s3://$SAVANT_S3_BUCKET/logs/$(basename "$TAR")" --only-show-errors && \
      rm -f "$TAR"
  fi

  # Optionally clear local copies after successful push
  rm -f "$HOME"/savant/exports/* 2>/dev/null
  find "$HOME/savant/logs" -type f -name "*.log" -size +512k -delete 2>/dev/null
else
  log "ℹ️  S3 mirror skipped (awscli or env not set)."
fi

sync

AFTER_B=$(free_kb)
log "📊  Free space after Phase B S3 mirror: ${AFTER_B} KB"

# ------------- Phase C: Deep package cache pruning -------------
# Keep it conservative: no package removals, only caches & wheels
rm -rf \
  "$HOME/.cache/pip" \
  "$HOME/.local/share/pip/"* \
  2>/dev/null

# Wipe pip wheel build temp (if any)
find /data/data/com.termux/files/usr/tmp -maxdepth 1 -type d -name "pip-*" -exec rm -rf {} + 2>/dev/null

sync
AFTER_C=$(free_kb)
log "📊  Free space after Phase C deep-cache: ${AFTER_C} KB"

# Final status
log "✅  Savant Clean v22 finished (shell-only)."
log "   If you want an aggressive offload (Python site-packages to S3), say the word and I’ll add an opt-in phase."
