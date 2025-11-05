#!/data/data/com.termux/files/usr/bin/bash
for f in index.html src/ui/App.tsx; do
  if [ -f "$f" ] && head -1 "$f" | grep -q '```'; then
    echo "🩹 Removing stray markdown fence from $f..."
    sed -i '1{/^```/d;}' "$f"
  fi
done
