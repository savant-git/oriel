#!/data/data/com.termux/files/usr/bin/bash
# --------------------------------------------------------------
# SAVANT DASHBOARD DAEMON v1.0
# --------------------------------------------------------------
cd ~/savant/services/web/dev_ui || exit 1
export NODE_ENV=production
export PORT=3030
LOG=~/savant/logs/dashboard_daemon.out

# Self-healing restart if crash
while true; do
  echo "🔁 [$(date -u)] Restarting Savant Dashboard..." >> "$LOG"
  npm run build >> "$LOG" 2>&1
  npm run start >> "$LOG" 2>&1
  echo "⚠️ [$(date -u)] Dashboard crashed — restarting in 10s" >> "$LOG"
  sleep 10
done
