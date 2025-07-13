import os
import hashlib

rules_dir = "rules"
merged_rules_path = os.path.join(rules_dir, "combined.rules")
log_path = os.path.join(rules_dir, "merge_log.txt")
seen_hashes = set()
merged_lines = []

def hash_rule(rule_line):
    return hashlib.md5(rule_line.strip().encode()).hexdigest()

# Scan and merge
for filename in os.listdir(rules_dir):
    if filename.endswith(".rules") and filename != "combined.rules":
        with open(os.path.join(rules_dir, filename), "r") as f:
            lines = f.readlines()
            added = 0
            for line in lines:
                if line.strip().startswith("#") or not line.strip():
                    continue
                h = hash_rule(line)
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    merged_lines.append(line)
                    added += 1
            print(f"Merged {added} lines from {filename}")

# Save combined rules
with open(merged_rules_path, "w") as f:
    f.writelines(merged_lines)

# Log the merge operation
with open(log_path, "a") as f:
    f.write(f"✔ Merged {len(merged_lines)} unique rules from {rules_dir}/ at version snapshot.\n")