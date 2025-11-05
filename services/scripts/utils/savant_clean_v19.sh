#!/data/data/com.termux/files/usr/bin/bash
echo "⚙️  Phase-0: Bare-metal pre-flight cleanup…"

# ---- Lightweight purge (no Python) ----
rm -rf /data/data/com.termux/files/usr/tmp/* \
       /data/data/com.termux/cache/* \
       /data/data/com.termux/files/usr/var/cache/apt/* \
       ~/.cache/* ~/.npm/_cacache ~/.cargo/registry ~/.cargo/git 2>/dev/null

# ---- Heavy package directories (safe to delete) ----
for d in pip setuptools wheel numpy pandas matplotlib requests; do
  rm -rf "/data/data/com.termux/files/usr/lib/python3.12/site-packages/${d}"* 2>/dev/null
done

# ---- Savant local caches ----
rm -rf ~/savant/tmp/* ~/savant/cache/* ~/savant/logs/* ~/savant/exports/* 2>/dev/null
sync

# ---- Verify free space ----
FREE=$(df -Pm /data/data/com.termux | awk 'NR==2 {print $4}')
if [ "$FREE" -lt 150000 ]; then
  echo "⚠️  Still critically low on space (${FREE} KB). Running minimal fallback purge…"
  rm -rf /data/data/com.termux/files/usr/lib/python3.12/site-packages/*tests* 2>/dev/null
  sync
fi

echo "✅ Phase-0 cleanup done — launching Python orchestrator…"
# ---- Call the actual Python orchestrator ----
/data/data/com.termux/files/usr/bin/python3 ~/savant/services/scripts/utils/savant_clean_v18.py
