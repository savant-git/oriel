#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# oriel Watchdog — Self-Healing Dev Loop + Auto-Optimizer
# ==========================================================
set -e

ROOT="$(pwd)"
LOG="$ROOT/oriel_watchdog.log"
touch "$LOG"

echo "🚀 oriel Watchdog starting at $(date)" >> "$LOG"

# --- 1️⃣ Ensure package.json is valid JSON -----------------
if ! jq empty package.json 2>/dev/null; then
  echo "⚠️  package.json invalid — attempting auto-repair" | tee -a "$LOG"
  sed -i 's/```json//g;s/```//g' package.json
  jq empty package.json || {
    echo "❌ package.json unrecoverable. Regenerating minimal valid file." | tee -a "$LOG"
    cat > package.json <<JSON
{
  "name": "oriel",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite --host",
    "build": "vite build",
    "start": "vite"
  },
  "dependencies": {},
  "devDependencies": {}
}
JSON
  }
fi

# --- 2️⃣ Verify node_modules / reinstall if missing ---------
if [ ! -d node_modules ]; then
  echo "📦 Installing missing dependencies..." | tee -a "$LOG"
  npm install --legacy-peer-deps --force >>"$LOG" 2>&1 || npm rebuild >>"$LOG" 2>&1
fi

# --- 3️⃣ Run ESLint + TypeScript validation ----------------
if [ -f ./node_modules/.bin/eslint ]; then
  echo "🔍 Linting and fixing issues..." | tee -a "$LOG"
  npx eslint src --ext .ts,.tsx,.js,.jsx --fix || true
fi
if [ -f tsconfig.json ]; then
  echo "🧩 Type-checking project..." | tee -a "$LOG"
  npx tsc --noEmit || true
fi

# --- 4️⃣ Self-heal missing imports / syntax issues ----------
echo "🧠 Healing import and syntax issues..." | tee -a "$LOG"
grep -rl "import " src | while read -r f; do
  sed -i 's/;;/;/g;s/,,/,/g' "$f"
done

# --- 5️⃣ Run Gemini optimization if available ---------------
if [ -f scripts/gemini-assist.mjs ]; then
  echo "🤖 Running Gemini 2.5 Pro context optimizer..." | tee -a "$LOG"
  bash scripts/optimize_oriel.sh || echo "⚠️ Gemini optimizer skipped." >>"$LOG"
fi

# --- 6️⃣ Continuous monitoring loop ------------------------
echo "🔁 Entering continuous monitoring loop..." | tee -a "$LOG"
while true; do
  echo "🧩 Verifying environment..." >>"$LOG"
  jq empty package.json 2>/dev/null || {
    echo "⚠️ Repairing package.json..." >>"$LOG"
    sed -i 's/```json//g;s/```//g' package.json
  }
  if ! pgrep -f "vite --host" >/dev/null; then
    echo "💡 Dev server not running — restarting..." >>"$LOG"
    npm run dev -- --host >>"$LOG" 2>&1 &
    sleep 10
  fi
  sleep 30
done
