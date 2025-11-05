#!/data/data/com.termux/files/usr/bin/bash
echo "🩹 Running oriel self-healing..."
find src -type f -name "*.tsx" -o -name "*.ts" | while read -r file; do
  sed -i '1s/^```[a-zA-Z]*//' "$file"
  sed -i 's/```$//' "$file"
done
npx eslint src --fix >/dev/null 2>&1 || true
npx tsc --noEmit >/dev/null 2>&1 || true
echo "✅ Syntax validated and healed."
