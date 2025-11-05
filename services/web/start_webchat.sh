#!/bin/bash
# ==============================================================
# 💬 Savant Web Chat Launcher
# --------------------------------------------------------------
# Activates virtual environment and runs Savant Web Interface
# ==============================================================

# Define environment
SAVANT_BASE=~/savant
VENV="$SAVANT_BASE/venv"
APP="$SAVANT_BASE/services/web/savant_web_v10.py"

# Display header
echo "=============================================================="
echo "💬 Launching Savant Web Chat (FastAPI)"
echo "📦 Environment: $VENV"
echo "📂 App: $APP"
echo "=============================================================="

# Activate venv
if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
    echo "✅ Virtual environment activated."
else
    echo "⚠️  Virtual environment not found — creating now..."
    python3 -m venv "$VENV"
    source "$VENV/bin/activate"
    pip install --upgrade pip
    pip install fastapi uvicorn openai rich python-dotenv
fi

# Launch web chat
cd "$SAVANT_BASE"
python3 "$APP"

# After exit
deactivate
echo "🧠 Savant Web Chat closed. Virtual environment deactivated."
