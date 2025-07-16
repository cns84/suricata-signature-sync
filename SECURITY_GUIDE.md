# SECURITY_GUIDE.md

## 🧠 Purpose

This guide documents the security principles and operational hygiene practices embedded in the Suricata signature update pipeline. It covers:

- Feed integrity & sourcing
- Signature validation & sanitization
- SID conflict resolution
- Automation hardening
- Audit trails for every change

---

## 🛒 1. Rule Feed Hygiene

| Source            | Integrity Practice                                 | Notes                          |
|------------------|-----------------------------------------------------|--------------------------------|
| Community Rules  | Downloaded via HTTPS                                | Fetched using `requests`       |
| Emerging Threats | Fetched over HTTPS and unpacked safely              | Validated format post-download |
| File Handling    | All extraction uses safe basename filtering         | Prevents path traversal        |

- Zip/Tar handling is sandboxed and cleaned post-extraction
- Feeds are stored in `rules/` with separation by origin

---

## 🧹 2. Invalid Signature Remediation

| Check                      | Enforcement                              |
|---------------------------|-------------------------------------------|
| Suricata validation       | `suricata -T -c suricata.yaml -S rules/...` |
| Error parsing             | Extracts `line_num` + optional `SID`     |
| Signature removal         | Automatically removes broken lines       |
| Audit log                 | `rules/removed.rules` contains traceable removals |

- Only rules that fail validation (and are traceable by line) are removed
- Removal count and SID list are logged, summarized, and surfaced

---

## 🪪 3. SID Collisions & Overrides

| Source                     | Detection Mechanism         | Location        |
|---------------------------|-----------------------------|-----------------|
| Duplicate SIDs            | Custom parser during merge  | `sid_collisions.log` |
| Override precedence       | Custom rules take priority  | Merge logic     |

- Rules with identical SIDs are reported
- Override logic can be extended in `postprocess_rules.py`

---

## 🔐 4. GitHub Automation Hardening

| Practice                         | Safeguard                                  |
|----------------------------------|--------------------------------------------|
| Token usage                      | `PAT_TOKEN` stored in GitHub secrets       |
| Commit enforcement               | Commits only on actual rule changes        |
| Permissions                      | Workflow uses `contents: write` only       |
| Suricata install failure fallback| `\|\| true` used for graceful fallback       |

---

## 📘 5. Audit & Observability

| Artifact               | Purpose                               |
|------------------------|----------------------------------------|
| `rules/sync_status.log`| Logs timestamp, rule count, removals   |
| `rules/removed.rules`  | Stores removed rules & associated SIDs |
| `README.md`            | Summarizes removal stats with timestamp|
| `WORKFLOW_NOTES.md`    | Documents orchestration flow           |

- All updates are timestamped in UTC
- No change → No push: avoids noise in commit history
- Logs and markdown blocks injected safely using regex or marker comments

---

## 🧪 Future Enhancements

- Quarantine removed rules instead of deleting
- Re-validate cleaned ruleset to confirm integrity
- Hash-based feed integrity checks
- Optional webhook alert on failure or rule count drop

---

> 📌 This guide is maintained alongside the pipeline itself. Changes to remediation, logging, or feed handling should be reflected here.
