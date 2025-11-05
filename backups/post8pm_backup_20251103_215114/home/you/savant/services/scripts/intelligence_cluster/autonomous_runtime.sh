#!/data/data/com.termux/files/usr/bin/bash
LOG=~/savant/logs/autonomous_runtime.log
echo "🚀 SAVANT AUTONOMOUS RUNTIME — $(date -Iseconds)" | tee -a "$LOG"

# --- Run core learning cycle ---
python3 ~/savant/services/scripts/intelligence_cluster/autonomous_knowledge_cluster.py >> "$LOG" 2>&1

# --- Enhancement & synthesis ---
python3 ~/savant/services/scripts/intelligence_cluster/intelligence_loop.py >> "$LOG" 2>&1

# --- Export + cloud sync ---
python3 ~/savant/services/scripts/intelligence_cluster/export_cluster_v5_1.py >> "$LOG" 2>&1
python3 ~/savant/services/scripts/cloud_engine/cloud_uplink.py ~/savant/exports >> "$LOG" 2>&1

# --- GitHub push (safe mode) ---
python3 ~/savant/services/scripts/intelligence_cluster/github_force_push.py >> "$LOG" 2>&1

# --- Schedule next run ---
echo "⏳ Cycle complete — next check in 1 hour." | tee -a "$LOG"
sleep 3600
exec "$0"
