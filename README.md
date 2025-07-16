Suricata Signature Sync
=======================

Automated feed discovery, rule curation, and deployment for high-performance Suricata pipelines.

This repository powers a scalable signature management system for Suricata. It dynamically pulls rules from public sources, applies post-processing to ensure hygiene and accuracy, and updates your rule corpus every 12 hours via GitHub Actions. Includes override logic, SID collision detection, status logging, and README metadata updates.

Built for large-scale environments with thousands of sensors and high-volume traffic.

------------------------------------------------------------------
Pipeline Workflow Overview
------------------------------------------------------------------

1. Pre-Flight Validation
   Script: scripts/preflight_check.py
   - Confirms required folders and files exist
   - Logs last modified timestamps
   - Detects missing assets before execution

2. Feed Discovery
   Script: scripts/discover_suricata_feeds.py
   - Downloads rules from multiple public sources
   - Optionally searches GitHub using GH_API_TOKEN
   - Output saved to: discovered_rules/

3. Rule Compilation
   Script: scripts/fetch_rules.py
   - Merges discovered `.rules` files into rules/combined.rules

4. Post-Processing & Overrides
   Script: scripts/postprocess_rules.py
   - Removes duplicates
   - Detects SID collisions and logs them
   - Applies control from conf/disable.conf, enable.conf, modify.conf
   - Final output: rules/combined.final.rules
   - Logs generated:
     - duplicates.rules
     - disabled.rules
     - sid_collisions.log

5. Sync Metadata Logging
   - Output written to: rules/sync_status.log
   - Includes:
     - Sync time (UTC)
     - Final rule count
     - SID collision count
     - Sync status flag

6. README Sync Status Update
   - Workflow automatically replaces metadata block at bottom of README.md
   - Uses clear marker anchors for automated edits:
<!-- SYNC_STATUS_BEGIN -->
Last sync: 2025-07-16 03:37 UTC
Rule count: 81355
SID collisions: 60
<!-- SYNC_STATUS_END -->

7. GitHub Actions Automation
   Workflow file: .github/workflows/update-suricata-rules.yml
   - Scheduled every 12 hours (00:00 and 12:00 EST)
   - Cron: 0 5,17 * * *
   - Manual trigger available via workflow_dispatch
   - Commits curated rule output and README changes

------------------------------------------------------------------
Directory Structure
------------------------------------------------------------------

```bash
.
├── discovered_rules/              # Raw rules from external feeds
├── rules/
│   ├── combined.rules
│   ├── combined.final.rules
│   ├── duplicates.rules
│   ├── disabled.rules
│   ├── sid_collisions.log
│   └── sync_status.log
├── conf/
│   ├── enable.conf
│   ├── disable.conf
│   └── modify.conf
├── scripts/
│   ├── discover_suricata_feeds.py
│   ├── fetch_rules.py
│   ├── postprocess_rules.py
│   └── preflight_check.py
└── .github/workflows/
    └── update-suricata-rules.yml
```

------------------------------------------------------------------
GitHub Token Setup
------------------------------------------------------------------

To enable GitHub API searches:

1. Create a personal access token with `public_repo` scope.
2. Save it to repo secrets as: GH_API_TOKEN
3. The discovery script uses: os.getenv("GH_API_TOKEN")

------------------------------------------------------------------
Conf File Examples
------------------------------------------------------------------

conf/disable.conf:
  1050001    # Disable noisy rule
  2003142    # Disable legacy rule

conf/enable.conf:
  1050001    # Force-enable useful rule

conf/modify.conf:
  1050001 msg "Exploit attempt"
  classtype shellcode-detect classtype web-application-attack

------------------------------------------------------------------
Future Enhancements
------------------------------------------------------------------

- Add inline source tagging via source_map.json
- Export sid_registry.json for dashboards and alert enrichment
- Slack/webhook notifications on rule changes or sync alerts
- Feed health scoring and adaptive retry logic
- Rule scoring via CVE age, relevance, or AI heuristics

------------------------------------------------------------------
License & Credits
------------------------------------------------------------------

MIT License  
Created by Daniel  
Architected with guidance from Microsoft Copilot 🤝  
Optimized for scalable and traceable Suricata deployments.

External Resources:
- Suricata Documentation: https://suricata.io/documentation/
- SSLBL Feed (Abuse.ch): https://sslbl.abuse.ch/
- Emerging Threats: https://rules.emergingthreats.net/

------------------------------------------------------------------
SYNC STATUS
------------------------------------------------------------------

<!-- SYNC_STATUS_BEGIN -->
Last sync: 2025-07-16 03:37 UTC
Rule count: 81355
SID collisions: 60
<!-- SYNC_STATUS_END -->

------------------------------------------------------------------
REMOVED SINATURES
------------------------------------------------------------------

<!-- REMOVALS_BEGIN -->
Last sync removed: SID 1002023, SID 1050410 (invalid metadata)
<!-- REMOVALS_END -->
