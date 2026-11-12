# Field report 3: package 0.5.0 building in a live repository (2026-11-12)

Follows [report 1](field-report-2026-10-03-mochios.md) and
[report 2](field-report-2026-10-03-mochios-2.md). Those used 0.2.0/0.3.0 on
design-only requests. This is the first report on **0.5.0 used to build**, in
a large existing repository (MochiOS, a Rust kernel and OS) and on the
plugin form (`/full-stack:full-stack`). It also uses the repository's own
guard history as data: 60 guarded runs recorded since 2026-10-05 in
`.git/full-stack-runs/`. It counts toward **FS-003** (real roadmap-slice
pilot) and **FS-010** (guard in live use), not FS-016. There was one
session, one model, no comparison arm and author scoring, so it shows how
the skill behaves in use, not whether it beats an alternative.

**Verdict.** The core rules and the guard did what they are for, in a
messier situation than any eval fixture. The prompt was a one-line
"continue building", the tree had 289 uncommitted files from earlier
sessions, and the target was a kernel slice that ends in a QEMU boot. The
guard log had a benefit nobody designed for: it let a fresh session learn
which of that uncommitted work had actually been verified, without
trusting anyone's memory. Four guard or script defects and three gaps were found (below). D1 and D3
were reproduced in this session. The design and assurance flows
were applied lightly, and the assurance screen was applied *after* the code
was written. That reversal of the order is recorded as a process failure,
not hidden.

## The session

| Item | Value |
|---|---|
| Request | "lets use the new full-stack set up and continue building mochios" (no outcome, no criteria) |
| Package | 0.5.0 plugin, Claude Code on Windows 11, Opus 5.5 |
| Subject | MochiOS: Rust workspace, ~300 crates, Recurspec-style `docs/architecture` + wiki checklists + `docs/ROADMAP.md`; project `CLAUDE.md` forbids new doc files and names `cargo xtask run` (QEMU boot) as the completion signal |
| Starting state | 289 modified/renamed files, last touched 9 h earlier, no running processes |
| Outcome built | `WAIT_BLOCK` completion rows: every blocking wait closes with one hash-chained event-log row (delivered / refused / abandoned), so the audit log records how a wait ended, not just that it was admitted |
| Write set | 7 files + shared `ROADMAP.md`: wire-abi row shape, Gate recorder, Gate test, scheduler park queue, two kernel files, wiki evidence |
| Guarded run | `20261112-051853-75a7dc` |

## What the skill did, step by step

