#!/data/data/com.termux/files/usr/bin/bash
cd ~/savant/services/web/dashboard || exit 1
python3 - <<'PY'
from savant.services.ai_core.trust_consensus import compute_trust
from savant.services.web.dashboard.federation_ui.graph_visualizer import snapshot
print("Trust:", compute_trust())
print("Graph snapshot:", snapshot())
PY
