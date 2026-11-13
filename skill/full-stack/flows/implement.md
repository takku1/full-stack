# Implement flow

Load only when building was requested. Without a build request, stop at the
design. The fenced block is ordered instructions; the sections below define
each step.

```contract
inputs:
  request, criteria, design, subject
order:
  verify design has a complete assurance table before write implementation
  exec guard start before write implementation
  write implementation before exec acceptance checks
  exec acceptance checks before exec guard close
```

```logic
implement:
  require request exists
    otherwise:
      abort with "A request is required."

  unless criteria are known:
    generate criteria from request and prior conversation as criteria
    if criteria cannot be derived:
      ask user to state the acceptance criteria as criteria

  if request is ambiguous on outcome or authority:
    ask user to clarify the outcome or authority as clarification
    apply update with clarification as request

  unless design is known:
    run design from flows/design.md with:
      request = request

  apply recheck with design as design
  exec assurance table check from scripts as table_check
  verify design has a complete assurance table from table_check
    otherwise:
      apply assurance repair with design as design
      write design with design_docs
      exec assurance table check from scripts as table_check
      retry

  apply ready selection with design as selected
  read implementation guide from references/implementation.md as guide
  generate implementation from selected as implementation
  apply build method with guide as implementation
  apply acceptance criteria with criteria as implementation

  if subject is known:
    read contracts from subject as contracts
    apply fit with contracts as implementation

  apply write set with implementation as implementation
  exec guard start from scripts as started
  verify the run started with no collision from started
    otherwise:
      apply collision resolution with implementation as implementation
      apply write set with implementation as implementation
      exec guard start from scripts as started
      retry

  write implementation with subject
  apply check plan with criteria as implementation
  exec acceptance checks from scripts as results
  verify each acceptance criterion and assurance row passed or is a reported blocker from results
    otherwise:
      apply correction with implementation as implementation
      write implementation with subject
      exec acceptance checks from scripts as results
      retry

  if subject has a work tracker:
    apply registry update with implementation as entry
    write entry with registry
  exec guard close from scripts as closed
  verify the run closed with clean scope or reported blockers from closed
    otherwise:
      apply correction with implementation as implementation
      write implementation with subject
      exec acceptance checks from scripts as results
      exec guard close from scripts as closed
      retry
  generate completion report from closed as completion
  if subject uses Recurspec:
    apply node evidence proposal with implementation as completion

  return:
    design
    report = completion
```

## What is checked mechanically

`scripts/run_guard.py` (Python 3, git) enforces scope and evidence claims;
its log, not memory, is the record. With the plugin's hooks, a session that
invokes Full Stack cannot edit code until a guarded run is open. The `exec` steps
map to these commands (run them with `python3`, `python`, or `py -3`):

| Step | Command |
|---|---|
| `exec assurance table check` | `scripts/assurance.py check <design file>` |
| `exec guard start` | `scripts/run_guard.py start ...` (below) |
| `exec acceptance checks` | `scripts/run_guard.py checks ...` (below) |
| `exec guard close` | `scripts/run_guard.py close` (below) |

A guarded run takes three calls:

1. **write set + write claim**: `run_guard.py start --write-set <paths>
   --label <work ID> --assurance <design file>`, or `--routine "<why>"` for
   a routine edit with no assurance table. The hook blocks edits until one
   is declared (`declare` sets it later); declaring after files changed,
   or replacing a table with `--routine` (needs `--override`), is reported.
   Exit 3 is a collision. `--shared` claims files other workers also edit.
2. **check plan + write checks**: all acceptance checks, including every
   check in the design's assurance table, in one call,
   `run_guard.py checks --each "<criterion> :: <command>" --each ...`
   (or `--plan checks.json`). Name each assurance row's ID in its
   criterion (`"A-1 <claim> :: <command>"`). Rerun it after a correction. Each command is
   split like a POSIX shell and run without one, so quotes are removed:
   put pipes, redirects, and `powershell -Command` or `sh -c` one-liners in
   a script file, or give `--plan` an argv array. Repeat or list paths
   freely: `--adopt a b` and `--adopt a --adopt b` are the same.
3. **verify gate + run report + run close**: `run_guard.py close` prints
   the report to paste into the completion report and finishes the run only
   if scope is clean, every check passed, the assurance table is complete,
   and each row's latest check passed (tier 2 rows always need one).
   `finish` applies the same gates. The report marks criteria seen failing
   before passing; reproduce a failure first where you can. If not, fix the problem, or
   report it as a blocker and rerun with `--accept-blockers`.

The guard holds this flow's `order:` rules at runtime, not only on paper:
code edits wait until the declared assurance table passes `assurance.py
check`; a check run before any code edit is recorded as a reproduction, not
an acceptance check; and when SkillWren is installed, the guard writes a
SkillWren run ledger (`.git/full-stack-runs/ledger/`) committed to this
file's order rules, and `close` refuses a run whose ledger shows a step out
of order or a missing milestone.

Without the guard, check with `git status` and `git diff` and say the run
was unguarded. When taking over someone else's uncommitted work,
`run_guard.py report --all` shows which earlier runs closed with passing
checks.

When the design contains a stack block, rerun
`scripts/check_stack.py check` after any change to a layer choice; a
dependency added during implementation that is not in the accepted profile
is a scope change and goes back to the user.

## Step meanings

- **assurance repair**: run [assurance.md](assurance.md) on the design and
  fill the gaps `assurance.py check` reported; never edit the check's input
  to make it pass.
- **recheck**: confirm a supplied design's facts still hold; revise only
  stale parts; settled decisions stay settled.
- **ready selection**: build only ready work; report conditional and
  blocked work.
- **build method / fit**: apply the implementation reference or the
  subject's contracts.
- **acceptance criteria**: tie each criterion to a check.
- **collision resolution**: narrow the write set around outside edits, or
  mark the colliding work blocked until the other run finishes.
- **correction**: repair the failing edit; the same failure twice with the
  same evidence becomes a blocked criterion, not another repair.
- **registry update**: update this work's entry, else add one.
- **node evidence proposal**: list Recurspec node evidence updates as
  proposed, not applied.

Control words read as in [design.md](design.md). Parallel workers and
shared files follow the implementation reference. A port or binary held by
another process means wait; never kill it. Never deploy, publish, or install
tools beyond the task's authorization.
