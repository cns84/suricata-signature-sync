import re
from datetime import datetime
import os

RULESET_PATH = "rules/combined.rules"
ERROR_LOG_PATH = "rules/suricata_errors.log"
REMOVED_RULES_PATH = "rules/removed.rules"
SYNC_LOG_PATH = "rules/sync_status.log"
README_PATH = "README.md"

BEGIN_TAG = "<!-- REMOVALS_BEGIN -->"
END_TAG = "<!-- REMOVALS_END -->"

def extract_invalid_lines():
    line_nums = set()
    sid_map = {}
    if not os.path.isfile(ERROR_LOG_PATH):
        print("No error log found.")
        return line_nums, sid_map

    with open(ERROR_LOG_PATH) as f:
        for line in f:
            m = re.search(r"combined\.rules:(\d+)", line)
            if m:
                line_num = int(m.group(1))
                line_nums.add(line_num)

            sid_match = re.search(r"sid[:=](\d+)", line)
            if sid_match:
                sid = sid_match.group(1)
                sid_map[line_num] = sid
    return line_nums, sid_map

def remove_invalid_rules(line_nums, sid_map):
    if not os.path.isfile(RULESET_PATH):
        print("Ruleset missing.")
        return [], []

    with open(RULESET_PATH) as f:
        lines = f.readlines()

    removed = []
    cleaned = []

    for idx, line in enumerate(lines, start=1):
        if idx in line_nums:
            removed.append(line.strip())
        else:
            cleaned.append(line)

    with open(RULESET_PATH, "w") as f:
        f.writelines(cleaned)

    removed_sids = []
    with open(REMOVED_RULES_PATH, "w") as f:
        for rule in removed:
            sid_match = re.search(r"sid[:=](\d+)", rule)
            sid = sid_match.group(1) if sid_match else None
            if sid:
                removed_sids.append((sid, rule))
                f.write(f"# Removed: SID {sid}\n{rule}\n")
            else:
                f.write(f"# Removed:\n{rule}\n")

    return removed_sids, removed

def log_sync_status(removed_count):
    with open(SYNC_LOG_PATH, "a") as log:
        log.write(f"🧹 Invalid Rules Removed: {removed_count}\n")

def inject_readme_summary(removed_sids):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [BEGIN_TAG, f"🕒 Last rule cleanup: {timestamp}"]

    if removed_sids:
        lines.append(f"🧹 Invalid rules removed: {len(removed_sids)}")
        for sid, rule in removed_sids:
            lines.append(f"SID {sid} — `{rule}`")
    else:
        lines.append("✅ No invalid rules removed in the latest sync.")
    lines.append(END_TAG)
    block = "\n".join(lines)

    with open(README_PATH) as f:
        content = f.read()

    new_content = re.sub(f"{BEGIN_TAG}.*?{END_TAG}", block, content, flags=re.DOTALL)
    with open(README_PATH, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    line_nums, sid_map = extract_invalid_lines()
    removed_sids, removed = remove_invalid_rules(line_nums, sid_map)
    log_sync_status(len(removed_sids))
    inject_readme_summary(removed_sids)
    print(f"✅ Cleanup completed: {len(removed_sids)} rules removed.")