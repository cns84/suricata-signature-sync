import os
import time

REQUIRED_DIRS = [
    "discovered_rules",
    "rules",
    "conf",
    "scripts"
]

REQUIRED_FILES = [
    "rules/combined.rules",
    "rules/combined.final.rules",
    "rules/sync_status.log",
    "conf/enable.conf",
    "conf/disable.conf",
    "conf/modify.conf"
]

def check_directories():
    print("📁 Checking required folders...")
    for d in REQUIRED_DIRS:
        if not os.path.isdir(d):
            print(f"❌ Missing folder: {d}")
        else:
            print(f"✅ Folder exists: {d}")

def check_files():
    print("\n📄 Checking required files...")
    for f in REQUIRED_FILES:
        if not os.path.isfile(f):
            print(f"⚠️ Missing file: {f}")
        else:
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(f)))
            print(f"✅ Found: {f}  (Last modified: {mod_time} UTC)")

def run_preflight():
    print("🚦 Suricata Sync Pre-Flight Check\n")
    check_directories()
    check_files()
    print("\n✅ Validation complete.\n")

if __name__ == "__main__":
    run_preflight()