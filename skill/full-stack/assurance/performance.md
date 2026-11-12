---
discipline: performance
triggers: [availability or latency target]
tier2_when: [stated throughput or latency target at scale, a brief future of tenfold load]
---

# Performance

## Policy

- Tier 1 only when a quality scenario states a latency, throughput, memory,
  or startup target; tier 2 when the target is at scale.
- Default: measure before optimizing; the measure comes from the scenario.
- Never: claim "fast" without a number; optimize code no measurement
  implicates; invent a target the user did not state (mark it proposed).

## Framework

Quality-attribute scenarios (stimulus, environment, response, measure), as
in the stack brief. Performance budgets per user task. The USE method to
locate saturation.

## How to

1. Copy each performance scenario from the brief with its measure.
2. Identify the operation that dominates it and its expected volume.
3. Write a benchmark or timing check at the stated load.
4. Tier 2: load test at the stated volume and at the brief's tenfold
   future; record where saturation appears.

## Checks

- A benchmark or timing check meets each scenario's measure.
- Tier 2: load test results at stated and tenfold volume, with the
  saturated resource named.
