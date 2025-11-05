#!/data/data/com.termux/files/usr/bin/bash
echo "🧩 Savant Clean Orchestrator v5.0 — $(date -Iseconds)"
python3 ~/savant/services/scripts/utils/lib_mirror_s3.py
python3 ~/savant/services/scripts/utils/dependency_snapshot.py
bash ~/savant/services/scripts/utils/full_cleanup.sh 2>/dev/null || true
python3 ~/savant/services/scripts/intelligence_cluster/clean_complete.py
python3 ~/savant/services/scripts/utils/disk_monitor.py
echo "✅ Savant cleanup orchestration complete — logs in ~/savant/logs/"
