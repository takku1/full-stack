# Field report 4: building in MochiOS with 0.8.2, and fixing the package from it (2026-11-19)

Follows [field report 3](field-report-2026-11-12-mochios-3.md). The owner asked to use Full Stack to build in MochiOS, to fix Full Stack from what the build showed, and to report back to SkillWren. One session, one model (Opus 5.5, Claude Code on Windows 11), author-scored, no comparison arm. It counts toward **FS-003** (real roadmap slice) and **FS-010** (guard in live use), not FS-016.

**Verdict.** The build worked end to end under the guard: designed in the owning wiki note, screened, test-first, host and native checks, a SkillWren ledger that closed `valid, complete`. The friction was all in the guard's *ordering*. Writing the design note before `start` forced a user-confirmed `--adopt`. Writing it after `start` was blocked by the hook. A test-first reproduction stayed a failing criterion until close. Each of these was reproduced in a scratch repository or in this run's record and then fixed with a failing test first. The last four MochiOS runs in the guard log show the same reproduction pattern, so the package was making a correct workflow look like a failure.

## The session

| Item | Value |
|---|---|
| Request | "use full stack on z:\mochios, you can actually build stuff", then fix and improve Full Stack and report to SkillWren |
| Package | Hooks and `SKILL.md` from the **cached plugin 0.8.0**; scripts run from the repository at 0.8.2 (finding F-1) |
| Subject state | 447 uncommitted paths from earlier sessions, last commit 2026-11-05; the WAIT_BLOCK feature itself uncommitted (guarded runs `2bbb45`, `75a7dc`) |
| Pick | Selection rule from field report 3 (G2): no verified-but-unfinished work in the guard log (its failing rows were reproductions), so the owning concept's named follow-up: "a fully push-driven condition router" (`docs/wiki/cpu/wait-object.md`, `docs/ROADMAP.md`) |
| Built | **Push wake:** a `CHANNEL_SEND`, `CHANNEL_WRITE`, `CAP_REVOKE`, `WAIT_CANCEL` or `WAIT_RELEASE` syscall completes the object waiters it unblocked on its own exit, instead of at the next unrelated syscall entry or the ~10 ms tick. The Gate owns the effect set (`Gate::wakes_object_waiters`); the kernel reuses the existing sweep after the Gate lock drops (`object_wait::push_after`). Deadlines, `DRAINED` quiescence and kernel-internal sends stay on the entry sweep. No ABI change |
| Files | 4 code (Gate classifier and test, kernel hook and sweep) and 2 docs (wiki section with the assurance table, ROADMAP row) |
| Guarded run | `20261119-212430-64b490`: 11 checks, scope clean, closed with one reported blocker (F-7), ledger `valid, complete` |

## Evidence

