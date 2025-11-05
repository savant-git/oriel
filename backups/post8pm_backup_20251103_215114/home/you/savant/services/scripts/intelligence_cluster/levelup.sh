#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
echo "🧠 Savant Level-Up Pipeline — $(date -Iseconds)"
python3 "$HOME/savant/services/scripts/intelligence_cluster/curriculum_seeder.py" || true
python3 "$HOME/savant/services/scripts/intelligence_cluster/knowledge_synthesis_cluster.py" || true
python3 "$HOME/savant/services/scripts/intelligence_cluster/cloud_uplink.py" || true
echo "📊 Status:"
if [ -f "$HOME/savant/knowledge/meta/synthesis_summary.json" ]; then
  cat "$HOME/savant/knowledge/meta/synthesis_summary.json"
else
  echo '{"level":0,"note":"No synthesis summary yet."}'
fi
