# Suricata Signature Sync

A modular, automated pipeline for discovering, curating, and deploying Suricata signatures from public and GitHub-based sources. Designed for large-scale network environments requiring feed provenance, rule hygiene, and continuous updates.

---

## 🧠 What This Project Does

- 📡 Discovers Suricata rule feeds from multiple public sources
- 🌐 Searches GitHub repositories for `.rules` files
- 📦 Merges rules into a unified corpus
- 🔍 Post-processes rules to:
  - Remove duplicates
  - Detect and resolve SID collisions
  - Filter disabled or noisy rules
  - Apply SID-specific overrides via `conf/`
- 🕒 Schedules automated syncs every 12 hours via GitHub Actions
- 📊 Logs sync results to `rules/sync_status.log`

---

## 🔁 Workflow Overview

### 1. **Feed Discovery**
Run `scripts/discover_suricata_feeds.py`

- Pulls rules from feeds listed in `scripts/discover_suricata_feeds.py`
- Saves each source’s rules to `discovered_rules/`
- Logs source name, rule count, and success/failure status

### 2. **Rule Merging**
Run `scripts/fetch_rules.py`

- Merges individual feed `.rules` files into `rules/combined.rules`
- Prepares the rule corpus for cleanup and curation

### 3. **Post-Processing**
Run `scripts/postprocess_rules.py`

- Reads `combined.rules` and outputs:
  - `combined.final.rules` — clean and ready for deployment
  - `duplicates.rules` — duplicate rules removed from final set
  - `disabled.rules` — rules filtered due to override logic
  - `sid_collisions.log` — report of overlapping SIDs across feeds
- Applies overrides from `conf/`:
  - `enable.conf` — forces rules to remain active
  - `disable.conf` — disables specific rules by SID
  - `modify.conf` — rewrites rule attributes using search/replace

### 4. **Sync Status Logging**
After post-processing, the workflow appends a status heartbeat:

```text
🕒 Sync Time: 2025-07-14 17:00 UTC
📦 Final Rule Count: 8421
🪪 SID Collisions: 3
✅ Status: Completed