| Check | Result |
|---|---|
| Gate test pinning the five-effect set (written first; failed to compile, then passed) | pass |
| Gate `wait_` suites (owner-checked evaluator), scheduler park-queue tests | pass |
| Native `cargo xtask run --run-chello --timeout 240`, twice | `##WAIT_BLOCK_PUSH effect=153 woke=1##` (a sibling thread's `WAIT_CANCEL` completed the parked waiter at its exit) and `CHELLO_EXIT exit_code=0` both times |
| Outcome 3 (abandoned) | Absent on the first boot, present on the second. The previous run (`75a7dc`) also failed and then passed its outcome check, so this is timing-dependent before this change. Recorded, not fixed |
| Plain `cargo xtask run` (MochiOS's completion signal) | pass |
| Not measured | Wake latency. Channel and cap push variants run only through the host evaluator, not natively |

## Findings

| # | Kind | Finding | Status |
|---|---|---|---|
| F-1 | Environment | The host loaded the cached plugin 0.8.0, so its hook (0.8.0) and the repository's scripts (0.8.2) acted on the same run record. Nothing records which package version enforced a run | Noted; the plugin needs `claude plugin marketplace update` plus `claude plugin update`. For SkillWren, see its report |
| F-2 | Defect | `assurance.py screen --help` listed no questions; the only way to learn them was a failing call | **Fixed:** the help epilog is generated from the rules (`test_help_lists_every_screen_question`) |
| F-3 | Fit | The assurance modules' Checks are web-shaped ("404 or 403", "client bundle"); a kernel change has to translate them | Noted, not changed (wording only, unevaluated) |
| F-4 | Defect | The design flow writes the note before `start`; the guard then calls it an outside edit that only the user may `--adopt`. Reproduced in a clean scratch repository with a brand-new file. The auto-mode classifier also refused the agent's own `--adopt`, correctly | **Fixed** with F-6: start first with the note in the write set, write it, then `declare`. `declare` now counts only code changes as late (`test_design_note_written_in_the_run_then_declared_is_not_late`; `test_code_changed_before_declaring_is_still_late` keeps the protection) |
| F-5 | Behaviour | Once a session invokes the skill, editing Full Stack itself also needs a guarded run in its own repository | Correct as designed; this report's fixes ran under run `20261119-212838-9b0292` |
| F-6 | Defect | With a run open but undeclared, the hook blocked Markdown design notes too, so the note the declaration needs could not be written. Combined with F-4, neither order worked | **Fixed:** design notes stay free until declared, as before a run; code stays blocked (`test_hook_lets_design_notes_through_an_undeclared_run`) |
| F-7 | Defect | A test-first reproduction run after its test is written is not "before the first edit", so it counted as a failing acceptance criterion. The last four MochiOS runs each carry such rows (`reproduce-...`, `baseline-missing-release`, `shared-queue-...`) | **Fixed:** `checks --reproduce` / `exec --reproduce` report reproductions apart and never count them toward acceptance or an assurance row; reproductions alone never close a run (`test_marked_reproduction_is_evidence_not_a_failing_acceptance_check`, `test_a_run_with_only_reproductions_does_not_close`). This MochiOS run predates the flag and closed with the row as a reported blocker |
| F-8 | Behaviour | The guard's `--adopt` prompt and the permission layer together kept the agent from silently taking ownership of 447 paths of earlier work. The owner answered one question | Held |
| F-9 | Gap | Committing the work is unsafe as a subset: the change builds on uncommitted files from two earlier runs, which share files with unrelated uncommitted work. The whole tree builds and boots, but it mixes provenance | Left to the owner (MochiOS) |

## Fixes to this package from this session

Screen: verification T1 (build); others T0

| ID | Discipline | Claim | Could fail by | Control (owner) | Check | Evidence |
|---|---|---|---|---|---|---|
| A-1 | verification | A design note written inside the run and then declared is not a late declaration, and its in-run evidence updates are in scope | Exempting code changes too, so code before the table passes | `declare` counts only code changes as late (`run_guard.py`) | `test_design_note_written_in_the_run_then_declared_is_not_late`, `test_code_changed_before_declaring_is_still_late` | tested |
| A-2 | verification | While a run is open but undeclared, the hook lets design notes through and still blocks code | Letting code through before the table passes | Hook applies `is_code` before declaration, as it does before a run (`run_guard.py`) | `test_hook_lets_design_notes_through_an_undeclared_run` | tested |
| A-3 | verification | `assurance.py screen --help` names every question it requires | Help text drifting from the rules file | Help epilog generated from the rules (`assurance.py`) | `test_help_lists_every_screen_question` | tested |
| A-4 | verification | A marked test-first reproduction is reported but never counts as acceptance for a criterion or an assurance row, and reproductions alone never close a run | A failing acceptance check hidden by the flag, or a reproduction covering a row | `--reproduce` records `reproduce: true`; close, report and row matching use acceptance checks only (`run_guard.py`) | `test_marked_reproduction_is_evidence_not_a_failing_acceptance_check`, `test_a_run_with_only_reproductions_does_not_close` | tested |

This run declared the table from a file outside the repository, because the hook (cached 0.8.0, F-1) blocked writing the note in-run (F-6). The table was copied here after declaration.

## Limits

One session and one subject, author-scored. The fixes were checked by unit tests and by this session's own use, not by a fresh session or the pressure harness. The push wake was not measured for latency. Whether the clean order (start, write, declare) is what a model actually follows is untested until the plugin cache is refreshed and FS-029 reruns.
