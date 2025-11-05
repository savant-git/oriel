#!/data/data/com.termux/files/usr/bin/bash
# =========================================
# oriel supervisor — keeps daemon + reports alive safely
# =========================================

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "🪄 launching oriel supervisor..."
echo "logs in $LOG_DIR/oriel_daemon.log and $LOG_DIR/oriel_report.log"

# start daemon in background with nohup so it survives shell exits
nohup npm run daemon >"$LOG_DIR/oriel_daemon.log" 2>&1 &

# separate infinite loop for reports every 5 minutes
(
  while true; do
    echo "🧾 running report at $(date)" >>"$LOG_DIR/oriel_report.log"
    npm run report >>"$LOG_DIR/oriel_report.log" 2>&1
    sleep 300
  done
) &

# keep supervisor alive and monitor background processes
while true; do
  sleep 60
  pgrep -f "npm run daemon" >/dev/null || {
    echo "⚠️ daemon stopped — restarting..." >>"$LOG_DIR/oriel_supervisor.log"
    nohup npm run daemon >>"$LOG_DIR/oriel_daemon.log" 2>&1 &
  }
done
