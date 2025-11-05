#!/data/data/com.termux/files/usr/bin/bash
echo "🧠 Launching oriel Daemon (auto-optimize mode)..."
while true; do
  inotifywait -r -e modify,create,delete src >/dev/null 2>&1
  echo "♻️ Change detected, running 10× optimization..."
  bash scripts/self_heal.sh
  node scripts/context_map.mjs
  node scripts/iterate_oriel.mjs "Auto-optimization"
done

# =============================================================
# 🧩 EXTENDED DAEMON FUNCTIONALITY (APPENDED NON-DESTRUCTIVE)
# =============================================================

LOG_APPEND="logs/daemon_extended.log"
CPU_LIMIT=75     # Safe threshold
INTERVAL=300     # Run every 5 min
BATCH_DELAY=120  # Delay after file changes (seconds)
LOAD_FILE="/proc/loadavg"

# Helper: CPU usage gatekeeper
check_cpu_load() {
  if [ -f "$LOAD_FILE" ]; then
    local load
    load=$(awk '{print $1*100}' "$LOAD_FILE" | cut -d. -f1)
    if [ "$load" -gt "$CPU_LIMIT" ]; then
      echo "⚠️  High CPU ($load%) — delaying cycle." | tee -a "$LOG_APPEND"
      return 1
    fi
  fi
  return 0
}

# Helper: Batching changes to avoid redundant cycles
batch_detect_changes() {
  echo "📦 Watching for code changes..." | tee -a "$LOG_APPEND"
  inotifywait -r -e modify,create,delete src >/dev/null 2>&1
  echo "🕐 Change detected — batching for ${BATCH_DELAY}s..." | tee -a "$LOG_APPEND"
  sleep "$BATCH_DELAY"
}

# Enhanced optimization cycle
extended_optimize_cycle() {
  echo "🚀 Running extended optimization @ $(date)" | tee -a "$LOG_APPEND"

  # Run preflight if it exists
  [ -f scripts/self_heal.sh ] && bash scripts/self_heal.sh >>"$LOG_APPEND" 2>&1

  # Run contextual mapping if present
  [ -f scripts/context_map.mjs ] && node scripts/context_map.mjs >>"$LOG_APPEND" 2>&1

  # Run primary iteration script
  [ -f scripts/iterate_oriel.mjs ] && node scripts/iterate_oriel.mjs "Scheduled optimization" >>"$LOG_APPEND" 2>&1

  # Optional reporting after iteration
  [ -f scripts/report_summary.mjs ] && node scripts/report_summary.mjs >>"$LOG_APPEND" 2>&1

  echo "✅ Extended optimization complete." | tee -a "$LOG_APPEND"
  echo "─────────────────────────────────────────────" | tee -a "$LOG_APPEND"
}

# Main extended loop (runs in parallel with existing logic)
(
  while true; do
    batch_detect_changes
    if check_cpu_load; then
      extended_optimize_cycle
    else
      echo "⏸  Skipping cycle due to high load @ $(date)" | tee -a "$LOG_APPEND"
    fi
    sleep "$INTERVAL"
  done
) &


# =============================================================
# 🧩 ENHANCED oriel DAEMON EXTENSION (non-destructive)
# =============================================================

LOG_EXT="logs/daemon_enhanced.log"
CPU_LIMIT=75       # Max CPU before delaying cycle
INTERVAL=300       # 5 minutes between scheduled runs
BATCH_DELAY=120    # Delay after detecting file changes
LOAD_FILE="/proc/loadavg"

check_cpu_load() {
  if [ -f "$LOAD_FILE" ]; then
    local load
    load=$(awk '{print $1*100}' "$LOAD_FILE" | cut -d. -f1)
    if [ "$load" -gt "$CPU_LIMIT" ]; then
      echo "⚠️ CPU load ${load}% > ${CPU_LIMIT}%. Pausing cycle." | tee -a "$LOG_EXT"
      return 1
    fi
  fi
  return 0
}

batch_file_changes() {
  echo "📦 Watching src/ for updates..." | tee -a "$LOG_EXT"
  inotifywait -r -e modify,create,delete src >/dev/null 2>&1
  echo "🕐 Change detected — batching for ${BATCH_DELAY}s..." | tee -a "$LOG_EXT"
  sleep "$BATCH_DELAY"
}

run_full_cycle() {
  echo "🚀 Starting optimization cycle @ $(date)" | tee -a "$LOG_EXT"

  [ -f scripts/self_heal.sh ] && bash scripts/self_heal.sh >>"$LOG_EXT" 2>&1
  [ -f scripts/context_map.mjs ] && node scripts/context_map.mjs >>"$LOG_EXT" 2>&1
  [ -f scripts/iterate_oriel.mjs ] && node scripts/iterate_oriel.mjs "Timed optimization" >>"$LOG_EXT" 2>&1
  [ -f scripts/report_summary.mjs ] && node scripts/report_summary.mjs >>"$LOG_EXT" 2>&1

  echo "✅ Cycle complete @ $(date)" | tee -a "$LOG_EXT"
  echo "─────────────────────────────────────────────" | tee -a "$LOG_EXT"
}

while true; do
  batch_file_changes
  if check_cpu_load; then
    run_full_cycle
  else
    echo "⏸ Skipping cycle due to high load." | tee -a "$LOG_EXT"
  fi
  sleep "$INTERVAL"
done &
