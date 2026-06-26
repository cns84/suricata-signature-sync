Suricata Signature Sync
=======================

Automated feed discovery, rule curation, validation, and remediation for high-performance Suricata pipelines.

This repository powers a scalable signature management system for Suricata. It dynamically pulls rules from public sources, applies post-processing to ensure hygiene and accuracy, validates the ruleset, removes broken signatures, and updates your corpus every 12 hours via GitHub Actions. Includes override logic, SID collision detection, sync logging, and README metadata injection.

Built for large-scale environments with thousands of sensors and high-volume traffic.

------------------------------------------------------------------
Pipeline Workflow Overview
------------------------------------------------------------------

1. Pre-Flight Validation
   Script: scripts/preflight_check.py
   - Confirms required folders and files exist
   - Logs last modified timestamps
   - Detects missing assets before execution

2. Feed Fetching
   Script: scripts/fetch_suricata_feeds.py
   - Downloads rules from community and ET sources
   - Handles ZIP/TAR formats securely
   - Output saved to: rules/community/, rules/emerging/

3. Rule Merging & Post-Processing
   Scripts: scripts/merge_rules.py, scripts/postprocess_rules.py
   - Combines `.rules` files into combined.rules
   - Removes duplicates, detects SID collisions
   - Applies overrides from conf/*.conf
   - Final output: rules/combined.final.rules
   - Logs:
     - duplicates.rules
     - disabled.rules
     - sid_collisions.log

4. Suricata Validation
   - Runs suricata -T in test mode
   - Errors logged to: rules/suricata_errors.log

5. Remediation & Reporting
   Script: scripts/remediate_and_report.py
   - Removes invalid rules based on error lines/SIDs
   - Logs removed rules to removed.rules
   - Appends removal count to sync_status.log
   - Injects summary block into README.md

6. Sync Metadata Logging
   Output written to: rules/sync_status.log
   Includes:
   - Sync time (UTC)
   - Final rule count
   - SID collision count
   - Removal count

7. README Sync Status Update
   Workflow automatically replaces metadata blocks using anchors:
<!-- SYNC_STATUS_BEGIN -->
Last sync: 2026-06-26 08:30 UTC
Rule count: 81982
<!-- SYNC_STATUS_END -->

   <!-- REMOVALS_BEGIN -->
🕒 Last rule cleanup: 2026-06-26 08:30 UTC
✅ No invalid rules removed in the latest sync.
<!-- REMOVALS_END -->

8. GitHub Actions Automation
   Workflow file: .github/workflows/suricata_signature_update.yml
   - Scheduled every 12 hours (05:00 and 17:00 UTC)
   - Cron: 0 5,17 * * *
   - Manual trigger via workflow_dispatch
   - Commits curated rule output and README changes only if updates occurred

------------------------------------------------------------------
Directory Structure
------------------------------------------------------------------
``` bash
.
├── rules/
│   ├── combined.rules
│   ├── combined.final.rules
│   ├── removed.rules
│   ├── sid_collisions.log
│   ├── sync_status.log
│   └── suricata_errors.log
├── conf/
│   ├── enable.conf
│   ├── disable.conf
│   └── modify.conf
├── scripts/
│   ├── fetch_suricata_feeds.py
│   ├── merge_rules.py
│   ├── postprocess_rules.py
│   ├── preflight_check.py
│   └── remediate_and_report.py
└── .github/workflows/
    └── suricata_signature_update.yml
```

------------------------------------------------------------------
GitHub Token Setup
------------------------------------------------------------------

To enable GitHub API searches (optional):

1. Create a personal access token with public_repo scope
2. Save it to repo secrets as: GH_API_TOKEN
3. Discovery script uses: os.getenv("GH_API_TOKEN")

------------------------------------------------------------------
Conf File Examples
------------------------------------------------------------------

disable.conf
  1050001    # Disable noisy rule
  2003142    # Disable legacy rule

enable.conf
  1050001    # Force-enable useful rule

modify.conf
  1050001 msg "Exploit attempt"
  classtype shellcode-detect classtype web-application-attack

------------------------------------------------------------------
Future Enhancements
------------------------------------------------------------------

- Quarantine removed rules instead of deleting
- Export sid_registry.json for dashboards
- Slack/webhook alerts on rule changes
- Feed health scoring and retry logic
- Rule scoring via CVE age, relevance, or AI heuristics

------------------------------------------------------------------
License & Credits
------------------------------------------------------------------

Created by Daniel Clark  
Email: cns_84@outlook.com  
Architected with guidance from Microsoft Copilot 🤝  
Optimized for scalable and traceable Suricata deployments.

External Resources:
- Suricata Documentation: https://suricata.io/documentation/
- SSLBL Feed (Abuse.ch): https://sslbl.abuse.ch/
- Emerging Threats: https://rules.emergingthreats.net/
