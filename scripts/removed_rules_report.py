import re
from datetime import datetime

REMOVALS_LOG = "rules/removed.rules"
README_PATH = "README.md"
BEGIN_TAG = "<!-- REMOVALS_BEGIN -->"
END_TAG = "<!-- REMOVALS_END -->"

def get_removed_sids():
    """Extract removed SIDs and summaries."""
    entries = []
    try:
        with open(REMOVALS_LOG) as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("# Removed:"):
                sid_match = re.search(r"SID (\d+)", lines[i])
                rule = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if sid_match:
                    entries.append((sid_match.group(1), rule))
    except FileNotFoundError:
        pass
    return entries

def build_summary_block(removed_sids):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [BEGIN_TAG]
    lines.append(f"🕒 Last rule cleanup: {timestamp}")
    if removed_sids:
        lines.append(f"🧹 Invalid rules removed: {len(removed_sids)}")
        for sid, rule in removed_sids:
            lines.append(f"SID {sid} — `{rule}`")
    else:
        lines.append("✅ No invalid rules removed in the latest sync.")
    lines.append(END_TAG)
    return "\n".join(lines)

def update_readme(summary_block):
    with open(README_PATH) as f:
        content = f.read()

    new_readme = re.sub(
        f"{BEGIN_TAG}.*?{END_TAG}",
        summary_block,
        content,
        flags=re.DOTALL
    )

    with open(README_PATH, "w") as f:
        f.write(new_readme)

if __name__ == "__main__":
    sids = get_removed_sids()
    block = build_summary_block(sids)
    update_readme(block)
    print(f"📘 Injected removal summary into README.md with {len(sids)} rule(s).")