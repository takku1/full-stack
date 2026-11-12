---
discipline: privacy
triggers: [personal data]
tier2_when: [regulated data, health, children, many users, data shared with third parties]
---

# Privacy and data governance

## Policy

- Tier 1 when personal data is stored or processed; tier 2 for regulated
  or sensitive data.
- Default: collect the minimum; every personal field has a purpose, a
  retention period, and a deletion path that reaches every copy.
- Never: personal data in logs, analytics, or test fixtures from production;
  a copy (cache, export, backup) that deletion cannot reach.

## Framework

LINDDUN's seven privacy threat categories: linking, identifying,
non-repudiation, detecting, data disclosure, unawareness, non-compliance.
Data minimization and privacy by design.

## How to

1. Classify personal fields: what, why, where stored, who reads, how long.
2. Trace every copy: replicas, caches, exports, logs, backups, vendors.
3. Define deletion and export paths that reach each copy.
4. Tier 2: walk the LINDDUN categories per data flow and record a control
   or accepted risk for each.

## Checks

- Deleting a user removes their data from every listed copy (or the
  backup expiry is documented).
- Logs and fixtures contain no personal fields (scan).
- Tier 2: LINDDUN findings each mapped to a control or an owner-accepted
  risk.
