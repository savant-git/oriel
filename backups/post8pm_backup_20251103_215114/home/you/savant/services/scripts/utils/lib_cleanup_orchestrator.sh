#!/data/data/com.termux/files/usr/bin/bash
echo "🧩 Savant Library Cleanup & Mirror — $(date -Iseconds)"
python3 ~/savant/services/scripts/utils/lib_mirror_s3.py
python3 ~/savant/services/scripts/utils/dependency_snapshot.py
bash ~/savant/services/scripts/utils/full_cleanup.sh
python3 ~/savant/services/scripts/intelligence_cluster/clean_complete.py
echo "✅ Library cleanup and backup cycle complete."