| Step (skill text) | What happened | Judgement |
|---|---|---|
| Restate outcome, exclusions, checks; ask only if underivable | Outcome could not be derived from "continue building". One question: finish the WIP / new slice / another session owns it. The user answered "you pick". | Right call. A single question with three options was enough. |
| Read code and instructions before deciding | Read STATUS, ROADMAP open rows, git state, process list and file mtimes before choosing. | Worked, but expensive (see G3). |
| Leave uncommitted edits you did not start untouched | The tree held 289 dirty files. No edits were made until the session confirmed nothing was running and the edits were stale. Taking over the WIP was then the chosen work, recorded with `--adopt`. | The rule forced the right check (are these someone else's live edits?). |
| "In an existing repository every layer starts as keep current" | No stack flow ran, because no technology choice existed. | Correct, with zero overhead. |
| Discovery never authorizes extra work | Noticed but not built: a 2× row volume per call, the wiki's other open items ("push-driven condition router", formal proofs), and committing the WIP. | Held. Committing was left to the user per host rules. |
| Prefer one real end-to-end path over mocks | Acceptance included a native QEMU boot that exercises all three outcomes, not only host unit tests. | The project already demanded this; the skill agreed with it. |
| Implement flow: write set → checks → close | `run_guard.py start / checks / close`. The start collision detection fired correctly on the 7 adopted files. | Worked; defects D1, D3, D4. |
| Assurance screen before design | **Applied after implementation.** See below. | Process failure (G1). |
| Design filing | The design stayed in chat plus the owning wiki section, because the project forbids new doc files. The design flow's filing rule allows exactly this. | Correct. |

## Assurance, as applied

Screen (applied late, from the request and code):

| Question | Answer | Raises |
|---|---|---|
| Trust boundary? | Yes, ring-3 → kernel syscall | security, observability |
| Several principals kept separate? | Yes, rows carry the owning principal | security, verification |
| Persistent data changed? | Yes, new rows in a persisted, chained log (existing schema) | reliability, operations |
| New boundary to protect? | Yes, row byte layout read by verifiers | maintainability |
| Personal data, money, SLO, external calls, UI, regulation, paid infra | No | none |

| ID | Discipline | Claim | Could fail by | Control (owner) | Check | Evidence |
|---|---|---|---|---|---|---|
| A-1 | security | A completion row names the principal that parked, never another | Kernel uses a different principal at reclaim | Key stores the owner at park time (kernel object queue) | Gate test asserts `principal`; native path | tested (host) / inferred (native) |
| A-2 | verification | All three outcomes occur on real hardware paths | A path never runs in the probe | Native C++ probe: timer, release while parked, parked sibling exit | `xtask run --run-chello` + serial grep for `outcome=1/2/3` | tested (native: `outcome=1/2/3`) |
| A-3 | reliability | Each call closes exactly once | A consumed entry is later reclaimed as abandoned | `take` removes the entry; reclaim returns only remaining keys (park queue) | Park-queue tests on returned keys | tested (host) |
| A-4 | reliability | No log flood | Sweep re-emits per tick | Emit only on removal; ≤1 closing row per admitted call | Plain boot regression; reasoning | tested (plain boot passed) / inferred (bound) |
| A-5 | maintainability | Admission and completion rows are distinguishable without ordering | Tag byte collides with snapshot bytes | Tag at byte 24, admission leaves it zero (wire-abi) | wire-abi row test | tested |

The screen added no control the code lacked, because the flood concern
came from the project's own `CLAUDE.md` history of audit-log floods. It did
add a documented row for each claim, and it showed that A-1's native half
rests on reasoning. Applied first, as the flow intends, it would have cost
nothing extra and would have shaped the native check list from the start.

## Findings

### D1: `run_guard.py start --adopt` silently drops all but the last flag (reproduced)

`--adopt`, `--write-set` and `--shared` use `nargs="+"` without
`action="extend"`, so the repeated form `--adopt a --adopt b --adopt c`
keeps only `c`. Observed: with seven repeated `--adopt` flags, `start`
reported six collisions (every path but the last) and refused. Passing one
`--adopt a b c …` list worked. The refusal is safe, but the message ("rerun
with --adopt PATH") invites exactly the repeated form. The same holds for
`--write-set`, where silently narrowing the claimed scope *is* unsafe: a
later edit outside the narrowed set would be reported, but against the
wrong claim.
**Fix:** `action="extend"` on all three arguments (Python ≥ 3.8, already
the floor), plus a test in `evals/test_run_guard.py`.

### D2: the flows never say how to call the scripts on Windows

`implement.md` writes `run_guard.py start …`. On this host `python` is the
Microsoft Store alias (exit 49), and only `py -3` works. The hook already
probes `python3`/`python`/`py -3` (FS-015 D6). Manual calls get no such
help. **Fix:** one line in the core or `implement.md`: "invoke scripts with
the interpreter the hook resolved (`python3`, `python`, or `py -3`)", or
print the resolved launcher in the hook's session message.

### D3: `checks --each` loses inner quoting

`--each "<criterion> :: <command>"` hands the command to a shell without its
inner quotes. A PowerShell one-liner with quoted `-Pattern` strings ran as
`-Pattern ##WAIT_BLOCK_CLOSED outcome=$o` and died with a parser error
(exit 1). That is a false failure, and the reverse case (a quoted grep that
silently matches less and passes) is the dangerous one. The workaround was
a script file. **Fix:** document "put multi-token or quoted commands in a
script file", or accept `--plan checks.json` with an argv array (the plan
form exists, but its quoting rules are not stated in `implement.md`).

### D4: inserting next to a protected shared hunk counts as changing it

The shared-file protection compares hunks by line position, so an insertion
at the boundary of another session's uncommitted hunk is reported as "changed a
pre-existing edit" even when the protected lines are byte-identical. That
is safe (it errs towards reporting), but in a registry that every session
appends to at the same place, it will recur. **Fix:** compare the protected
hunk's content, not its line span, before reporting. In the meantime, the
report should say "adjacent to" when the content is unchanged.

### G1: the assurance screen is easy to skip when design is light

The core routes "any design or build beyond a routine edit" to
`assurance.md`. But when the design was small and stayed in chat, no step
stopped implementation before the screen ran. The design flow's `verify
design has … assurance …` gate only fires when the design flow itself runs
end to end. FS-015 saw the same skip on a greenfield task, so this is now
two of two live builds. **Fix candidates:** make `run_guard.py start`
accept `--screen "<one line per raised discipline>"` and refuse without it
for non-routine work, or have `checks` warn when no check is labelled with
an assurance ID. FS-027 (deterministic resolver) is the frozen larger
version.

### G2: "continue building" has no selection rule

The skill handles an ambiguous outcome by asking. When the user then says
"you pick", nothing in the package says how to pick. The choice here
followed a sensible order (in-flight work first, then the owning concept's
named open follow-up), but that order was improvised. **Fix:** two lines in
`references/existing-projects.md`: when asked to continue, prefer (1)
verified-but-unfinished work in the registry or guard log, then (2) the
next open item named by the owning concept or contract, then (3) the
registry's highest-priority open row; state the pick and why.

### G3: orientation cost in a large repository

Before the first edit, the session spent about ten tool calls on status,
roadmap, git state and run logs. Two outputs overflowed the host limit (a
34 KB STATUS read and CRLF warnings across 289 files). The core's
"spend few turns" rule helped (batched reads) but cannot shrink a 1,000-row
roadmap. This is subject cost, not skill cost. One cheap aid is noted
under *What the guard log is worth*.

## What the guard log is worth (FS-010 evidence)

Aggregated over every run in `.git/full-stack-runs/` (2026-10-05 →
2026-11-12, including this one):

| Measure | Value |
|---|---|
| Guarded runs | 60 (49 in October, 11 in November) |
| Closed / left open | 58 / 2 (this run closed after the native checks) |
| Runs closed with zero checks | 6, all from before the FS-023 fixes or same-label restarts |
| Checks recorded | 207, of which 54 exited non-zero |
| Native QEMU boots among checks | 46 (13 failing), 7.3 h of 10.5 h total check time |
| Runs whose first check *failed* (reproduce before fix) | 16 |
| Runs that adopted pre-existing edits / declared shared files | 9 / 54 |
| Write-set size, min / median / max | 1 / 5 / 28 files |

Observations:

- **The log served as a handoff record, which was not in the design.** The
  289-file tree was explained by seven closed runs from 11-09 to 11-10
  (shared text buffer, undo, wait lifecycle, WAIT_RELEASE, process
  teardown, WAIT_BLOCK), each with a passing native boot. Edits from 11-11
  (a crate rename and browser-engine work) had no run at all. That told
  this session exactly which work was verified and which was not, in one
  query. D-016 framed the guard as scope enforcement and evidence for
  claims; handoff deserves to be named as a third use.
- **Failing checks are kept, not hidden.** 54 of 207 checks failed and are
  still in the record, including 16 deliberate reproduce-first runs and 13
  failed boots that were later fixed. That is the "never call an
  unexecuted check passed" rule working in its strongest form: the
  failures are evidence too.
- **Collision detection held up in practice.** The only collisions this
  session were true positives (files from the earlier WIP). No false
  positive was seen. The `shared` mechanism was used in 54 of 60 runs,
  almost always for `docs/ROADMAP.md`, the project's single registry.
- **Gap: there is no query command.** The statistics above came from an
  ad-hoc script. A `run_guard.py report --all` (label, finished, checks
  passed/failed, last native check) would make the handoff use cheap
  and would address part of G3.

## Native results for this session

Guard report for `20261112-051853-75a7dc` (closed with `--accept-blockers`,
reasons below):

| Criterion | Command | Exit | Seconds |
|---|---|---|---|
| host-row-shape-and-reclaim-keys | `cargo test -p mochios-sched -p mochios-wire-abi -p mochios-gate --lib` | 0 | 0.5 (cached; the same suites ran earlier: Gate 325, wire-abi 720, scheduler 195) |
| native-blocking-waits-close | `cargo xtask run --run-chello --timeout 240` | 0 | 254 |
| all-three-outcomes-recorded-natively | PowerShell `Select-String` one-liner | **1** | 0.2 (quoting defect D3, not behaviour) |
| plain-boot-regression | `cargo xtask run --timeout 120` | 0 | 65 |
| whitespace-integrity | `git diff --check` on the write set | 0 | 0.03 |
| native-blocking-waits-close-rerun | `cargo xtask run --run-chello --timeout 240` | 0 | 99 |
| all-three-outcomes-recorded-natively | `sh outcomes.sh` (same check as a script file) | 0 | 0.1 |

Serial evidence from the rerun: `##WAIT_BLOCK_CLOSED outcome=1 wait_id=84##`
(timer delivered), `outcome=2 wait_id=87` (released while parked → refused),
`CHELLO_EXIT exit_code=0`, then `outcome=3 wait_id=89` (sibling still parked
when its process exited → abandoned, closed by the next sweep). The
pre-existing WIP's own baseline boot (`cargo xtask run`, before any edit)
had also passed: desktop route, boot ok in 20.2 s.

The failed row stays in the record next to its passing retry. The guard
kept the evidence honest even though the failure was the operator's own
mistake.

`close` also reported a scope violation: "changed a pre-existing edit:
`docs/ROADMAP.md` (line 238 of the start state)". The new registry section
was inserted directly after an earlier session's uncommitted section, and
that section's text is byte-identical afterwards. See D4.

## Recommendations, in priority order

| # | Change | Kind | Cost |
|---|---|---|---|
| 1 | D1: `action="extend"` on `--adopt/--write-set/--shared`, plus a test | Defect fix (allowed under the freeze) | One line + test |
| 2 | G1: make the assurance screen hard to skip on builds (guard flag or warning) | Gap; overlaps FS-027 | Small, but it is a feature, so wait for FS-016 unless treated as a defect fix |
| 3 | D3: state the quoting rule for `--each` (or document argv in `--plan`) | Defect fix | Two lines |
| 4 | D4: content-based comparison for protected shared hunks | Defect fix | Small |
| 5 | D2: name the Windows launcher for manual script calls | Defect fix | One line |
| 6 | G2: a selection rule for open-ended "continue" | Doc fix | Two lines |
| 7 | `run_guard.py report --all` for handoff | Feature, so wait for FS-016 | Small |

## Limits

One session, one model, author-scored, no control arm. The task suited the
skill (a coupled change across ABI, Gate, scheduler and kernel, inside a
project that already enforces executed proof), so this says nothing about
small or greenfield work. The guard statistics cover many sessions but all
in one repository and with one operator. The skill's effect cannot be
separated from the project's own strong conventions; several behaviours
credited above (native-boot acceptance, no new doc files) were required
by the project anyway.

## Follow-up (same day)

| Item | Action | Evidence |
|---|---|---|
| D1 | `action="extend"` on `--write-set`, `--shared`, `--adopt` | `test_repeated_list_flags_accumulate` failed before, passes after |
| D3 | Report and console show argv with `shlex.join`; `--each` help and `implement.md` state the quoting rule | `test_report_shows_check_argv_with_quoting` failed before, passes after |
| D4 | A shared file's protected blocks are compared by content (contiguous, in order) before a positional hit is reported; whitespace-only blocks keep the positional check | `test_shared_claim_allows_insert_adjacent_to_outside_hunk` failed before, passes after; a 32-layout sweep went from 3 false positives to 0, with edits inside the outside section still caught 32/32 |
| D2 | No change: already fixed by FS-015 D6 (core names `python3`, `python`, or `py -3`; the hook tries all three) | `SKILL.md`, `guard_hook.sh` |
| G2 | Selection rule for open-ended "continue" added to `references/existing-projects.md` | Doc change; untested in a session |
| G1 | Recorded under FS-027 (frozen) | ROADMAP |
| G3 / `report --all` | Recorded as FS-028 (frozen) | ROADMAP |
