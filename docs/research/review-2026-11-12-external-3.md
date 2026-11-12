# External review of package 0.6.0 (2026-11-12)

A summary of a third external review, of commit `9dc25fe`, supplied by the owner. The reviewer read the committed source and tests but did not run them. Ratings are the reviewer's qualitative assessment, not benchmark results. Earlier reviews: [first](review-2026-11-12-external.md) (0.4.0), [second](review-2026-11-12-external-2.md) (0.5.0).

## Verdict

| Property | Reviewer's rating |
|---|---|
| Rule-based discipline selection | Implemented |
| Module dependency resolution | Implemented |
| Assurance declaration | Implemented |
| Assurance-before-build ordering | Not enforced |
| Assurance evidence validity | Partial |
| Live 0.6.0 verification | Not yet demonstrated |

0.6.0 enforces that an assurance declaration exists and that some checks ran. It does not yet guarantee that the declaration was valid, made in time, or backed by passing, relevant evidence.

## Findings

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | High | The guard parses the table but does not run `check_table()`, so a raised discipline with no row, an unraised row, a row without a check, a duplicate ID, or a missing Screen line all pass `close` | Fixed in 0.7.0 ([D-022](../design-decisions.md#d-022-tighten-assurance-enforcement-and-pressure-test-the-rules-package-070)) |
| 2 | High | Assurance is enforced at `close`, not before code: start undeclared, write the code, write the table, close | Fixed in 0.7.0 for tool edits: the PreToolUse hook blocks edits until assurance is declared. Shell writes cannot be blocked; a declaration made after changes is recorded and blocks `close` |
| 3 | High | `--routine` is unrestricted and `declare --routine` can replace an assurance table | Fixed in 0.7.0: `--routine` needs a reason, which is reported; a downgrade from a table needs `--override`. Whether agents misuse it is for FS-016 |
| 4 | Medium-high | A check is linked to a row by matching its ID in the criterion text, and any earlier passing check counts | Partly fixed in 0.7.0: checks store the assurance IDs they name, and the latest check per ID must pass. Whether a check tests its claim remains for FS-016's planted defects |
| 5 | Medium | Tier 2 pending evidence does not block `close`; the Markdown label is trusted | Fixed in 0.7.0: a tier 2 row needs a passing executed check, and `documented` no longer exempts it. The report shows declared and executed evidence separately |
| 6 | Medium | `finish` bypasses all gates | Fixed in 0.7.0: `finish` applies the same gates as `close` |

Also noted: `report --all` gives run-level summaries, not file-level provenance. Accepted for now.

## Strengths noted

- The resolver is small, requires every answer, treats unknown as yes, closes over dependencies, and explains what raised each discipline.
- The rules are data (`rules/assurance.json`), not prompt text.
- `report --all` makes a benefit found by accident in MochiOS reusable.

## Reviewer's recommendation

Keep the next patch narrow, write a failing regression test before each fix, and add negative tests (missing screen, missing discipline, duplicate IDs, tier 2 pending evidence). The existing tests mostly cover the happy path.
