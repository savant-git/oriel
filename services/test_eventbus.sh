#!/data/data/com.termux/files/usr/bin/bash
cd ~/savant/services || exit 1
echo "🧠 Re-verifying Savant Event Bus..."

# Restart cleanly
pkill -f "dashboard_openapi" 2>/dev/null || true
pkill -f "inference_broker" 2>/dev/null || true
nohup python3 federation/inference_broker.py > ~/savant/logs/inference_broker.log 2>&1 &
nohup python3 web/dashboard/dashboard_openapi.py > ~/savant/logs/dashboard_openapi.out 2>&1 &
sleep 5

# Verify endpoints
echo "🔍  Checking /api/events endpoints..."
curl -s http://127.0.0.1:7070/api/events/recent | head -n 10
curl -s -X POST "http://127.0.0.1:7070/api/events/subscribe?type=test_event"
python3 - <<'PY'
from savant.services.event_bus.event_bus_core import publish
publish("diagnostic","event_bus_live")
print("✅ Event Bus test event published.")
PY
