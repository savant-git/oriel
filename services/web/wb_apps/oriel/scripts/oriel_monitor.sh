#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🧠  oriel Monitor Daemon Started..."
WATCH_DIR="src"
SLEEP_INTERVAL=5

hash_last=""

# --- helpers ---------------------------------------------------------------
snapshot() {
  TS=$(date +"%Y%m%d_%H%M%S")
  SNAP="snapshots/auto_${TS}"
  mkdir -p "$SNAP"
  cp -r src "$SNAP/src" 2>/dev/null || true
  cp -r scripts "$SNAP/scripts" 2>/dev/null || true
  cp package.json vite.config.* tsconfig.* "$SNAP" 2>/dev/null || true
  echo "📦 Snapshot created → $SNAP"
}

heal() {
  echo "🩹  Self-healing syntax..."
  find src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
    -exec sed -i '1{/^```/d}' {} \; -exec sed -i 's/```.*//g' {} \;
  if npx tsc --noEmit --skipLibCheck > /dev/null 2>&1; then
    echo "✅  TypeScript verified"
  else
    echo "⚠️  TypeScript errors detected – see logs/ts_last.log"
    npx tsc --noEmit --skipLibCheck > logs/ts_last.log 2>&1 || true
  fi
}

optimize_ai() {
  echo "🤖  Optional AI optimization step..."
  if [ -x scripts/gemini-assist.mjs ]; then
    node scripts/gemini-assist.mjs audit "$1" "Context-aware audit & optimize for clarity, performance, maintainability, and design consistency. Maintain valid TypeScript."
  fi
}

# --- watcher loop ----------------------------------------------------------
while true; do
  new_hash=$(find "$WATCH_DIR" -type f -printf "%T@ %p\n" | md5sum | cut -d' ' -f1)

  if [ "$new_hash" != "$hash_last" ]; then
    echo "🔄  Change detected $(date +"%H:%M:%S")"
    snapshot
    heal

    # AI optimization can be heavy – only trigger on idle interval
    optimize_ai "src" &
    hash_last="$new_hash"
  fi

  sleep "$SLEEP_INTERVAL"
done
