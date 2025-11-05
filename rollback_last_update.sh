#!/bin/bash
echo "🕓 Rolling back to previous Savant state..."
LATEST=$(ls -dt ~/savant/backups/post8pm_backup_* | head -1)
if [ -d "$LATEST" ]; then
  cp -r "$LATEST"/* ~/savant/
  echo "✅ Restored from backup: $LATEST"
else
  echo "⚠️ No backup found."
fi
