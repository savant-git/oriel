#!/bin/bash
VM_USER="you"
VM_HOST="34.58.138.20"
SSH_KEY="$HOME/.ssh/id_ed25519"

echo "=============================================================="
echo "🧠 Savant VM Connect v110"
echo "=============================================================="
echo "🌐 Connecting to ${VM_USER}@${VM_HOST}..."
echo "🔑 Using key: $SSH_KEY"
echo "---------------------------------------------------------------"
ssh -i "$SSH_KEY" "${VM_USER}@${VM_HOST}"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "🏁 VM session closed normally."
else
  echo "❌ SSH exited with code $EXIT_CODE."
fi
