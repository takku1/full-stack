---
layer: platform
decides: [hosting model, packaging (container, binary, function, static), environments, CI/CD pipeline, configuration and secrets delivery, scaling model]
constrains: [runtime, data, interface, client]
criteria: [fit to scaling and availability scenarios, operational burden for this team, cost at present and future load, lock-in and exit cost, compliance and region needs, maturity]
evidence: [documented service limits, pricing page checked with date, regions, support for required runtimes and connection types]
tags: [long-lived-connections, serverless-functions, ephemeral-filesystem, persistent-volumes, horizontally-scaled-instances, single-instance, static-hosting-only, container-runtime, managed-database, edge-runtime, on-premises]
---

# Platform layer

Decides where the system runs, how it is built and shipped, and how it
scales. This is usually the most costly choice to reverse.

## Establish first

1. **Existing infrastructure**, accounts, and operations skills. Running
   one more platform is a standing cost.
2. **Availability and scaling scenarios**: expected load, peaks, recovery
   time and data-loss targets, regions.
3. **Workload needs**: long-lived connections, background jobs, scheduled
   work, local disk, GPU, startup latency.
4. **Compliance**: data residency, audit, and certification needs.
5. **Delivery path**: how a change goes from commit to production, who
   approves, and how it rolls back.

## Choosing

Prefer what the team already operates. For a new small system, one
managed instance or container with a managed database is the boring
default; serverless fits spiky, stateless work; Kubernetes and multi-region
need a scenario that demands them. Always define rollback before rollout.

## Traps to check

- Serverless or edge functions with long-lived connections, local files,
  or connection-per-request databases.
- Several instances sharing an embedded single-writer database.
- Secrets in the repository or build logs.
- No staging or preview environment for a change that needs one.
- A pricing model that breaks at one of the brief's futures.

## Neighbor assumptions to record

Runtimes and versions it must support, connections and storage the data
layer needs, transports the interface uses, and hosting the client needs.
