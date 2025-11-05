#!/data/data/com.termux/files/usr/bin/bash
LOG=~/savant/logs/quality_audit.out
while true; do
  python3 ~/savant/services/utils/personality_quality_bridge.py >> "$LOG" 2>&1
  sleep 3600
done
