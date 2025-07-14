Suricata Signature Sync
=======================

Automated feed discovery, rule curation, and deployment for high-performance Suricata pipelines.

This repository powers a scalable signature management system for Suricata. It dynamically pulls rules from public sources, performs post-processing to ensure hygiene and accuracy, and keeps your rule corpus updated every 12 hours via GitHub Actions — complete with override logic, SID collision detection, and status logging.

Built for large-scale environments with thousands of sensors and terabytes of daily traffic. Precision signature orchestration starts here.

----------------------------------------------------------------------
Workflow Overview
----------------------------------------------------------------------

1. Feed Discovery
   - Script: scripts/discover_suricata_feeds.py
   - Collects .rules files from public sources (Corelight, SSLBL, TrafficID)
   - Authenticated GitHub search enabled via GH_API_TOKEN
   - Files saved to: discovered_rules/

2. Rule Compilation
   - Script: scripts/fetch_rules.py
   - Merges discovered feeds into: rules/combined.rules

3. Post-Processing
   - Script: scripts/postprocess_rules.py
   - Tasks:
     • Remove duplicates
     • Detect SID collisions
     • Disable selected rules (conf/disable.conf)
     • Apply rule modifications (conf/modify.conf)
     • Re-enable rules (conf/enable.conf)
   - Output:
     • rules/combined.final.rules
     • rules/duplicates.rules
     • rules/disabled.rules
     • rules/sid_collisions.log

4. Sync Status Logging
   - File: rules/sync_status.log
   - Sample Log Entry:
     🕒 Sync Time: 2025-07-14 17:00 UTC
     📦 Final Rule Count: 8421
     🪪 SID Collisions: 3
     ✅ Status: Completed

5. GitHub Actions Scheduling
   - File: .github/workflows/update-suricata-rules.yml
   - Runs every 12 hours at midnight & noon EST (5am/5pm UTC)
   - Uses cron: 0 5,17 * * *
   - Supports manual trigger via workflow_dispatch

----------------------------------------------------------------------
Directory Structure
----------------------------------------------------------------------

.
├── discovered_rules/        # Raw downloaded rules per feed
├── rules/
│   ├── combined.rules        # Merged raw rules
│   ├── combined.final.rules  # Post-processed rule set
│   ├── duplicates.rules      # Removed duplicates
│   ├── disabled.rules        # Disabled via conf rules
│   ├── sid_collisions.log    # Detected SID conflicts
│   └── sync_status.log       # Last sync summary
├── conf/
│   ├── enable.conf           # Force-enable rules
│   ├── disable.conf          # Disable rules selectively
│   └── modify.conf           # Rewrite rule fields
├── scripts/
│   ├── discover_suricata_feeds.py
│   ├── fetch_rules.py
│   └── postprocess_rules.py
└── .github/workflows/
    └── update-suricata-rules.yml

----------------------------------------------------------------------
GitHub Token Setup
----------------------------------------------------------------------

Required for GitHub API search:

1. Create a token with `public_repo` scope
2. Save to repo secrets as: GH_API_TOKEN
3. The discovery script uses this via os.getenv("GH_API_TOKEN")

----------------------------------------------------------------------
Conf File Examples
----------------------------------------------------------------------

enable.conf:
  1050001     # Force-enable specific rules

disable.conf:
  2003142     # Disable noisy or legacy rules

modify.conf:
  1050001 msg "Exploit attempt"
  classtype shellcode-detect classtype web-application-attack

----------------------------------------------------------------------
Roadmap
----------------------------------------------------------------------

- Source tagging via source_map.json
- Export sid_registry.json for dashboards
- Slack/webhook alerts on sync success or failure
- Feed health scoring and retry logic
- Rule scoring via CVE metadata or AI

----------------------------------------------------------------------
Credits & License
----------------------------------------------------------------------

MIT License

Created by Daniel Clark
Architected with support from Microsoft Copilot  
Optimized for scalable, traceable Suricata deployments

Useful Resources:
- Suricata Documentation: https://suricata.io/documentation/
- Abuse.ch SSLBL: https://sslbl.abuse.ch/
- Emerging Threats: https://rules.emergingthreats.net/
