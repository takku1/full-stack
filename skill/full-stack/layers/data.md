---
layer: data
decides: [data model, storage engine, schema and migration approach, consistency and durability model]
constrains: [runtime, interface, platform]
criteria: [fit to access patterns and volumes, consistency and durability needs, operational burden, team familiarity, maturity, license, cost]
evidence: [current release and date, maintenance activity, license text, documented limits for the scenarios]
tags: [transactional-writes, relational, document-model, key-value, local-replica, embedded-single-writer, multi-region-replication, conflict-resolution, full-text-search, time-series, local-file-store, requires-persistent-connections, serverless-safe-connections]
---

# Data layer

Decides where state lives, who may write it, and what it guarantees. Start
from the domain, not the product.

## Establish first

1. **Entities and authority**: each entity, its single authoritative owner,
   and its writers. A cache or replica never gains authority by copying.
2. **Access patterns**: reads and writes per entity, query shapes (by key,
   by range, ad hoc, full-text, aggregate), and expected volumes now and in
   each future.
3. **Guarantees per scenario**: which writes must be atomic together, what
   may be stale and for how long, what must survive a crash, and what
   happens on concurrent edits (reject, last-writer-wins, merge).
4. **Lifecycle**: retention, deletion obligations, backup and restore
   targets, and how the schema changes over time.
5. **Existing stores**: what already exists, who owns it, and whether the
   outcome can use it through its boundary.

## Choosing

Choose the model class first (relational, document, key-value, embedded,
log or time-series, search index), then a product within it. A relational
store with transactions is the boring default for multi-entity business
data. Add a second store only for a scenario the first demonstrably cannot
meet, and name which store is authoritative for each entity.

## Traps to check

- Two stores both treated as the source of truth for one entity.
- Offline or multi-device clients without a defined conflict policy.
- Schema migrations without a rollback or expand-then-contract path.
- An embedded single-writer store on a platform that runs several
  instances, or a file store on an ephemeral filesystem.
- Connection-per-request databases behind serverless functions without a
  pooler or HTTP access.
- Personal or regulated data without retention, deletion, and encryption
  decisions (coordinate with crosscut).

## Neighbor assumptions to record

What the runtime needs (a maintained driver or client, migration tooling),
what the interface exposes (pagination, versioning, sync), and what the
platform must provide (persistent volumes, managed backups, regions).
