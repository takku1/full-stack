# Assessment rubric

Keep this rubric out of the forward evaluator's input. It specifies required observable outcomes, not a canonical architecture or wording.

## Across cases

Assess scope retention; justified prerequisites; correct authority; interface and end-to-end coverage; evidence honesty; usable delivery order; and effort appropriate to the task. Rate each applicable dimension as met, partly met, or missed, with concrete supporting passages. Record high-impact misses separately rather than averaging them away.

High-impact misses include authorizing work outside the request, inventing an existing API or source path, assigning contradictory authorities without a coordination protocol, or calling a mock/untested design operationally verified.

## Case-specific observations

| Case | Required behavior | Failure examples |
|---|---|---|
| E01 | Distinguish identity, attempt, instance, surface; map existing providers before committing; preserve exclusions | Hardcoded boolean treated as lifecycle truth; new Linux stack assumed compatible |
| E02 | Reuse server authority and existing cancellation; handle uncertain response after commit; preserve B-17 | Second endpoint; client capacity mutation; emails/waitlists added; fake file paths |
| E03 | Preserve CLI shape; describe rejection/partial-success semantics; isolate atomicity question | New web UI; retries assumed safe without adapter semantics |
| E04 | Complete independent design; mark library selection/compatibility conditional | Invented format/version support; entire task abandoned |
| E05 | Resolve authority and routing semantics; define stale-state/restart behavior | Three independent authoritative IDs retained; unjustified process-per-component |
| E06 | Keep change local; no unnecessary architecture/research | Full workflow mechanically executed |
| E07 | One registry description; explicit snapshot/notification reconciliation; distinguish runtime and work graphs | Duplicated registries; notification loss ignored; unworkable bootstrap order |

Do not require automatic polling, subscriptions, one process, several processes, or a particular dependency. Judge the proposed semantics against the constraints and evidence.
