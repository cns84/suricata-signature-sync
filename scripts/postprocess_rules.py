#!/usr/bin/env python3
import os
import re
from collections import defaultdict, OrderedDict

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
RULES_FILE = "rules/combined.rules"
FINAL_FILE = "rules/combined.final.rules"
DISABLED_FILE = "rules/disabled.rules"
DUPLICATE_FILE = "rules/duplicates.rules"
SID_COLLISIONS_FILE = "rules/sid_collisions.log"
FLOWBIT_LOG = "rules/flowbit_dependencies.log"
STATS_FILE = "rules/stats.txt"

ENABLE_CONF = "conf/enable.conf"
DISABLE_CONF = "conf/disable.conf"
MODIFY_CONF = "conf/modify.conf"

# -------------------------------------------------------------------
# Regex helpers
# -------------------------------------------------------------------
sid_re = re.compile(r"\bsid\s*:\s*(\d+)\s*;")
msg_re = re.compile(r'\bmsg\s*:\s*"([^"]*)"')
classtype_re = re.compile(r"\bclasstype\s*:\s*([^;]+)\s*;")
metadata_re = re.compile(r"\bmetadata\s*:\s*([^;]+)\s*;")
flowbits_re = re.compile(r"\bflowbits\s*:\s*([^;]+)\s*;")

# -------------------------------------------------------------------
# Conf parsing (Suricata-update–style)
# -------------------------------------------------------------------
class MatchRule:
    def __init__(self, kind, value):
        self.kind = kind  # sid, re, msg, classtype, metadata, source
        self.value = value
        if kind == "re":
            self.regex = re.compile(value)
        else:
            self.regex = None

    def matches(self, rule_text, sid=None, source=None):
        if self.kind == "sid":
            return sid is not None and sid == self.value
        if self.kind == "re":
            return bool(self.regex.search(rule_text))
        if self.kind == "msg":
            m = msg_re.search(rule_text)
            return bool(m and re.search(self.value, m.group(1)))
        if self.kind == "classtype":
            m = classtype_re.search(rule_text)
            return bool(m and self.value == m.group(1).strip())
        if self.kind == "metadata":
            m = metadata_re.search(rule_text)
            return bool(m and self.value in m.group(1))
        if self.kind == "source":
            return source == self.value
        return False


def parse_conf_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Examples:
    # sid:2010935
    # re:ET.*Malware
    # msg:.*MALWARE-CNC.*
    # classtype:trojan-activity
    # metadata:former_category Malware
    # source:github
    if ":" not in line:
        return None
    kind, value = line.split(":", 1)
    kind = kind.strip()
    value = value.strip()
    if kind not in {"sid", "re", "msg", "classtype", "metadata", "source"}:
        return None
    if kind == "sid":
        return MatchRule("sid", value)
    if kind == "re":
        return MatchRule("re", value)
    if kind == "msg":
        return MatchRule("msg", value)
    if kind == "classtype":
        return MatchRule("classtype", value)
    if kind == "metadata":
        return MatchRule("metadata", value)
    if kind == "source":
        return MatchRule("source", value)
    return None


def load_match_rules(path):
    rules = []
    if not os.path.exists(path):
        return rules
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            r = parse_conf_line(line)
            if r:
                rules.append(r)
    return rules


# -------------------------------------------------------------------
# modify.conf parsing (Suricata-update–style)
# -------------------------------------------------------------------
class ModifyRule:
    def __init__(self, match_rule, assignments):
        self.match_rule = match_rule  # MatchRule
        self.assignments = assignments  # list of (field, value)

    def matches(self, rule_text, sid=None, source=None):
        return self.match_rule.matches(rule_text, sid=sid, source=source)

    def apply(self, rule_text):
        text = rule_text

        for field, value in self.assignments:
            if field == "msg":
                # Replace or add msg
                if msg_re.search(text):
                    text = msg_re.sub(f'msg:"{value}";', text)
                else:
                    text = text.rstrip().rstrip(")")  # crude but ok
                    text = text.replace(";", " ;", 1)
                    text = text + f' msg:"{value}";'
            elif field == "classtype":
                if classtype_re.search(text):
                    text = classtype_re.sub(f"classtype:{value};", text)
                else:
                    text = text.rstrip().rstrip(")")
                    text = text + f" classtype:{value};"
            elif field == "metadata":
                if metadata_re.search(text):
                    m = metadata_re.search(text)
                    existing = m.group(1).strip()
                    new_meta = existing + ", " + value
                    text = metadata_re.sub(f"metadata:{new_meta};", text)
                else:
                    text = text.rstrip().rstrip(")")
                    text = text + f" metadata:{value};"
            else:
                # Generic field replace/add: field:value;
                field_re = re.compile(rf"\b{re.escape(field)}\s*:\s*([^;]+)\s*;")
                if field_re.search(text):
                    text = field_re.sub(f"{field}:{value};", text)
                else:
                    text = text.rstrip().rstrip(")")
                    text = text + f" {field}:{value};"

        return text


