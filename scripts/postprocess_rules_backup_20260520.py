import os
import re
from collections import defaultdict

# Paths
RULES_FILE = "rules/combined.rules"
FINAL_FILE = "rules/combined.final.rules"
DISABLED_FILE = "rules/disabled.rules"
DUPLICATE_FILE = "rules/duplicates.rules"
SID_COLLISIONS_FILE = "rules/sid_collisions.log"

# Conf files
ENABLE_CONF = "conf/enable.conf"
DISABLE_CONF = "conf/disable.conf"
MODIFY_CONF = "conf/modify.conf"

# Regex
sid_pattern = re.compile(r"sid\s*:\s*(\d+)\s*;")
disabled_pattern = re.compile(r"^\s*#")

# Load control lists
def load_conf(path):
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(line.strip() for line in f if line.strip() and not line.startswith("#"))

enable_sids = load_conf(ENABLE_CONF)
disable_sids = load_conf(DISABLE_CONF)

# Load modify rules
modify_rules = []
if os.path.exists(MODIFY_CONF):
    with open(MODIFY_CONF, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.strip().split(" ", 2)
                if len(parts) == 3:
                    modify_rules.append((re.compile(parts[0]), parts[1], parts[2]))

# Processing
unique_rules = set()
sid_map = defaultdict(list)
final_rules = []
disabled_rules = []
duplicates = []

print(f"🔍 Processing: {RULES_FILE}")
if not os.path.exists(RULES_FILE):
    print(f"❌ File not found: {RULES_FILE}")
    exit(1)

with open(RULES_FILE, "r", encoding="utf-8") as f:
    for line in f:
        stripped = line.strip()
        if not stripped:
            continue

        # Detect SID
        sid_match = sid_pattern.search(stripped)
        sid = sid_match.group(1) if sid_match else None

        # Check for duplicates
        if stripped in unique_rules:
            duplicates.append(line)
            continue
        unique_rules.add(stripped)

        # SID collision tracking
        if sid:
            sid_map[sid].append(stripped)

        # Apply disable.conf
        if sid in disable_sids:
            disabled_rules.append(f"# {line}")
            continue

        # Apply modify.conf
        for pattern, find, replace in modify_rules:
            if pattern.search(stripped):
                line = re.sub(find, replace, line)
                break

        # Apply enable.conf (uncomment if disabled)
        if sid in enable_sids and line.strip().startswith("#"):
            line = line.lstrip("#").strip()

        final_rules.append(line)

# Write outputs
with open(FINAL_FILE, "w", encoding="utf-8") as out:
    out.writelines(f"{r}\n" for r in final_rules)
print(f"✅ Final rules saved to: {FINAL_FILE}")

if disabled_rules:
    with open(DISABLED_FILE, "w", encoding="utf-8") as out:
        out.writelines(disabled_rules)
    print(f"🚫 Disabled rules saved to: {DISABLED_FILE}")

if duplicates:
    with open(DUPLICATE_FILE, "w", encoding="utf-8") as out:
        out.writelines(duplicates)
    print(f"🔁 Duplicates saved to: {DUPLICATE_FILE}")

collisions = {sid: rules for sid, rules in sid_map.items() if len(rules) > 1}
if collisions:
    with open(SID_COLLISIONS_FILE, "w", encoding="utf-8") as out:
        for sid, rules in collisions.items():
            out.write(f"\nSID {sid} has {len(rules)} collisions:\n")
            for rule in rules:
                out.write(f"  {rule}\n")
    print(f"🪪 SID collisions logged to: {SID_COLLISIONS_FILE}")

# Summary
print("\n📊 Post-Processing Summary:")
print(f"   ✔ Final rules:      {len(final_rules)}")
print(f"   🚫 Disabled rules:  {len(disabled_rules)}")
print(f"   🔁 Duplicates:      {len(duplicates)}")
print(f"   🪪 SID collisions:  {len(collisions)}")