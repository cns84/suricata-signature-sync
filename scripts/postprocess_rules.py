#!/usr/bin/env python3
import os
import re
from collections import defaultdict

RULES_FILE = "rules/combined.rules"
OUTPUT_FILE = "rules/combined.cleaned.rules"
DISABLED_FILE = "rules/disabled.rules"
DUPLICATE_FILE = "rules/duplicates.rules"
SID_COLLISIONS_FILE = "rules/sid_collisions.log"

# 🧠 Regex patterns
sid_pattern = re.compile(r"sid\s*:\s*(\d+)\s*;")
disabled_pattern = re.compile(r"^\s*#")
rule_lines = []
disabled_rules = []
sid_map = defaultdict(list)
unique_rules = set()
duplicates = []

print(f"🔍 Scanning: {RULES_FILE}")

if not os.path.exists(RULES_FILE):
    print(f"❌ File not found: {RULES_FILE}")
    exit(1)

with open(RULES_FILE, "r", encoding="utf-8") as f:
    for line in f:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Detect disabled rules
        if disabled_pattern.match(stripped):
            disabled_rules.append(line)
            continue

        # Detect duplicates
        if stripped in unique_rules:
            duplicates.append(line)
            continue
        unique_rules.add(stripped)

        # Detect SID collisions
        sid_match = sid_pattern.search(stripped)
        if sid_match:
            sid = sid_match.group(1)
            sid_map[sid].append(stripped)

        rule_lines.append(line)

# ✍️ Write cleaned rules
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.writelines(rule_lines)
print(f"✅ Cleaned rules saved to: {OUTPUT_FILE}")

# ✍️ Write disabled rules
if disabled_rules:
    with open(DISABLED_FILE, "w", encoding="utf-8") as out:
        out.writelines(disabled_rules)
    print(f"🚫 Disabled rules saved to: {DISABLED_FILE}")

# ✍️ Write duplicates
if duplicates:
    with open(DUPLICATE_FILE, "w", encoding="utf-8") as out:
        out.writelines(duplicates)
    print(f"🔁 Duplicates saved to: {DUPLICATE_FILE}")

# ✍️ Log SID collisions
collisions = {sid: rules for sid, rules in sid_map.items() if len(rules) > 1}
if collisions:
    with open(SID_COLLISIONS_FILE, "w", encoding="utf-8") as out:
        for sid, rules in collisions.items():
            out.write(f"\nSID {sid} has {len(rules)} collisions:\n")
            for rule in rules:
                out.write(f"  {rule}\n")
    print(f"🪪 SID collisions logged to: {SID_COLLISIONS_FILE}")

# 📊 Summary
print("\n📊 Post-Processing Summary:")
print(f"   ✔ Total rules kept: {len(rule_lines)}")
print(f"   🚫 Disabled rules:   {len(disabled_rules)}")
print(f"   🔁 Duplicates:       {len(duplicates)}")
print(f"   🪪 SID collisions:   {len(collisions)}")