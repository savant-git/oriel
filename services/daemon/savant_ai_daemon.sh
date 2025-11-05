#!/data/data/com.termux/files/usr/bin/bash
LOG=~/savant/logs/ai_gateway_daemon.out
APP=~/savant/services/scripts/ai_core/openai_gateway.py
echo "[`date -u`] Launching Savant AI Gateway…" >> "$LOG"
while true; do
  python3 "$APP" >> "$LOG" 2>&1
  echo "[`date -u`] Gateway crashed; restarting after 10 s…" >> "$LOG"
  sleep 10
done
