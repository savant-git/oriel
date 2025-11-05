#!/data/data/com.termux/files/usr/bin/bash
echo "⚙️  Savant Environment Reset — $(date -Iseconds)"
echo "🔻 Killing orphaned Python processes..."
ps -ef | grep 'savant/services/scripts' | grep python3 | awk '{print $2}' | xargs kill -9 2>/dev/null
echo "🧹 Cleaning temp and cache directories..."
rm -rf ~/savant/__pycache__ ~/savant/tmp ~/savant/cache ~/savant/services/**/__pycache__
echo "💾 Releasing sockets..."
sleep 5
echo "✅ Environment reset complete. You can now restart with: savant-gateway"