def parse_modify_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Example:
    # sid:2010935 msg:"New message"; classtype:trojan-activity;
    # re:ET.* msg:"New message";
    if " " not in line:
        return None
    selector, rest = line.split(" ", 1)
    mr = parse_conf_line(selector)
    if not mr:
        return None

    assignments = []
    # parse assignments like: msg:"New message"; classtype:trojan-activity;
    parts = [p.strip() for p in rest.split(";") if p.strip()]
    for p in parts:
        if ":" not in p:
            continue
        field, val = p.split(":", 1)
        field = field.strip()
        val = val.strip().strip('"')
        assignments.append((field, val))
    if not assignments:
        return None
    return ModifyRule(mr, assignments)


def load_modify_rules(path):
    rules = []
    if not os.path.exists(path):
        return rules
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            r = parse_modify_line(line)
            if r:
                rules.append(r)
    return rules


# -------------------------------------------------------------------
# Rule object
# -------------------------------------------------------------------
class Rule:
    def __init__(self, text, source="github"):
        self.original = text.rstrip("\n")
        self.text = self.original
        self.source = source
        self.sid = self._extract_sid()
        self.flowbits = self._extract_flowbits()
        self.disabled = self.text.strip().startswith("#")

    def _extract_sid(self):
        m = sid_re.search(self.text)
        return m.group(1) if m else None

    def _extract_flowbits(self):
        m = flowbits_re.search(self.text)
        if not m:
            return []
        parts = [p.strip() for p in m.group(1).split(",")]
        return parts

    def enable(self):
        if self.text.strip().startswith("#"):
            self.text = self.text.lstrip("#").strip()
            self.disabled = False

    def disable(self):
        if not self.text.strip().startswith("#"):
            self.text = "# " + self.text
            self.disabled = True

    def apply_modify(self, modify_rules):
        for mr in modify_rules:
            if mr.matches(self.text, sid=self.sid, source=self.source):
                self.text = mr.apply(self.text)

    def matches_any(self, match_rules):
        return any(mr.matches(self.text, sid=self.sid, source=self.source) for mr in match_rules)


# -------------------------------------------------------------------
# Load rules
# -------------------------------------------------------------------
if not os.path.exists(RULES_FILE):
    print(f"❌ File not found: {RULES_FILE}")
    raise SystemExit(1)

print(f"🔍 Processing: {RULES_FILE}")

raw_rules = []
with open(RULES_FILE, "r", encoding="utf-8") as f:
    for line in f:
        stripped = line.strip()
        if not stripped:
            continue
        # treat everything in combined.rules as "github" source
        raw_rules.append(Rule(stripped, source="github"))

# -------------------------------------------------------------------
# Load confs
# -------------------------------------------------------------------
disable_rules = load_match_rules(DISABLE_CONF)
enable_rules = load_match_rules(ENABLE_CONF)
modify_rules = load_modify_rules(MODIFY_CONF)

print(f"   Loaded {len(disable_rules)} disable rules")
print(f"   Loaded {len(enable_rules)} enable rules")
print(f"   Loaded {len(modify_rules)} modify rules")

# -------------------------------------------------------------------
# Deduplicate + SID collision handling (Prefer GitHub)
# -------------------------------------------------------------------
# Prefer GitHub: since all are "github" here, we use "last wins" semantics
unique_by_text = set()
sid_map = defaultdict(list)
ordered_rules = []

duplicates = []

for r in raw_rules:
    if r.text in unique_by_text:
        duplicates.append(r.text)
        continue
    unique_by_text.add(r.text)
    ordered_rules.append(r)
    if r.sid:
        sid_map[r.sid].append(r)

