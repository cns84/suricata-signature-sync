# scripts/update_status.py

def append_removal_count():
    try:
        with open("rules/removed.rules") as f:
            count = sum(1 for line in f if line.startswith("# Removed:"))
    except FileNotFoundError:
        count = 0

    with open("rules/sync_status.log", "a") as log:
        log.write(f"🧹 Invalid Rules Removed: {count}\n")

if __name__ == "__main__":
    append_removal_count()