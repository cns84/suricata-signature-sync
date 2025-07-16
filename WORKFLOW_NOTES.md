<!-- SYNC_WORKFLOW_BEGIN -->
## 🔄 Suricata Signature Update Workflow

This GitHub Actions pipeline automates the fetch, merge, validation, and remediation of Suricata IDS rule signatures. It runs every 12 hours and includes self-healing logic for invalid signatures.

### 🔧 Steps Overview

| Step                          | Purpose                                                   | Fallbacks / Notes                                      |
|-------------------------------|------------------------------------------------------------|--------------------------------------------------------|
| 🛒 Feed Fetch (`fetch_suricata_feeds.py`) | Downloads community + ET signatures              | Handles ZIP/TAR formats, skips if feed unreachable     |
| 🔗 Rule Merge & Postprocess   | Combines and cleans ruleset into `combined.rules`         | Modular scripts allow future expansion of logic        |
| ⚙️ Config Generation          | Builds fresh `suricata.yaml` tailored for test mode       | Fails silently if not needed                           |
| ✅ Suricata Validation        | Tests merged ruleset using `suricata -T`                  | stderr redirected to `suricata_errors.log`             |
| 🧹 Remediation (`remediate_and_report.py`) | Removes invalid rules, logs count, injects README | No-op if no invalid rules detected                     |
| 📋 Sync Log Update            | Appends metadata to `sync_status.log`                     | Includes timestamp and final rule count                |
| 📘 README Injection           | Updates `<REMOVALS>` and `<SYNC_STATUS>` blocks           | Includes timestamped summary even on clean runs        |
| ⬆️ Conditional Commit         | Commits only if tracked changes occurred                  | Skipped on no-op runs to avoid commit spam             |

### 🕒 Schedule

- Cron: `0 5,17 * * *` → Runs at 05:00 and 17:00 UTC daily  
- Manual trigger: Available via `workflow_dispatch`

### 🔐 Permissions

- Requires `PAT_TOKEN` stored in GitHub secrets  
- Uses `contents: write` permission for README and rule file updates

### 📂 Output Files

- `rules/combined.rules` — Final merged ruleset  
- `rules/removed.rules` — Invalid rules removed  
- `rules/sync_status.log` — Sync metadata  
- `README.md` — Visual summary of SID removals and sync status  
- `suricata.yaml` — Fresh test config

<!-- SYNC_WORKFLOW_END -->