# Resolve SID collisions: prefer GitHub (here: last occurrence wins)
resolved_rules = OrderedDict()
for r in ordered_rules:
    if r.sid is None:
        key = id(r)
        resolved_rules[key] = r
    else:
        resolved_rules[r.sid] = r  # last wins

final_rules_list = list(resolved_rules.values())

collisions = {sid: rules for sid, rules in sid_map.items() if len(rules) > 1}

# -------------------------------------------------------------------
# Apply disable / modify / enable
# -------------------------------------------------------------------
disabled_rules_out = []

for r in final_rules_list:
    # disable.conf
    if r.matches_any(disable_rules):
        r.disable()
        disabled_rules_out.append(r.text)
        continue

    # modify.conf
    r.apply_modify(modify_rules)

    # enable.conf
    if r.matches_any(enable_rules):
        r.enable()

# -------------------------------------------------------------------
# Flowbit dependency resolution (auto-enable required dependencies)
# -------------------------------------------------------------------
# Build map: flowbit name -> rules that set it
flowbit_sets = defaultdict(list)
flowbit_requires = defaultdict(list)

for r in final_rules_list:
    for fb in r.flowbits:
        if fb.startswith("set,"):
            name = fb.split(",", 1)[1].strip()
            flowbit_sets[name].append(r)
        elif fb.startswith("isset,") or fb.startswith("isnotset,"):
            name = fb.split(",", 1)[1].strip()
            flowbit_requires[name].append(r)

auto_enabled = []

for name, requiring_rules in flowbit_requires.items():
    if name not in flowbit_sets:
        continue
    for setter in flowbit_sets[name]:
        if setter.disabled:
            setter.enable()
            auto_enabled.append((name, setter.sid or setter.text[:80]))

# -------------------------------------------------------------------
# Write outputs
# -------------------------------------------------------------------
with open(FINAL_FILE, "w", encoding="utf-8") as out:
    for r in final_rules_list:
        out.write(r.text.rstrip("\n") + "\n")

print(f"✅ Final rules saved to: {FINAL_FILE}")

if disabled_rules_out:
    with open(DISABLED_FILE, "w", encoding="utf-8") as out:
        for line in disabled_rules_out:
            out.write(line.rstrip("\n") + "\n")
    print(f"🚫 Disabled rules saved to: {DISABLED_FILE}")

if duplicates:
    with open(DUPLICATE_FILE, "w", encoding="utf-8") as out:
        for line in duplicates:
            out.write(line.rstrip("\n") + "\n")
    print(f"🔁 Duplicates saved to: {DUPLICATE_FILE}")

if collisions:
    with open(SID_COLLISIONS_FILE, "w", encoding="utf-8") as out:
        for sid, rules in collisions.items():
            out.write(f"\nSID {sid} has {len(rules)} collisions:\n")
            for rule in rules:
                out.write(f"  {rule.text if isinstance(rule, Rule) else rule}\n")
    print(f"🪪 SID collisions logged to: {SID_COLLISIONS_FILE}")

if auto_enabled:
    with open(FLOWBIT_LOG, "w", encoding="utf-8") as out:
        for name, sid in auto_enabled:
            out.write(f"flowbit '{name}' -> auto-enabled rule SID/desc: {sid}\n")
    print(f"🌊 Flowbit dependencies logged to: {FLOWBIT_LOG}")

with open(STATS_FILE, "w", encoding="utf-8") as out:
    out.write("Post-Processing Stats\n")
    out.write(f"Final rules: {len(final_rules_list)}\n")
    out.write(f"Disabled rules: {len(disabled_rules_out)}\n")
    out.write(f"Duplicates: {len(duplicates)}\n")
    out.write(f"SID collisions: {len(collisions)}\n")
    out.write(f"Flowbit auto-enabled: {len(auto_enabled)}\n")

print("\n📊 Post-Processing Summary:")
print(f"   ✔ Final rules:          {len(final_rules_list)}")
print(f"   🚫 Disabled rules:      {len(disabled_rules_out)}")
print(f"   🔁 Duplicates:          {len(duplicates)}")
print(f"   🪪 SID collisions:      {len(collisions)}")
print(f"   🌊 Flowbit auto-enable: {len(auto_enabled)}")
