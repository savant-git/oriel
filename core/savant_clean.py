#!/usr/bin/env python3
import os, glob, subprocess

def remove_old_zips():
    base = os.path.expanduser("~/savant/exports")
    if not os.path.isdir(base):
        return
    zips = sorted(glob.glob(os.path.join(base, "*.zip")), key=os.path.getmtime, reverse=True)
    for f in zips[1:]:
        os.remove(f)
        print("Removed", f)

def clean_caches():
    for path in ["~/.cache/pip", "~/.npm", "~/.cache"]:
        subprocess.run(["rm", "-rf", os.path.expanduser(path)])
    subprocess.run(["sudo","journalctl","--vacuum-time=3d"])

if __name__ == "__main__":
    remove_old_zips()
    clean_caches()
    print("Cleanup complete.")
