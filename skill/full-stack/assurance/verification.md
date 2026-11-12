---
discipline: verification
triggers: [any build request, multiple users or tenants, money or irreversible actions]
tier2_when: [money, health, safety, regulated data, a module others depend on]
---

# Verification

## Policy

- Tier 1 for every build request; tier 2 for high consequence.
- Default: every requirement and every assurance claim maps to at least one
  executed check, including its failure path.
- Never: report coverage as evidence of correctness; mock the boundary the
  outcome is about; call a check passed that did not run.

## Framework

Risk-based testing (test where failure costs most). Test layers by risk:
unit for logic, contract tests at boundaries whose sides release
separately, integration and end-to-end for the outcome's real path.
Mutation testing as test-quality evidence, since coverage can be 100% while
catching almost nothing. Property-based tests for invariants.

## How to

1. List the outcome's requirements and the assurance table's claims.
2. For each, name the cheapest check that would fail if it were false:
   success path, each failure, and restart when state persists.
3. Prefer the project's existing test tools and layout.
4. Run all checks in one `run_guard.py checks` call.
5. Tier 2: run mutation testing on the critical module and add property
   tests for its invariants; report the mutation score, not coverage.

## Checks

- Each requirement and claim has a named check that ran.
- Failure paths are exercised, not only success.
- Persistence is checked across a process restart when required.
- Tier 2: mutation score on the critical module reported, with surviving
  mutants either killed or justified.
