---
discipline: maintainability
triggers: [new boundary or dependency to protect]
tier2_when: [shared library or public contract, long-lived system, several teams]
---

# Maintainability and evolution

## Policy

- Tier 1 when the design draws a new boundary or adds a dependency; tier 2
  for public contracts or long-lived shared code.
- Default: protect each boundary the design draws with an automated check;
  every new dependency is maintained, licensed, and pinned.
- Never: a boundary that exists only in a diagram; a dependency added for
  one function the standard library already has.

## Framework

Fitness functions (Ford, Parsons, Kua, Sadalage): automated tests,
metrics, or checks that protect an architectural property and run in the
project's pipeline. Information hiding (Parnas) for where to draw the line.

## How to

1. Name the property the design must keep (for example "the client never
   imports the data layer", "the public API stays backward compatible").
2. Express it as the cheapest automated check: an import rule, a contract
   test, a schema diff, a dependency audit.
3. For each new dependency, record maintenance, license, and why it is
   needed.
4. Tier 2: a compatibility test against the previous public version and an
   upgrade path for the riskiest dependency.

## Checks

- The fitness function runs in the project's checks and passes.
- New dependencies are pinned in the lockfile, with license recorded.
- Tier 2: backward-compatibility test against the last released contract.
