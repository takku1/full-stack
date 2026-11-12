---
discipline: cost
triggers: [hosted or paid infrastructure, paid APIs]
tier2_when: [usage-based pricing on a hot path, a brief future of tenfold load, a fixed budget]
---

# Cost

## Policy

- Tier 1 when the outcome adds or changes paid infrastructure or APIs;
  tier 2 for usage-based pricing on a hot path or a fixed budget.
- Default: estimate monthly cost at present load and at each future in the
  brief, from pricing pages checked now, with the date.
- Never: a price from memory; an unbounded usage-based call in a loop or
  retry path without a cap.

## Framework

The cost pillar of the AWS Well-Architected Framework (measure, attribute,
right-size). The brief's futures and the regret column for lock-in and
exit cost.

## How to

1. List each paid resource or API the outcome uses and its pricing unit.
2. Estimate units per month now and at each future; multiply by today's
   price, citing the page and date.
3. Name the cost driver and any cap, quota, or alert.
4. Tier 2: a budget alert, and a usage cap on calls in retry or fan-out
   paths.

## Checks

- A cost table (resource, unit, volume now and at each future, price,
  source, date) is in the design.
- Tier 2: budget alert or quota configured; a test shows retries cannot
  multiply paid calls without bound.
