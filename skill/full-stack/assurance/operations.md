---
discipline: operations
triggers: [schema or data changes, operated by others or unattended]
tier2_when: [many users, stated availability target, irreversible data changes]
---

# Deployment and operations

## Policy

- Tier 1 when any trigger holds; tier 2 for many users, availability
  targets, or irreversible data changes.
- Default: configuration from the environment; a rollback path stated
  before rollout; schema changes are expand, migrate, then contract.
- Never: secrets in configuration files under version control; a
  destructive migration without a tested restore; deploys beyond the task's
  authorization.

## Framework

Twelve-Factor configuration. Expand–contract schema migration. DORA's four
key metrics (deployment frequency, lead time, change failure rate, time to
restore) as the outcome measures. Backup is only as good as the last
restore test.

## How to

1. List what the change deploys: code, schema, configuration, data.
2. For each, state how it rolls back and in what order.
3. Make migrations reversible or split them expand-then-contract.
4. Name required configuration and where it comes from.
5. Tier 2: staged rollout with a health gate, and a restore drill for the
   affected data.

## Checks

- Migration up, then down (or contract skipped), on a copy succeeds.
- The app starts from environment configuration alone.
- Tier 2: restore from backup verified; rollout health gate defined and
  exercised in staging.
