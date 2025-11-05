#!/data/data/com.termux/files/usr/bin/bash
UI_PATH=~/savant/services/web/wb_ui
BACKUP_PATH=~/savant/backups/wb_ui_backup
LOG_PATH=~/savant/logs/ui_protection.log
while true; do
  if [ ! -d "$UI_PATH" ]; then
    echo "$(date -u) [ALERT] wb_ui missing — auto-restore triggered." >> "$LOG_PATH"
    cp -r "$BACKUP_PATH" "$UI_PATH" 2>/dev/null || mkdir -p "$UI_PATH"
    chmod -R a-w "$UI_PATH"
  fi
  sleep 30
done
