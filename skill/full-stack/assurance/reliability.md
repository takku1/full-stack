---
discipline: reliability
triggers: [money or irreversible actions, availability or latency target, schema or data changes, external calls]
tier2_when: [money, health, safety, stated availability target, many users]
---

# Reliability

## Policy

- Tier 1 when any trigger holds; tier 2 for high consequence or a stated
  availability target.
- Default: every external call has a timeout; every retried write is
  idempotent; every multi-step change has a defined partial-failure state.
- Never: unbounded retries; retrying non-idempotent writes; a failure that
  leaves state that no component owns.

## Framework

Google SRE: service level objectives and error budgets. Nygard's stability
patterns: timeouts, retries with backoff, circuit breakers, bulkheads,
idempotency keys. FMEA-style failure listing (what fails, effect,
detection, response).

## How to

1. List each external call, write, and multi-step operation in the outcome.
2. For each, record timeout, retry policy, idempotency, and the state after
   a failure at each step; name the component that recovers it.
3. Decide behavior when a dependency is down: fail, degrade, or queue.
4. Tier 2: write an SLO (indicator, target, window) and an error-budget
   rule; add fault-injection tests for the critical path.

## Checks

- A slow or failed dependency produces the designed outcome, not a hang.
- A replayed write (lost response, client retry) applies once.
- A restart mid-operation leaves recoverable, owned state.
- Tier 2: fault-injection test on the critical path; SLO measurable from
  existing signals.
