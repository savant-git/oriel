#!/data/data/com.termux/files/usr/bin/bash
echo "🚀 Starting Savant Server Daemon..."
nohup python3 ~/savant/services/scripts/server_daemon/server_daemon.py > ~/savant/logs/server_daemon.out 2>&1 &
echo "✅ Savant Server Daemon running in background."
