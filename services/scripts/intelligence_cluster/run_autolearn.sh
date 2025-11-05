#!/data/data/com.termux/files/usr/bin/bash
echo "🧩 Running Savant Autonomous Knowledge Cluster — $(date -Iseconds)"
python3 "$HOME/savant/services/scripts/intelligence_cluster/autonomous_knowledge_cluster.py"
python3 "$HOME/savant/services/scripts/intelligence_cluster/cloud_uplink.py" || true
