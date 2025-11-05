#!/bin/bash
# small helper that writes any base64 payload to a target path
read -r TARGET
read -r PAYLOAD
echo "$PAYLOAD" | base64 -d > "$TARGET"
chmod +x "$TARGET"
