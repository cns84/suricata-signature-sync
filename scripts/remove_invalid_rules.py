import re
import os

RULESET_PATH = "rules/combined.rules"
ERROR_LOG_PATH = "rules/suricata_errors.log"
REMOVED_RULES_PATH = "rules/removed.rules"

def extract_invalid_lines():
    """Parse Suricata error log and extract line numbers of faulty rules."""
    line_nums = set()
    sid_map = {}  # Optional SID tracking
    if not os.path.isfile(ERROR_LOG_PATH):
        print("No error log found — skipping cleanup.")
        return line_nums, sid_map

    with open(ERROR_LOG_PATH, "r") as f:
        for line in f:
            # Match: rules/combined.rules:123 ...
            m = re.search(r"combined\.rules:(\d+)", line)
            if m:
                num = int(m.group(1))
                line_nums.add(num)

            # Match SID if available
            sid_match = re.search(r"sid[:=](\d+)", line)
            if sid_match:
                sid = sid_match.group(1)
                sid_map[num] = sid

    return line_nums, sid_map

def remove_invalid_rules(line_nums, sid_map):
    """Remove offending rule lines and log them."""
    if not os.path.isfile(RULESET_PATH):
        print("Ruleset missing — aborting.")
        return 0

    with open(RULESET_PATH, "r") as f:
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

    with open(REMOVED_RULES_PATH, "w") as f:
        for line in removed:
            sid_str = ""
            sid_match = re.search(r"sid[:=](\d+)", line)
            if sid_match:
                sid_str = f"SID {sid_match.group(1)}"
            f.write(f"# Removed: {sid_str}\n{line}\n")

    print(f"✅ Removed {len(removed)} invalid rule(s). Logged to {REMOVED_RULES_PATH}")
    return len(removed)

if __name__ == "__main__":
    line_nums, sid_map = extract_invalid_lines()
    removed_count = remove_invalid_rules(line_nums, sid_map)
    # Optional: print removed SIDs for README injection
    print("🔍 Removed SIDs:", [sid for sid in sid_map.values()])