# Field report 5: SkillWren 0.11 pipeline check, building in MochiOS with 0.9.0 (2026-11-20)

Follows [field report 4](field-report-2026-11-19-mochios-4.md). The owner's pipeline check for a SkillWren change: rebuild Full Stack on the new SkillWren (tier 1), use it to build in MochiOS (tier 2), then feed what the build showed back into each tier (tier 3). One session, one model (Opus 5.5, Claude Code on Windows 11), author-scored, no comparison arm. It counts toward **FS-003** and **FS-010**, not FS-016.

**Verdict.** Adopting SkillWren 0.10's exclusion rules found a real defect on paper: the 0.8.3 flows filed the design note before the guarded run started, the F-4 collision, while the prose already said the opposite. The MochiOS build then ran end to end on 0.9.0 (ledger `valid, complete`, package line matched), and exposed two guard defects that cost a restart. Both are fixed here with tests.

## Tier 1: Full Stack on SkillWren 0.10 to 0.11

| Step | Result |
|---|---|
| 0.8.3 unchanged on the new SkillWren | 98 tests pass, four flows clean, `skillwren build` 0 warnings. Nothing new exercised |
| Exclusion rules added to `implement.md` | SkillWren reported P3 twice: `run design` reached `write design with design_docs` (design.md) and `write table with design_docs` (assurance.md) before `exec guard start`. The hint named both statements and said to do them after `start` |
| Restructure (D-025) | `design` returns with a filing mark; new `deliver` flow files design-only work; `assurance` checks a scratch `table_draft`; `implement` files the note after `start`. Flows clean; three P3 mutants added |
| Package binding and load record | Guard ledger bound to its own package; hook records the loaded tree. Opt-in `fullstack.requireSkill` |

## Tier 2: the MochiOS build

| Item | Value |
|---|---|
| Package | 0.9.0 from `Z:\full-stack` (branch `skillwren-0.11`). The host's installed plugin was 0.8.3, so the session read the 0.9.0 skill directly and recorded the load by feeding the 0.9.0 hook a Skill event for this session: a simulated host load, reported as such |
| Pick | Field report 4's open item: outcome 3 (abandoned) printed on only one of two native boots |
| Diagnosis | The "timing dependency seen in run `75a7dc`" was wrong: that run's failing check was a PowerShell parse error, not a missing outcome. The real cause: every `WAIT_BLOCK` one-shot marker set its once-flag *before* a `try_lock` on COM1, so a busy port lost the line for the whole boot, and `CLOSED` printed while holding the Gate lock |
| Built | `mochios_kernel_pure::one_shot::mark_once` (flag claimed only when written, bounded retries); `object_wait.rs` prints markers after the Gate and queue locks drop. Event rows unchanged |
| Evidence | Reproduction failed first (helper missing), then 4 host tests pass; Gate and scheduler suites pass; two native `--run-chello` boots each printed all six markers with `CHELLO_EXIT exit_code=0`; `cargo xtask run` passed |
| Guarded runs | `20261120-135033-fd11a9` (finished with blockers, see R-1) and `20261120-135526-59aae5` (closed clean; ledger `valid, complete`; "Package: ... same tree as this run's scripts") |
| Not done | MochiOS commit: the tree holds about 400 uncommitted paths from other sessions (field report 4, F-9) |

## Findings

| # | Tier | Finding | Status |
|---|---|---|---|
| R-1 | Full Stack | The write set could not be widened. The fix belonged in `kernel-pure` (the kernel binary has `test = false`), which the design had not named, so the run was finished with blockers and restarted | **Fixed:** `run_guard.py widen` with start's collision rules (`test_widen_claims_a_path_found_mid_run`, `test_widen_keeps_starts_collision_rules`, `test_widen_refuses_another_open_runs_claim`) |
| R-2 | Full Stack | `assurance.py check` and the guard read every table in the declared file. A concept note with one dated section per delivery made IDs collide (renumbered to A-6..A-8) and made close demand fresh checks for the earlier section's A-1..A-5. The first `Screen:` line (the old section's) was also the one parsed | **Fixed:** `--section HEADING` on `declare`/`start` and `assurance.py check` (`test_section_scopes_the_assurance_table`) |
| R-3 | Full Stack | Restarting forced `--adopt` of this session's own note edit from the finished run; the guard cannot tell its own previous run's edits from someone else's | Removed in practice by R-1 (no restart needed); not otherwise changed |
| R-4 | MochiOS | Earlier docs blamed outcome 3 on timing based on a malformed check | Corrected in `wait-object.md` and `ROADMAP.md` |
| R-5 | SkillWren | P3's hint was enough to restructure three flows; the package line from the 0.10 load record was visible in a real close | Reported to SkillWren |
| R-6 | Host | The installed plugin (0.8.3) lags the branch, so the build could not use the real host load path | Release 0.9.0 and update the plugin before the next field run |

## Limits

One session, one subject, author-scored. The host load was simulated (R-6). Two native boots show no lost marker, not how often a busy port occurs. R-1 and R-2 are checked by unit tests and this report's reproduction, not yet by a fresh session.
