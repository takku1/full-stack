# External review of package 0.5.0 (2026-11-12)

A summary of a second external review, of commit `91ce4e4`, supplied by the owner. The ratings are the reviewer's qualitative assessment, not benchmark results. An earlier review of the same day covered 0.4.0 ([first review](review-2026-11-12-external.md)). Code-level guard findings from between the two reviews are in the [FS-023 results](../../evals/results/plugin-smoke-2026-11-12.md).

## Verdict

Architecture and modularity: strong. Engineering-discipline coverage: much improved. Plugin operation on Windows: smoke-tested. Assurance effectiveness: not yet proven. The remaining step is proving that module selection improves real software, not adding layers.

## Strengths noted

- The twelve-question screen with tiers loads only the raised modules.
- The security module is specific: trust boundaries, object-level authorization, injection, secrets, abuse cases, STRIDE, ASVS.
- Assurance claims end in executable checks that feed the run guard.

## Challenges and dispositions

| Challenge | Disposition |
|---|---|
| The screen is applied by the model, not a deterministic resolver with module dependencies, conflict detection, and interchangeable providers | Recorded as FS-027, frozen until FS-016 shows the model misapplies the screen. The reviewer's reference to a "Hitch-style composition system" points to a discussion outside this repository's record; it is noted, not interpreted here |
| An executed check is not necessarily a meaningful check: the guard verifies exit codes, not that the command tests the claim (for example a passing `GET /users/me` proves nothing about another user's record) | Added to FS-016 as "check meaningfulness": does the agent's check fail when the planted defect is present |
| Twelve fixed questions can miss implicit risk, such as a local tool that runs untrusted plugins or reads confidential files | Added to FS-016 as a screen-recall case; capability-based screening is part of FS-027 |
| `docs/STATUS.md` still called FS-015 a 0.4.0 trial and said the plugin had not been loaded live | **Fixed**: FS-015 now targets 0.5.0 including assurance; D-019 and FS-005 lines updated to reflect FS-023 |

## Recommendations adopted

- No new modules. Next: FS-015, then FS-016 with the 0.5.0 assurance cases.
- A flawed multi-tenant application with a planted authorization hole and an unsafe retry path, given to plain, the brief, 0.4.0, and 0.5.0, scored on detection, fix, and unneeded infrastructure. Added to FS-016.
